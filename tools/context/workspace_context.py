#!/usr/bin/env python3
"""Provider-neutral Workspace Live Context reference implementation.

The tool never authenticates to Feishu and never stores provider identifiers in Git.
Approved Hosts use the generated publish/candidate plans with Document Capability,
then acknowledge the verified provider revision in Host-local state.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterator


SCHEMA_VERSION = "1.0"
MODES = {"OFF", "ON_DEMAND", "WATCH"}
AUTHORITIES = {"git", "feishu", "external-review"}
STATUSES = {"current", "stale", "conflict", "unavailable", "disabled"}
SECRET_PATTERNS = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
    "authorization": re.compile(r"\bAuthorization\s*:\s*(?:Bearer|Basic)\s+\S+", re.I),
    "credential-assignment": re.compile(
        r"\b(?:app[_-]?secret|client[_-]?secret|access[_-]?token|password|passwd)\s*[:=]\s*['\"]?[^\s'\"]{8,}",
        re.I,
    ),
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def emit(event: str, **fields: Any) -> None:
    print(json.dumps({"event": event, **fields}, ensure_ascii=False, sort_keys=True))


def run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=root, text=True, encoding="utf-8", errors="replace", capture_output=True, check=check
    )


def default_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_state_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(base) / "AI-Workspace" / "workspace-context"


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def atomic_json(path: Path, value: Any) -> None:
    atomic_write(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def scan_secrets(text: str) -> list[str]:
    return sorted(name for name, pattern in SECRET_PATTERNS.items() if pattern.search(text))


def safe_repo_path(root: Path, relative: str) -> Path:
    if not relative or Path(relative).is_absolute():
        raise ValueError(f"repository path must be relative: {relative!r}")
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"repository path escapes root: {relative}") from exc
    return resolved


def load_manifest(root: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict):
        raise ValueError("Live Context manifest must be a JSON object")
    errors: list[str] = []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    contexts = manifest.get("contexts")
    if not isinstance(contexts, list) or not contexts:
        errors.append("contexts must be a non-empty array")
        contexts = []
    ids: set[str] = set()
    for index, item in enumerate(contexts):
        if not isinstance(item, dict):
            errors.append(f"contexts[{index}] must be an object")
            continue
        context_id = str(item.get("context_id", ""))
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,63}", context_id):
            errors.append(f"invalid context_id: {context_id!r}")
        if context_id in ids:
            errors.append(f"duplicate context_id: {context_id}")
        ids.add(context_id)
        if item.get("authority") not in AUTHORITIES:
            errors.append(f"{context_id}: invalid authority")
        if item.get("scope") not in {"public", "project-private", "local-only"}:
            errors.append(f"{context_id}: invalid scope")
        if item.get("sensitivity") not in {"public", "internal", "confidential", "local-only"}:
            errors.append(f"{context_id}: invalid sensitivity")
        source = item.get("git_path")
        if source:
            try:
                path = safe_repo_path(root, str(source))
                if item.get("enabled", True) and not path.is_file():
                    errors.append(f"{context_id}: missing git_path {source}")
            except ValueError as exc:
                errors.append(f"{context_id}: {exc}")
        if item.get("include_in_pack") and (item.get("scope") != "public" or item.get("sensitivity") != "public"):
            errors.append(f"{context_id}: local pack may contain only public/public content")
    if errors:
        raise ValueError("; ".join(errors))
    return manifest


def generated_current_state(root: Path) -> str:
    head = run_git(root, "rev-parse", "HEAD").stdout.strip()
    branch = run_git(root, "branch", "--show-current").stdout.strip()
    commit_time = run_git(root, "show", "-s", "--format=%cI", "HEAD").stdout.strip()
    rows: list[tuple[str, str, str]] = []
    for path in sorted((root / "tasks").glob("TASK-*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()[:24]
        title = lines[0].removeprefix("# ").strip() if lines else path.stem
        status = next((line.split(":", 1)[1].strip() for line in lines if line.startswith("- Status:")), "Unknown")
        rows.append((path.name, title, status))
    lines = [
        "# Workspace Current State",
        "",
        f"- Base commit time: {commit_time}",
        f"- Git branch: `{branch}`",
        f"- Git commit: `{head}`",
        "- Authority: Git Task / Status / Review / Handoff",
        "",
        "## Task Registry View",
        "",
        "| File | Title | Status |",
        "| --- | --- | --- |",
    ]
    lines.extend(f"| `{name}` | {title.replace('|', '/')} | {status.replace('|', '/')} |" for name, title, status in rows)
    lines.extend(
        [
            "",
            "## Handoff Entry Points",
            "",
            "- `handoff/CHATGPT.md`",
            "- `handoff/CODEX.md`",
            "",
            "This generated view is a local interaction-time snapshot. Re-run Workspace Sync before relying on it.",
            "",
        ]
    )
    return "\n".join(lines)


def context_content(root: Path, context: dict[str, Any]) -> str | None:
    if not context.get("enabled", True):
        return None
    if context.get("generator") == "git-current-state":
        return generated_current_state(root)
    git_path = context.get("git_path")
    if not git_path:
        return None
    return safe_repo_path(root, str(git_path)).read_text(encoding="utf-8")


def context_fingerprint(root: Path, context: dict[str, Any]) -> str | None:
    content = context_content(root, context)
    return sha256_text(content) if content is not None else None


def load_snapshot(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None or not path.exists():
        return {}
    data = read_json(path)
    items = data.get("contexts") if isinstance(data, dict) else None
    if not isinstance(items, list):
        raise ValueError("provider snapshot must contain a contexts array")
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or not item.get("context_id"):
            raise ValueError("provider snapshot entry requires context_id")
        context_id = str(item["context_id"])
        if context_id in result:
            raise ValueError(f"duplicate provider snapshot context_id: {context_id}")
        content = item.get("content")
        fingerprint = item.get("content_sha256")
        if content is not None:
            computed = sha256_text(str(content))
            if fingerprint and fingerprint != computed:
                raise ValueError(f"provider snapshot fingerprint mismatch: {context_id}")
            fingerprint = computed
        result[context_id] = {
            "revision": str(item.get("revision", "")),
            "content_sha256": str(fingerprint or ""),
            **({"content": str(content)} if content is not None else {}),
            **({"provider_ref": str(item["provider_ref"])} if item.get("provider_ref") else {}),
        }
    return result


def default_state() -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "mode": "ON_DEMAND", "updated_at": utc_now(), "contexts": {}}


def load_state(state_dir: Path) -> dict[str, Any]:
    state = read_json(state_dir / "state.json", default_state())
    if not isinstance(state, dict) or state.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Host-local state schema is invalid")
    if state.get("mode") not in MODES:
        raise ValueError("Host-local mode is invalid")
    if not isinstance(state.get("contexts"), dict):
        raise ValueError("Host-local context state is invalid")
    return state


class FileLock:
    def __init__(self, state_dir: Path, timeout_seconds: float = 5.0, stale_seconds: float = 300.0):
        self.path = state_dir / "workspace-context.lock"
        self.timeout_seconds = timeout_seconds
        self.stale_seconds = stale_seconds

    def __enter__(self) -> "FileLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + self.timeout_seconds
        while True:
            try:
                descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                os.write(descriptor, json.dumps({"pid": os.getpid(), "created_at": utc_now()}).encode("utf-8"))
                os.close(descriptor)
                return self
            except FileExistsError:
                try:
                    age = time.time() - self.path.stat().st_mtime
                    if age > self.stale_seconds:
                        self.path.unlink()
                        continue
                except FileNotFoundError:
                    continue
                if time.monotonic() >= deadline:
                    raise TimeoutError("another Workspace Sync writer holds the lock")
                time.sleep(0.05)

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        with contextlib.suppress(FileNotFoundError):
            self.path.unlink()


def transaction_write(state_dir: Path, writes: list[tuple[Path, str]], fault_stage: str | None = None) -> None:
    snapshots = {path: path.read_bytes() if path.exists() else None for path, _ in writes}
    allow_fault = (state_dir / ".allow-fault-injection").exists()
    try:
        for index, (path, text) in enumerate(writes):
            atomic_write(path, text)
            if allow_fault and fault_stage == f"after-write-{index + 1}":
                raise RuntimeError(f"test fault: {fault_stage}")
    except Exception:
        for path, previous in snapshots.items():
            if previous is None:
                with contextlib.suppress(FileNotFoundError):
                    path.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(previous)
        raise


def compare_status(
    root: Path, manifest: dict[str, Any], state: dict[str, Any], snapshot: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    baselines = state.get("contexts", {})
    for context in manifest["contexts"]:
        context_id = context["context_id"]
        if not context.get("enabled", True):
            results.append({"context_id": context_id, "status": "disabled", "reason": context.get("status", "disabled")})
            continue
        git_fp = context_fingerprint(root, context)
        provider = snapshot.get(context_id)
        provider_fp = provider.get("content_sha256") if provider else None
        baseline = baselines.get(context_id, {})
        base_git = baseline.get("git_fingerprint")
        base_provider = baseline.get("provider_fingerprint")
        git_changed = bool(base_git and git_fp and base_git != git_fp)
        provider_changed = bool(base_provider and provider_fp and base_provider != provider_fp)
        authority = context["authority"]
        status = "current"
        reason = "fingerprints match acknowledged baseline"
        if authority == "external-review":
            status, reason = ("current", "external reviewed document is registered") if provider else ("unavailable", "provider snapshot missing")
        elif not baseline:
            if authority == "git":
                if provider_fp and provider_fp == git_fp:
                    status, reason = "current", "provider matches Git source"
                else:
                    status, reason = "stale", "initial Git publication is required"
            else:
                status, reason = ("stale", "provider draft requires Candidate capture") if provider else ("unavailable", "provider snapshot missing")
        elif git_changed and provider_changed:
            status, reason = "conflict", "Git and provider both changed since baseline"
        elif authority == "git":
            if provider_changed:
                status, reason = "conflict", "provider changed a Git-authoritative object"
            elif git_changed or not provider:
                status, reason = "stale", "provider needs Git publication"
        elif authority == "feishu":
            if provider_changed:
                status, reason = "stale", "provider draft requires Candidate capture"
            elif not provider:
                status, reason = "unavailable", "provider snapshot missing"
        if status not in STATUSES:
            raise AssertionError(status)
        results.append(
            {
                "context_id": context_id,
                "authority": authority,
                "status": status,
                "reason": reason,
                "git_fingerprint": git_fp,
                "provider_fingerprint": provider_fp,
                "provider_revision": provider.get("revision", "") if provider else "",
            }
        )
    return results


def style_issues(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    prose = [line.strip() for line in lines if line.strip() and not re.match(r"^(#|[-*+] |\d+\. |\||```|>|<)", line.strip())]
    issues: list[str] = []
    streak = 0
    for line in prose:
        isolated = len(line) <= 12 and not re.search(r"[。！？；：,.!?;:]$", line)
        streak = streak + 1 if isolated else 0
        if streak >= 4:
            issues.append("four or more isolated short prose lines")
            break
    headings = sum(1 for line in lines if line.startswith("#"))
    nonempty = sum(1 for line in lines if line.strip())
    if nonempty >= 20 and headings / nonempty > 0.35:
        issues.append("heading density exceeds 35%")
    return issues


def doctor(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    checks: dict[str, Any] = {"manifest": "ok", "git": {}, "sources": [], "style": []}
    probe = run_git(root, "rev-parse", "--show-toplevel")
    if Path(probe.stdout.strip()).resolve() != root.resolve():
        raise ValueError("root is not the Git repository root")
    head = run_git(root, "rev-parse", "HEAD").stdout.strip()
    branch = run_git(root, "branch", "--show-current").stdout.strip()
    checks["git"] = {"head": head, "branch": branch, "origin_main_ancestor": None}
    origin = run_git(root, "rev-parse", "--verify", "origin/main", check=False)
    if origin.returncode == 0:
        ancestor = run_git(root, "merge-base", "--is-ancestor", origin.stdout.strip(), head, check=False)
        checks["git"]["origin_main_ancestor"] = ancestor.returncode == 0
    for context in manifest["contexts"]:
        content = context_content(root, context)
        if content is None:
            continue
        categories = scan_secrets(content)
        if categories:
            raise ValueError(f"{context['context_id']}: secret scan failed: {categories}")
        checks["sources"].append({"context_id": context["context_id"], "sha256": sha256_text(content), "bytes": len(content.encode("utf-8"))})
        if context.get("style_check") and context.get("git_path"):
            issues = style_issues(safe_repo_path(root, context["git_path"]))
            checks["style"].append({"context_id": context["context_id"], "issues": issues})
            if issues:
                raise ValueError(f"{context['context_id']}: style check failed: {issues}")
    return checks


def build_local_pack(root: Path, manifest: dict[str, Any], statuses: list[dict[str, Any]], state_dir: Path) -> Path:
    by_id = {item["context_id"]: item for item in statuses}
    head = run_git(root, "rev-parse", "HEAD").stdout.strip()
    lines = [
        "# Workspace Local Context Pack",
        "",
        f"- Generated: {utc_now()}",
        f"- Git commit: `{head}`",
        "- Authority: Git and the Live Context manifest",
        "- Freshness: re-run `workspace sync` before Task, Review, or status work",
        "",
    ]
    for context in manifest["contexts"]:
        if not context.get("include_in_pack") or not context.get("enabled", True):
            continue
        content = context_content(root, context)
        if content is None:
            continue
        status = by_id[context["context_id"]]["status"]
        lines.extend([f"## {context['title']}", "", f"Context status: `{status}`", "", content.strip(), ""])
    path = state_dir / "LOCAL_CONTEXT_PACK.md"
    atomic_write(path, "\n".join(lines).rstrip() + "\n")
    return path


def build_publish_plan(root: Path, manifest: dict[str, Any], statuses: list[dict[str, Any]], state_dir: Path) -> Path:
    publishable = {item["context_id"] for item in statuses if item["status"] in {"stale", "conflict"}}
    entries = []
    for context in manifest["contexts"]:
        if context["authority"] != "git" or context["context_id"] not in publishable or not context.get("enabled", True):
            continue
        content = context_content(root, context)
        if content is None:
            continue
        entries.append(
            {
                "context_id": context["context_id"],
                "title": context["title"],
                "provider_alias": context["provider_alias"],
                "folder_alias": manifest["provider_binding"]["folder_alias"],
                "sharing": context.get("sharing", "company_readable"),
                "content_sha256": sha256_text(content),
                "markdown": content,
            }
        )
    plan = {"schema_version": SCHEMA_VERSION, "generated_at": utc_now(), "operation": "CONTEXT_PUBLISH", "contexts": entries}
    path = state_dir / "publish-plan.json"
    atomic_json(path, plan)
    return path


def sanitized_statuses(statuses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: value for key, value in item.items() if key not in {"git_fingerprint", "provider_fingerprint", "provider_revision"}} for item in statuses]


def cmd_doctor(args: argparse.Namespace) -> int:
    root, state_dir = Path(args.root).resolve(), Path(args.state_dir).resolve()
    manifest = load_manifest(root, Path(args.manifest).resolve())
    checks = doctor(root, manifest)
    state = load_state(state_dir)
    emit("doctor", ok=True, mode=state["mode"], checks=checks)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root, state_dir = Path(args.root).resolve(), Path(args.state_dir).resolve()
    manifest = load_manifest(root, Path(args.manifest).resolve())
    state = load_state(state_dir)
    snapshot = load_snapshot(Path(args.provider_snapshot).resolve() if args.provider_snapshot else None)
    statuses = compare_status(root, manifest, state, snapshot)
    emit("status", mode=state["mode"], counts={name: sum(i["status"] == name for i in statuses) for name in sorted(STATUSES)}, contexts=sanitized_statuses(statuses))
    return 2 if any(item["status"] == "conflict" for item in statuses) else 0


def cmd_sync(args: argparse.Namespace) -> int:
    root, state_dir = Path(args.root).resolve(), Path(args.state_dir).resolve()
    manifest = load_manifest(root, Path(args.manifest).resolve())
    with FileLock(state_dir, timeout_seconds=args.lock_timeout):
        checks = doctor(root, manifest)
        state = load_state(state_dir)
        snapshot = load_snapshot(Path(args.provider_snapshot).resolve() if args.provider_snapshot else None)
        statuses = compare_status(root, manifest, state, snapshot)
        pack = build_local_pack(root, manifest, statuses, state_dir)
        plan = build_publish_plan(root, manifest, statuses, state_dir)
        summary = {
            "schema_version": SCHEMA_VERSION,
            "generated_at": utc_now(),
            "mode": state["mode"],
            "git_head": checks["git"]["head"],
            "provider_available": bool(snapshot),
            "contexts": sanitized_statuses(statuses),
        }
        transaction_write(
            state_dir,
            [(state_dir / "last-sync.json", json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")],
            os.environ.get("WORKSPACE_CONTEXT_TEST_FAULT"),
        )
    emit(
        "sync",
        mode=state["mode"],
        local_pack=str(pack),
        publish_plan=str(plan),
        provider_available=bool(snapshot),
        conflicts=sum(item["status"] == "conflict" for item in statuses),
        stale=sum(item["status"] == "stale" for item in statuses),
    )
    return 2 if any(item["status"] == "conflict" for item in statuses) else 0


def cmd_publish(args: argparse.Namespace) -> int:
    root, state_dir = Path(args.root).resolve(), Path(args.state_dir).resolve()
    manifest = load_manifest(root, Path(args.manifest).resolve())
    state = load_state(state_dir)
    snapshot = load_snapshot(Path(args.provider_snapshot).resolve() if args.provider_snapshot else None)
    statuses = compare_status(root, manifest, state, snapshot)
    with FileLock(state_dir, timeout_seconds=args.lock_timeout):
        plan = build_publish_plan(root, manifest, statuses, state_dir)
    entries = read_json(plan, {}).get("contexts", [])
    emit("publish-plan", plan=str(plan), changed=len(entries), mode=state["mode"], next_action="Approved Host applies this plan with Document Capability, then runs acknowledge.")
    return 0


def cmd_acknowledge(args: argparse.Namespace) -> int:
    root, state_dir = Path(args.root).resolve(), Path(args.state_dir).resolve()
    manifest = load_manifest(root, Path(args.manifest).resolve())
    context = next((item for item in manifest["contexts"] if item["context_id"] == args.context_id), None)
    if context is None:
        raise ValueError("unknown context_id")
    git_fp = context_fingerprint(root, context)
    with FileLock(state_dir, timeout_seconds=args.lock_timeout):
        state = load_state(state_dir)
        state["contexts"][args.context_id] = {
            "git_fingerprint": git_fp,
            "provider_fingerprint": args.provider_fingerprint,
            "provider_revision": args.provider_revision,
            **({"provider_ref": args.provider_ref} if args.provider_ref else {}),
            "acknowledged_at": utc_now(),
        }
        state["updated_at"] = utc_now()
        atomic_json(state_dir / "state.json", state)
    emit("acknowledged", context_id=args.context_id, provider_ref="stored-locally" if args.provider_ref else "not-recorded")
    return 0


def yaml_scalar(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def cmd_capture_draft(args: argparse.Namespace) -> int:
    root, state_dir = Path(args.root).resolve(), Path(args.state_dir).resolve()
    manifest = load_manifest(root, Path(args.manifest).resolve())
    context = next((item for item in manifest["contexts"] if item["context_id"] == args.context_id), None)
    if context is None or context["authority"] != "feishu":
        raise ValueError("capture-draft requires a Feishu-authoritative context")
    snapshot = load_snapshot(Path(args.provider_snapshot).resolve())
    provider = snapshot.get(args.context_id)
    if not provider or "content" not in provider:
        raise ValueError("provider snapshot must include draft content")
    content = provider["content"].strip()
    categories = scan_secrets(content)
    if categories:
        emit("capture-draft", status="local-only", secret_categories=categories, captured=0)
        return 0
    summary = content[:2000]
    event = {
        "schema_version": "1.0",
        "title": f"{context['title']} provider draft",
        "type": "decision",
        "scope": context["scope"],
        "sensitivity": context["sensitivity"],
        "source_host": args.source_host,
        "source_project": "AI-Workspace",
        "source_actor_alias": args.source_actor_alias,
        "source_reference": f"{args.context_id}@revision:{provider.get('revision') or 'unversioned'}",
        "related_task": "TASK-0021",
        "durability_score": 4,
        "reuse_score": 4,
        "evidence_score": 3,
        "confidence": 0.8,
        "summary": summary,
        "canonical_destination": "",
        "evidence": ["Provider snapshot fingerprint verified by Workspace Sync"],
        "constraints": ["Candidate only; do not overwrite Git canonical content without Review"],
    }
    event_path = state_dir / "pending-events" / f"{args.context_id}.yaml"
    atomic_write(event_path, "\n".join(f"{key}: {yaml_scalar(value)}" for key, value in event.items()) + "\n")
    if not args.memory_cli:
        emit("capture-draft", status="candidate-plan", event_path=str(event_path), captured=0)
        return 0
    command = [
        sys.executable,
        str(Path(args.memory_cli).resolve()),
        "--root",
        str(Path(args.memory_root or root).resolve()),
        "--state-dir",
        str(Path(args.memory_state_dir or (state_dir / "memory-state")).resolve()),
        "capture",
        "--event",
        str(event_path),
    ]
    result = subprocess.run(command, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=args.timeout)
    if result.returncode != 0:
        emit("capture-draft", status="failed", captured=0, error="Memory Candidate capture failed")
        return result.returncode
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    emit("capture-draft", status=payload.get("status", "unknown"), captured=payload.get("captured", 0), candidate=payload.get("path", ""))
    return 0


def cmd_resolve_conflict(args: argparse.Namespace) -> int:
    root, state_dir = Path(args.root).resolve(), Path(args.state_dir).resolve()
    manifest = load_manifest(root, Path(args.manifest).resolve())
    snapshot_path = Path(args.provider_snapshot).resolve()
    snapshot = load_snapshot(snapshot_path)
    state = load_state(state_dir)
    statuses = compare_status(root, manifest, state, snapshot)
    item = next((entry for entry in statuses if entry["context_id"] == args.context_id), None)
    if item is None or item["status"] != "conflict":
        raise ValueError("context is not in conflict")
    record = {
        "context_id": args.context_id,
        "decision": args.decision,
        "decision_reference": args.decision_reference,
        "recorded_at": utc_now(),
        "automatic_overwrite": False,
    }
    with FileLock(state_dir, timeout_seconds=args.lock_timeout):
        path = state_dir / "conflict-resolutions" / f"{args.context_id}-{int(time.time())}.json"
        atomic_json(path, record)
    emit("conflict-resolution", context_id=args.context_id, decision=args.decision, record=str(path), next_action="publish Git" if args.decision == "keep-git" else "capture provider Candidate")
    return 0


def cmd_set_mode(args: argparse.Namespace) -> int:
    state_dir = Path(args.state_dir).resolve()
    mode = args.mode.upper()
    if mode == "WATCH" and not args.user_approved:
        raise ValueError("WATCH requires explicit --user-approved")
    with FileLock(state_dir, timeout_seconds=args.lock_timeout):
        state = load_state(state_dir)
        state["mode"] = mode
        state["updated_at"] = utc_now()
        atomic_json(state_dir / "state.json", state)
    emit("mode-set", mode=mode)
    return 0


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--provider-snapshot")
    parser.add_argument("--lock-timeout", type=float, default=5.0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI-Workspace Live Context tooling")
    parser.add_argument("--root", default=str(default_root()))
    parser.add_argument("--state-dir", default=str(default_state_dir()))
    parser.add_argument("--manifest", default=str(default_root() / "LIVE_CONTEXT_MANIFEST.json"))
    sub = parser.add_subparsers(dest="command", required=True)
    doctor_parser = sub.add_parser("doctor")
    doctor_parser.set_defaults(func=cmd_doctor)
    status_parser = sub.add_parser("status")
    add_common(status_parser)
    status_parser.set_defaults(func=cmd_status)
    sync_parser = sub.add_parser("sync")
    add_common(sync_parser)
    sync_parser.set_defaults(func=cmd_sync)
    publish_parser = sub.add_parser("publish")
    add_common(publish_parser)
    publish_parser.set_defaults(func=cmd_publish)
    acknowledge = sub.add_parser("acknowledge")
    acknowledge.add_argument("context_id")
    acknowledge.add_argument("--provider-revision", required=True)
    acknowledge.add_argument("--provider-fingerprint", required=True)
    acknowledge.add_argument("--provider-ref")
    acknowledge.add_argument("--lock-timeout", type=float, default=5.0)
    acknowledge.set_defaults(func=cmd_acknowledge)
    capture = sub.add_parser("capture-draft")
    capture.add_argument("context_id")
    capture.add_argument("--provider-snapshot", required=True)
    capture.add_argument("--source-host", required=True)
    capture.add_argument("--source-actor-alias", required=True)
    capture.add_argument("--memory-cli")
    capture.add_argument("--memory-root")
    capture.add_argument("--memory-state-dir")
    capture.add_argument("--timeout", type=float, default=20.0)
    capture.set_defaults(func=cmd_capture_draft)
    resolve = sub.add_parser("resolve-conflict")
    resolve.add_argument("context_id")
    resolve.add_argument("--provider-snapshot", required=True)
    resolve.add_argument("--decision", choices=["keep-git", "keep-provider"], required=True)
    resolve.add_argument("--decision-reference", required=True)
    resolve.add_argument("--lock-timeout", type=float, default=5.0)
    resolve.set_defaults(func=cmd_resolve_conflict)
    mode = sub.add_parser("set-mode")
    mode.add_argument("mode", choices=sorted(MODES))
    mode.add_argument("--user-approved", action="store_true")
    mode.add_argument("--lock-timeout", type=float, default=5.0)
    mode.set_defaults(func=cmd_set_mode)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        emit("failed", reason="interrupted")
        return 130
    except Exception as exc:
        emit("failed", reason=str(exc), error_type=type(exc).__name__)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
