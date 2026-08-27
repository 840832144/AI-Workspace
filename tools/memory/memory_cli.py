#!/usr/bin/env python3
"""Deterministic Git-backed memory curation reference implementation.

The core intentionally uses only the Python standard library. Models may propose
events, but this module owns schema, routing, secret, dedup and promotion gates.
"""

from __future__ import annotations

import argparse
import copy
import contextlib
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Iterable


SCHEMA_VERSION = "1.0"
MODES = {"OFF", "ASSISTED", "AUTO"}
SCOPES = {"public", "project-private", "cross-project-private", "local-only", "unknown"}
SENSITIVITIES = {"public", "internal", "confidential", "secret", "unknown"}
TYPES = {
    "decision", "rule", "fact", "solution", "skill", "workflow", "status",
    "handoff", "review", "failure", "manifest", "context-pack", "lesson",
}
REQUIRED_FIELDS = {
    "schema_version", "memory_id", "title", "type", "scope", "sensitivity",
    "status", "source_host", "source_project", "source_actor_alias",
    "source_reference", "created_at", "durability_score", "reuse_score",
    "evidence_score", "confidence", "normalized_key", "content_fingerprint",
    "evidence", "constraints", "supersedes", "canonical_destination",
}
ALLOWED_DESTINATION_ROOTS = {
    "solutions", "memory", "handoff", "tasks", "projects", "skills",
    "workflows", "bootstrap",
}
PROVENANCE_FIELDS = ("source_host", "source_project", "source_actor_alias", "source_reference")
PROVENANCE_PLACEHOLDERS = {
    "", "unknown", "n a", "na", "none", "null", "not applicable", "tbd", "unspecified",
}
PRIVATE_CLASSIFICATION_BY_SCOPE = {
    "project-private": "project-private",
    "cross-project-private": "cross-project-private-hub",
}
SECRET_PATTERNS = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
    "authorization-header": re.compile(r"Authorization\s*:\s*(?:Bearer|Basic)\s+[A-Za-z0-9._~+/=-]{8,}", re.I),
    "openai-key": re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    "github-token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{16,}\b", re.I),
    "assigned-secret": re.compile(
        r"\b(?:api[_-]?key|secret|token|password|credential)\b\s*[:=]\s*[\"']?[A-Za-z0-9._~+/=-]{12,}",
        re.I,
    ),
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def emit(status: str, **payload: Any) -> None:
    print(json.dumps({"status": status, **payload}, ensure_ascii=False, sort_keys=True))


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        with contextlib.suppress(OSError):
            os.unlink(temp_name)
        raise


def atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        with contextlib.suppress(OSError):
            os.unlink(temp_name)
        raise


def default_state_dir() -> Path:
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "AI-Workspace" / "memory"
    base = os.environ.get("XDG_STATE_HOME")
    return Path(base) / "ai-workspace" / "memory" if base else Path.home() / ".local" / "state" / "ai-workspace" / "memory"


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def normalize_text(value: str) -> str:
    return " ".join(re.findall(r"[\w\-]+", value.lower(), flags=re.UNICODE))


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return (slug or "memory")[:64]


def yaml_value(value: Any) -> str:
    if isinstance(value, (list, dict, str)):
        return json.dumps(value, ensure_ascii=False, sort_keys=isinstance(value, dict))
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    return str(value)


def parse_yaml_value(raw: str) -> Any:
    raw = raw.strip()
    if not raw:
        return ""
    if raw[0:1] in {'"', "'", "[", "{"} or raw in {"true", "false", "null"}:
        if raw.startswith("'") and raw.endswith("'"):
            return raw[1:-1].replace("''", "'")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if re.fullmatch(r"-?\d+\.\d+", raw):
        return float(raw)
    return raw


def parse_flat_yaml(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1].isspace() or ":" not in line:
            raise ValueError(f"unsupported YAML at line {number}; use flat key/value fields")
        key, raw = line.split(":", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", key):
            raise ValueError(f"invalid YAML key at line {number}")
        data[key] = parse_yaml_value(raw)
    return data


def split_candidate(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("candidate must start with YAML frontmatter")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError("candidate frontmatter is not closed") from exc
    return parse_flat_yaml("\n".join(lines[1:end])), "\n".join(lines[end + 1:]).strip() + "\n"


def render_candidate(meta: dict[str, Any], summary: str) -> str:
    ordered = [
        "schema_version", "memory_id", "title", "type", "scope", "sensitivity",
        "status", "source_host", "source_project", "source_actor_alias",
        "source_reference", "related_task", "related_commit", "created_at", "repository_alias",
        "durability_score", "reuse_score", "evidence_score", "confidence",
        "normalized_key", "content_fingerprint", "canonical_destination",
        "evidence", "constraints", "supersedes", "curated_at", "review_reason",
    ]
    lines = ["---"]
    for key in ordered:
        if key in meta:
            lines.append(f"{key}: {yaml_value(meta[key])}")
    for key in sorted(set(meta) - set(ordered)):
        lines.append(f"{key}: {yaml_value(meta[key])}")
    lines.extend(["---", "", "## Summary", "", summary.strip(), "", "## Evidence", ""])
    evidence = meta.get("evidence") or []
    lines.extend([f"- {item}" for item in evidence] or ["- None recorded"])
    lines.extend(["", "## Constraints", ""])
    constraints = meta.get("constraints") or []
    lines.extend([f"- {item}" for item in constraints] or ["- None recorded"])
    return "\n".join(lines).rstrip() + "\n"


def extract_section(body: str, heading: str) -> str:
    pattern = re.compile(rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)", re.M | re.S)
    match = pattern.search(body)
    return match.group(1).strip() if match else ""


def scan_secrets(text: str) -> list[str]:
    return sorted(name for name, pattern in SECRET_PATTERNS.items() if pattern.search(text))


def redact_secrets(text: str) -> str:
    for name, pattern in SECRET_PATTERNS.items():
        text = pattern.sub(f"[REDACTED:{name}]", text)
    return text


def record_text(data: dict[str, Any], body: str = "") -> str:
    safe = {key: value for key, value in data.items() if key not in {"content_fingerprint"}}
    return json.dumps(safe, ensure_ascii=False, sort_keys=True) + "\n" + body


def normalized_key(data: dict[str, Any]) -> str:
    return f"{data['scope']}:{data['type']}:{normalize_text(str(data['title']))}"


def candidate_fingerprint(data: dict[str, Any], summary: str) -> str:
    evidence = [normalize_text(str(item)) for item in data.get("evidence", [])]
    payload = {
        "normalized_key": data.get("normalized_key") or normalized_key(data),
        "summary": normalize_text(summary),
        "evidence": sorted(evidence),
        "source_reference": normalize_text(str(data.get("source_reference", ""))),
    }
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def provenance_errors(meta: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in PROVENANCE_FIELDS:
        value = str(meta.get(key, "")).strip()
        if normalize_text(value) in PROVENANCE_PLACEHOLDERS:
            errors.append(f"{key} must be stable provenance, not a placeholder")
    return errors


class FileLock:
    def __init__(self, root: Path, state_dir: Path, timeout: float = 10.0) -> None:
        digest = hashlib.sha256(str(root.resolve()).lower().encode()).hexdigest()[:16]
        self.path = state_dir / "locks" / f"{digest}.lock"
        self.timeout = timeout
        self.fd: int | None = None

    def __enter__(self) -> "FileLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + self.timeout
        while True:
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self.fd, json.dumps({"pid": os.getpid(), "created_at": utc_now()}).encode())
                return self
            except FileExistsError:
                try:
                    if time.time() - self.path.stat().st_mtime > 300:
                        self.path.unlink()
                        continue
                except FileNotFoundError:
                    continue
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"memory lock busy: {self.path}")
                time.sleep(0.05)

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        if self.fd is not None:
            os.close(self.fd)
        with contextlib.suppress(FileNotFoundError):
            self.path.unlink()


def mode_paths(root: Path, state_dir: Path) -> tuple[Path, Path]:
    return state_dir / "mode.json", root / "memory" / "index" / "default-mode.json"


def get_mode(root: Path, state_dir: Path) -> tuple[str, str]:
    local, default = mode_paths(root, state_dir)
    if local.exists():
        data = json.loads(local.read_text(encoding="utf-8"))
        mode = str(data.get("mode", "")).upper()
        if mode in MODES:
            return mode, "host-local"
    if default.exists():
        data = json.loads(default.read_text(encoding="utf-8"))
        mode = str(data.get("default_mode", "ASSISTED")).upper()
        if mode in MODES:
            return mode, "repository-default"
    return "ASSISTED", "built-in-default"


def set_mode(root: Path, state_dir: Path, mode: str) -> Path:
    mode = mode.upper()
    if mode not in MODES:
        raise ValueError(f"invalid mode: {mode}")
    path, _ = mode_paths(root, state_dir)
    atomic_write_text(path, json.dumps({"schema_version": SCHEMA_VERSION, "mode": mode, "updated_at": utc_now()}, indent=2) + "\n")
    return path


def outbox_path(state_dir: Path, kind: str, event_id: str) -> Path:
    return state_dir / "outbox" / kind / f"{event_id}.json"


def write_outbox(state_dir: Path, kind: str, data: dict[str, Any], reason: str, secret_categories: list[str] | None = None) -> Path:
    event_id = str(data.get("memory_id") or f"OUT-{dt.datetime.now():%Y%m%d}-{os.urandom(6).hex().upper()}")
    safe = {
        "schema_version": SCHEMA_VERSION,
        "outbox_id": event_id,
        "status": kind,
        "reason": reason,
        "created_at": utc_now(),
        "title": redact_secrets(str(data.get("title", ""))),
        "type": data.get("type", "unknown"),
        "scope": data.get("scope", "unknown"),
        "sensitivity": data.get("sensitivity", "unknown"),
        "source_host": data.get("source_host", "unknown"),
        "source_project": data.get("source_project", "unknown"),
        "source_actor_alias": data.get("source_actor_alias", "unknown"),
        "source_reference": redact_secrets(str(data.get("source_reference", "")))[:500],
        "summary": redact_secrets(str(data.get("summary", "")))[:4000],
        "secret_categories": secret_categories or [],
        "target_hint": data.get("canonical_destination", ""),
    }
    path = outbox_path(state_dir, kind, event_id)
    atomic_write_text(path, json.dumps(safe, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return path


def validate_destination(value: str) -> str | None:
    if not value:
        return None
    if "\\" in value or re.match(r"^[A-Za-z]:", value):
        return "canonical_destination must use a repository-relative POSIX path"
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        return "canonical_destination escapes the repository"
    if path.parts[0] not in ALLOWED_DESTINATION_ROOTS:
        return f"canonical_destination root is not allowed: {path.parts[0]}"
    return None


def validate_meta(meta: dict[str, Any], body: str, require_git_provenance: bool = True) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_FIELDS - set(meta))
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    if meta.get("schema_version") != SCHEMA_VERSION:
        errors.append("unsupported schema_version")
    if not re.fullmatch(r"MEM-\d{8}-[A-F0-9]{12}", str(meta.get("memory_id", ""))):
        errors.append("invalid memory_id")
    if meta.get("type") not in TYPES:
        errors.append("invalid type")
    if meta.get("scope") not in SCOPES:
        errors.append("invalid scope")
    if meta.get("sensitivity") not in SENSITIVITIES:
        errors.append("invalid sensitivity")
    if meta.get("scope") == "public" and meta.get("sensitivity") != "public":
        errors.append("public scope requires public sensitivity")
    for key in ("durability_score", "reuse_score", "evidence_score"):
        try:
            if not 0 <= int(meta.get(key, -1)) <= 5:
                errors.append(f"{key} must be 0..5")
        except (TypeError, ValueError):
            errors.append(f"{key} must be an integer")
    try:
        if not 0 <= float(meta.get("confidence", -1)) <= 1:
            errors.append("confidence must be 0..1")
    except (TypeError, ValueError):
        errors.append("confidence must be numeric")
    for key in ("evidence", "constraints", "supersedes"):
        if not isinstance(meta.get(key), list):
            errors.append(f"{key} must be a list")
    for key in ("title", "source_host", "source_project", "source_actor_alias", "source_reference"):
        if not str(meta.get(key, "")).strip():
            errors.append(f"{key} must not be empty")
    if require_git_provenance:
        errors.extend(provenance_errors(meta))
    if len(str(meta.get("source_reference", ""))) > 500:
        errors.append("source_reference is too long; store a stable reference, not a transcript")
    destination_error = validate_destination(str(meta.get("canonical_destination", "")))
    if destination_error:
        errors.append(destination_error)
    summary = extract_section(body, "Summary")
    if not summary:
        errors.append("Summary section must not be empty")
    if len(summary) > 4000:
        errors.append("Summary is too long")
    if meta.get("normalized_key") and meta.get("scope") and meta.get("type") and meta.get("title"):
        if meta["normalized_key"] != normalized_key(meta):
            errors.append("normalized_key mismatch")
    if meta.get("content_fingerprint") and summary:
        if meta["content_fingerprint"] != candidate_fingerprint(meta, summary):
            errors.append("content_fingerprint mismatch")
    secret_categories = scan_secrets(record_text(meta, body))
    if secret_categories:
        errors.append("secret scan failed: " + ", ".join(secret_categories))
    return errors


def all_candidate_paths(root: Path) -> Iterable[Path]:
    for name in ("inbox", "review", "archive"):
        directory = root / "memory" / name
        if directory.exists():
            yield from (path for path in directory.glob("*.md") if not path.name.endswith(".review.md"))


def find_duplicate(root: Path, fingerprint: str, exclude: Path | None = None) -> Path | None:
    for path in all_candidate_paths(root):
        if exclude and path.resolve() == exclude.resolve():
            continue
        try:
            meta, _ = split_candidate(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if meta.get("content_fingerprint") == fingerprint:
            return path
    index = load_index(root)
    for entry in index["entries"]:
        if entry.get("content_fingerprint") == fingerprint:
            return root / str(entry.get("canonical_destination", "memory/index/memory-index.json"))
    return None


def load_index(root: Path) -> dict[str, Any]:
    path = root / "memory" / "index" / "memory-index.json"
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "entries": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("entries"), list):
        raise ValueError("memory index entries must be a list")
    return data


def save_index(root: Path, data: dict[str, Any]) -> None:
    data["schema_version"] = SCHEMA_VERSION
    data["entries"] = sorted(data["entries"], key=lambda item: (item.get("normalized_key", ""), item.get("memory_id", "")))
    atomic_write_text(root / "memory" / "index" / "memory-index.json", json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def git_path(root: Path, value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def validate_auto_git_context(root: Path) -> dict[str, Any]:
    if not (root / ".git").exists():
        raise RuntimeError("AUTO promotion requires a Git worktree")
    branch = git(["branch", "--show-current"], root).stdout.strip()
    if branch in {"", "main", "master"}:
        raise RuntimeError("AUTO promotion requires a non-main branch")
    git_dir = git_path(root, git(["rev-parse", "--git-dir"], root).stdout.strip())
    common_dir = git_path(root, git(["rev-parse", "--git-common-dir"], root).stdout.strip())
    if git_dir == common_dir:
        raise RuntimeError("AUTO promotion requires an independent linked worktree")
    status = git_status_paths(root)
    unrelated = sorted(path for path in status if not path.startswith("memory/inbox/"))
    if unrelated:
        raise RuntimeError(f"AUTO promotion worktree has unrelated changes: {unrelated}")
    return {"branch": branch, "head": git(["rev-parse", "HEAD"], root).stdout.strip(), "status": status}


def path_snapshot(path: Path) -> bytes | None:
    return path.read_bytes() if path.exists() else None


def restore_path_snapshot(path: Path, content: bytes | None) -> None:
    if content is None:
        with contextlib.suppress(FileNotFoundError):
            path.unlink()
        with contextlib.suppress(OSError):
            path.parent.rmdir()
    else:
        atomic_write_bytes(path, content)


def maybe_inject_promotion_fault(root: Path, stage: str) -> None:
    requested = os.environ.get("AI_WORKSPACE_MEMORY_FAULT_INJECTION", "").strip()
    if not requested:
        return
    if not (root / ".memory-test-allow-faults").exists():
        raise RuntimeError("fault injection is disabled outside a marked disposable worktree")
    if requested == "git-status-change" and stage == "after-target":
        atomic_write_text(root / ".memory-fault-unrelated", "fault injection\n")
        return
    if requested == stage:
        raise RuntimeError(f"injected promotion failure at {stage}")


def write_recovery_record(state_dir: Path, memory_id: str, error: Exception, rollback_error: Exception) -> Path:
    path = state_dir / "recovery" / f"{memory_id}.json"
    payload = {
        "schema_version": SCHEMA_VERSION,
        "memory_id": memory_id,
        "status": "manual-recovery-required",
        "created_at": utc_now(),
        "error_type": type(error).__name__,
        "rollback_error_type": type(rollback_error).__name__,
    }
    atomic_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return path


def assert_promotion_git_state(root: Path, context: dict[str, Any], managed_paths: set[str]) -> None:
    branch = git(["branch", "--show-current"], root).stdout.strip()
    head = git(["rev-parse", "HEAD"], root).stdout.strip()
    if branch != context["branch"] or head != context["head"]:
        raise RuntimeError("Git branch or HEAD changed during AUTO promotion")
    current = git_status_paths(root)
    unexpected = sorted(current - set(context["status"]) - managed_paths)
    if unexpected:
        raise RuntimeError(f"Git status changed outside promotion transaction: {unexpected}")


def promote_solution_transaction(
    root: Path,
    state_dir: Path,
    candidate_path: Path,
    meta: dict[str, Any],
    summary: str,
    index: dict[str, Any],
    git_context: dict[str, Any],
) -> Path:
    recovery = state_dir / "recovery"
    if recovery.exists() and any(recovery.glob("*.json")):
        raise RuntimeError("unresolved promotion recovery record; AUTO promotion is blocked")
    target = root / str(meta["canonical_destination"])
    archive = root / "memory" / "archive" / candidate_path.name
    index_path = root / "memory" / "index" / "memory-index.json"
    managed = {
        candidate_path.relative_to(root).as_posix(), target.relative_to(root).as_posix(),
        archive.relative_to(root).as_posix(), index_path.relative_to(root).as_posix(),
    }
    snapshots = {path: path_snapshot(path) for path in (candidate_path, target, archive, index_path)}
    index_before = copy.deepcopy(index)
    try:
        assert_promotion_git_state(root, git_context, managed)
        atomic_write_text(target, solution_document(meta, summary))
        maybe_inject_promotion_fault(root, "after-target")
        assert_promotion_git_state(root, git_context, managed)
        maybe_inject_promotion_fault(root, "before-archive")
        archive_candidate(root, candidate_path, dict(meta), summary, "promoted", "AUTO solution allowlist")
        maybe_inject_promotion_fault(root, "after-archive")
        assert_promotion_git_state(root, git_context, managed)
        index["entries"].append({
            "memory_id": meta["memory_id"],
            "normalized_key": meta["normalized_key"],
            "content_fingerprint": meta["content_fingerprint"],
            "canonical_destination": meta["canonical_destination"],
            "promoted_at": utc_now(),
            "source_reference": meta["source_reference"],
        })
        maybe_inject_promotion_fault(root, "index-save")
        save_index(root, index)
        assert_promotion_git_state(root, git_context, managed)
        git_context["status"] = git_status_paths(root)
        return target
    except Exception as exc:
        try:
            for path, content in snapshots.items():
                restore_path_snapshot(path, content)
            index.clear()
            index.update(index_before)
        except Exception as rollback_exc:
            record = write_recovery_record(state_dir, str(meta.get("memory_id", "unknown")), exc, rollback_exc)
            raise RuntimeError(f"promotion rollback failed; recovery record: {record}") from rollback_exc
        raise


def git(args: list[str], root: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, text=True, encoding="utf-8", errors="replace", capture_output=True, check=check)


def status_path(line: str) -> str:
    value = line[3:].strip()
    if " -> " in value:
        value = value.split(" -> ", 1)[1]
    if value.startswith('"'):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass
    return value.replace("\\", "/")


def git_status_paths(root: Path) -> set[str]:
    lines = git(["status", "--porcelain", "--untracked-files=all"], root).stdout.splitlines()
    return {status_path(line) for line in lines if line.strip()}


def load_repository_registry(state_dir: Path) -> list[dict[str, Any]]:
    path = state_dir / "repositories.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != SCHEMA_VERSION or not isinstance(data.get("repositories"), list):
        raise ValueError("local repositories registry schema is invalid")
    return data["repositories"]


def approved_private_repository(data: dict[str, Any], state_dir: Path) -> tuple[Path | None, str, str]:
    scope = str(data.get("scope", ""))
    expected_classification = PRIVATE_CLASSIFICATION_BY_SCOPE.get(scope, "")
    alias = str(data.get("repository_alias", "")).strip()
    if not expected_classification:
        return None, "", "scope is not eligible for private Git routing"
    if not alias or normalize_text(alias) in PROVENANCE_PLACEHOLDERS:
        return None, expected_classification, "approved repository_alias is required"
    matches = [entry for entry in load_repository_registry(state_dir) if str(entry.get("alias", "")) == alias]
    if len(matches) != 1:
        return None, expected_classification, "repository alias is not uniquely approved"
    entry = matches[0]
    if not entry.get("enabled", False) or not entry.get("writer_enabled", False):
        return None, expected_classification, "repository writer is not enabled"
    if entry.get("classification") != expected_classification:
        return None, expected_classification, "repository classification does not match scope"
    allowed_scopes = entry.get("allowed_scopes", [])
    allowed_sensitivities = entry.get("allowed_sensitivities", [])
    allowed_projects = entry.get("allowed_source_projects", [])
    if not all(isinstance(value, list) for value in (allowed_scopes, allowed_sensitivities, allowed_projects)):
        return None, expected_classification, "repository allowlists must be lists"
    if scope not in allowed_scopes:
        return None, expected_classification, "scope is not approved for repository"
    if str(data.get("sensitivity", "")) not in allowed_sensitivities:
        return None, expected_classification, "sensitivity is not approved for repository"
    if str(data.get("source_project", "")) not in allowed_projects:
        return None, expected_classification, "source project is not approved for repository"
    raw_path = Path(str(entry.get("path", "")))
    if not raw_path.is_absolute():
        return None, expected_classification, "approved repository path must be absolute"
    path = raw_path.resolve()
    if not path.is_dir():
        return None, expected_classification, "approved repository is unavailable"
    probe = git(["rev-parse", "--show-toplevel"], path, check=False)
    if probe.returncode != 0 or Path(probe.stdout.strip()).resolve() != path:
        return None, expected_classification, "approved destination is not the Git repository root"
    return path, expected_classification, "approved"


def commit_candidate(root: Path, candidate: Path, push: bool) -> dict[str, str]:
    branch = git(["branch", "--show-current"], root).stdout.strip()
    if branch in {"main", "master", ""}:
        raise RuntimeError("automatic candidate commits require a non-main branch")
    status = git(["status", "--porcelain", "--untracked-files=all"], root).stdout.splitlines()
    relative = candidate.relative_to(root).as_posix()
    unrelated = [line for line in status if status_path(line) != relative]
    if unrelated:
        raise RuntimeError(f"working tree contains unrelated changes; candidate commit refused: {unrelated}")
    git(["add", "--", relative], root)
    git(["commit", "-m", f"memory: capture {candidate.stem}"], root)
    commit = git(["rev-parse", "HEAD"], root).stdout.strip()
    result = {"branch": branch, "commit": commit}
    if push:
        git(["push", "-u", "origin", branch], root)
        result["pushed"] = "true"
    return result


def build_event(args: argparse.Namespace) -> dict[str, Any]:
    data: dict[str, Any] = {}
    if args.event:
        data.update(parse_flat_yaml(Path(args.event).read_text(encoding="utf-8")))
    for key in (
        "title", "type", "scope", "sensitivity", "source_host", "source_project",
        "source_actor_alias", "source_reference", "related_task", "related_commit",
        "summary", "canonical_destination", "repository_alias",
    ):
        value = getattr(args, key, None)
        if value is not None:
            data[key] = value
    for key in ("durability_score", "reuse_score", "evidence_score", "confidence"):
        value = getattr(args, key, None)
        if value is not None:
            data[key] = value
    for key in ("evidence", "constraints", "supersedes"):
        value = getattr(args, key, None)
        if value:
            data[key] = value
        data.setdefault(key, [])
    defaults = {
        "schema_version": SCHEMA_VERSION,
        "type": "lesson",
        "scope": "unknown",
        "sensitivity": "unknown",
        "source_host": "unknown",
        "source_project": "unknown",
        "source_actor_alias": "unknown",
        "source_reference": "unknown",
        "related_task": "",
        "related_commit": "",
        "durability_score": 0,
        "reuse_score": 0,
        "evidence_score": 0,
        "confidence": 0.0,
        "canonical_destination": "",
        "repository_alias": "",
    }
    for key, value in defaults.items():
        data.setdefault(key, value)
    return data


def capture_command(args: argparse.Namespace) -> int:
    root, state_dir = Path(args.root).resolve(), Path(args.state_dir).resolve()
    mode, mode_source = get_mode(root, state_dir)
    if mode == "OFF":
        emit("rejected", reason="memory mode OFF", mode=mode, mode_source=mode_source, captured=0)
        return 0
    data = build_event(args)
    required_event = ["title", "summary", "source_reference"]
    missing = [key for key in required_event if not str(data.get(key, "")).strip()]
    if missing:
        emit("failed", reason="missing event fields", fields=missing)
        return 2
    created = utc_now()
    seed = json.dumps({key: data.get(key) for key in sorted(data)}, ensure_ascii=False, sort_keys=True) + created
    memory_id = f"MEM-{dt.datetime.now():%Y%m%d}-{hashlib.sha256(seed.encode()).hexdigest()[:12].upper()}"
    meta = {**data, "memory_id": memory_id, "status": "candidate", "created_at": created}
    summary = str(meta.pop("summary"))
    meta["normalized_key"] = normalized_key(meta)
    meta["content_fingerprint"] = candidate_fingerprint(meta, summary)
    candidate_text = render_candidate(meta, summary)
    _, candidate_body = split_candidate(candidate_text)
    secret_categories = scan_secrets(record_text(meta, candidate_body))
    if secret_categories:
        outbox = write_outbox(state_dir, "local-only", {**meta, "summary": summary}, "secret scan failed", secret_categories)
        emit("local-only", reason="secret scan failed", secret_categories=secret_categories, outbox=str(outbox), captured=0)
        return 0
    validation_errors = validate_meta(meta, candidate_body, require_git_provenance=False)
    if validation_errors:
        outbox = write_outbox(state_dir, "failed-validation", {**meta, "summary": summary}, "; ".join(validation_errors))
        emit("failed", reason="candidate validation failed", errors=validation_errors, outbox=str(outbox), captured=0)
        return 2
    public_safe = meta["scope"] == "public" and meta["sensitivity"] == "public"
    destination_root = root
    repository_classification = "public-control-plane"
    if args.force_outbox:
        reason = "writer unavailable"
        outbox = write_outbox(state_dir, "route-required", {**meta, "summary": summary}, reason)
        emit("local-only", reason=reason, scope=meta["scope"], sensitivity=meta["sensitivity"], outbox=str(outbox), captured=0)
        return 0
    if public_safe and str(meta.get("repository_alias", "")).strip():
        reason = "public Candidate cannot target a private repository_alias"
        outbox = write_outbox(state_dir, "route-required", {**meta, "summary": summary}, reason)
        emit("local-only", reason=reason, outbox=str(outbox), captured=0)
        return 0
    if not public_safe:
        try:
            destination_root, repository_classification, route_reason = approved_private_repository(meta, state_dir)
        except Exception as exc:
            destination_root, repository_classification = None, ""
            route_reason = f"repository registry rejected: {type(exc).__name__}"
        if destination_root is not None:
            try:
                destination_root.relative_to(root)
                destination_root = None
                route_reason = "private repository must be outside the public control-plane repository"
            except ValueError:
                pass
        if destination_root is None:
            outbox = write_outbox(state_dir, "route-required", {**meta, "summary": summary}, route_reason)
            emit(
                "local-only", reason=route_reason, scope=meta["scope"], sensitivity=meta["sensitivity"],
                repository_alias=meta.get("repository_alias", ""), outbox=str(outbox), captured=0,
            )
            return 0
    provenance = provenance_errors(meta)
    if provenance:
        outbox = write_outbox(state_dir, "provenance-required", {**meta, "summary": summary}, "; ".join(provenance))
        emit("local-only", reason="Git provenance required", errors=provenance, outbox=str(outbox), captured=0)
        return 0
    candidate = destination_root / "memory" / "inbox" / f"{memory_id}-{slugify(str(meta['title']))}.md"
    try:
        with FileLock(destination_root, state_dir):
            duplicate = find_duplicate(destination_root, meta["content_fingerprint"])
            if duplicate:
                emit("rejected", reason="duplicate", duplicate_of=str(duplicate), captured=0)
                return 0
            atomic_write_text(candidate, candidate_text)
        git_result: dict[str, str] = {}
        if args.git_commit:
            git_result = commit_candidate(destination_root, candidate, args.git_push)
        emit(
            "captured", memory_id=memory_id, path=str(candidate), mode=mode, captured=1,
            repository_alias=meta.get("repository_alias", ""), repository_classification=repository_classification,
            git=git_result,
        )
        return 0
    except Exception as exc:
        outbox = write_outbox(state_dir, "failed", {**meta, "summary": summary}, f"repository write failed: {type(exc).__name__}")
        emit("failed", reason=str(exc), outbox=str(outbox), captured=0)
        return 1


def validate_command(args: argparse.Namespace) -> int:
    path = Path(args.path).resolve()
    try:
        meta, body = split_candidate(path.read_text(encoding="utf-8"))
        errors = validate_meta(meta, body)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    if errors:
        emit("failed", path=str(path), valid=False, errors=errors)
        return 1
    emit("validated", path=str(path), valid=True, memory_id=meta["memory_id"])
    return 0


def write_review(root: Path, candidate_path: Path, meta: dict[str, Any], summary: str, reason: str, conflicts: list[str]) -> Path:
    meta["status"] = "review"
    meta["curated_at"] = utc_now()
    meta["review_reason"] = reason
    target = root / "memory" / "review" / candidate_path.name
    atomic_write_text(target, render_candidate(meta, summary))
    review_id = f"REV-{dt.datetime.now():%Y%m%d}-{os.urandom(6).hex().upper()}"
    review = {
        "schema_version": SCHEMA_VERSION,
        "review_id": review_id,
        "memory_id": meta["memory_id"],
        "status": "pending",
        "reason": reason,
        "review_actor": "ChatGPT/User",
        "created_at": utc_now(),
        "conflicts_with": conflicts,
        "recommended_action": "Review evidence, routing and canonical destination; do not overwrite existing content.",
    }
    lines = ["---", *[f"{key}: {yaml_value(value)}" for key, value in review.items()], "---", "", "## Candidate Summary", "", summary, "", "## Review Decision", "", "- Decision: Pending", "- Rationale:", "- Canonical destination:", ""]
    atomic_write_text(target.with_name(target.stem + ".review.md"), "\n".join(lines))
    candidate_path.unlink()
    return target


def archive_candidate(root: Path, candidate_path: Path, meta: dict[str, Any], summary: str, status: str, reason: str) -> Path:
    meta["status"] = status
    meta["curated_at"] = utc_now()
    meta["review_reason"] = reason
    target = root / "memory" / "archive" / candidate_path.name
    atomic_write_text(target, render_candidate(meta, summary))
    candidate_path.unlink()
    return target


def solution_document(meta: dict[str, Any], summary: str) -> str:
    evidence = "\n".join(f"- {item}" for item in meta.get("evidence", [])) or "- None recorded"
    constraints = "\n".join(f"- {item}" for item in meta.get("constraints", [])) or "- None recorded"
    return (
        f"# {meta['title']}\n\n"
        f"- Status: Confirmed / Auto-promoted under TASK-0016 policy\n"
        f"- Source candidate: `{meta['memory_id']}`\n"
        f"- Source: `{meta['source_reference']}`\n"
        f"- Related task: `{meta.get('related_task', '')}`\n"
        f"- Related commit: `{meta.get('related_commit', '')}`\n\n"
        f"## Summary\n\n{summary}\n\n## Evidence\n\n{evidence}\n\n"
        f"## Constraints\n\n{constraints}\n"
    )


def auto_eligible(meta: dict[str, Any], root: Path) -> tuple[bool, str]:
    if meta.get("type") != "solution":
        return False, "type not in auto-promotion allowlist"
    if meta.get("scope") != "public" or meta.get("sensitivity") != "public":
        return False, "not Public-safe"
    if min(int(meta.get(key, 0)) for key in ("durability_score", "reuse_score", "evidence_score")) < 4:
        return False, "scores below auto threshold"
    if float(meta.get("confidence", 0)) < 0.9:
        return False, "confidence below auto threshold"
    if not meta.get("evidence"):
        return False, "evidence required"
    destination = str(meta.get("canonical_destination", ""))
    if not re.fullmatch(r"solutions/[a-z0-9][a-z0-9-]*/README\.md", destination):
        return False, "solution destination not allowlisted"
    if (root / destination).exists():
        return False, "canonical destination already exists"
    return True, "eligible"


def curate_command(args: argparse.Namespace) -> int:
    root, state_dir = Path(args.root).resolve(), Path(args.state_dir).resolve()
    mode, _ = get_mode(root, state_dir)
    if mode == "OFF":
        emit("rejected", reason="memory mode OFF", promoted=0, review=0, rejected=0, failed=0)
        return 0
    counts = {"promoted": 0, "review": 0, "rejected": 0, "local-only": 0, "failed": 0}
    details: list[dict[str, Any]] = []
    try:
        git_context = validate_auto_git_context(root) if mode == "AUTO" else {}
        with FileLock(root, state_dir):
            index = load_index(root)
            for path in sorted((root / "memory" / "inbox").glob("*.md")):
                try:
                    meta, body = split_candidate(path.read_text(encoding="utf-8"))
                    summary = extract_section(body, "Summary")
                    errors = validate_meta(meta, body)
                    if errors:
                        categories = scan_secrets(record_text(meta, body))
                        if categories:
                            quarantine = state_dir / "outbox" / "quarantine" / path.name
                            quarantine.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(path), str(quarantine))
                            write_outbox(state_dir, "local-only", {**meta, "summary": summary}, "manual candidate failed secret scan", categories)
                            counts["local-only"] += 1
                            details.append({"memory_id": meta.get("memory_id"), "result": "local-only", "errors": errors})
                        else:
                            archive_candidate(root, path, meta, summary or "Invalid candidate", "rejected", "; ".join(errors))
                            counts["rejected"] += 1
                            details.append({"memory_id": meta.get("memory_id"), "result": "rejected", "errors": errors})
                        continue
                    duplicate = find_duplicate(root, meta["content_fingerprint"], exclude=path)
                    if duplicate:
                        archive_candidate(root, path, meta, summary, "rejected", f"duplicate of {duplicate}")
                        counts["rejected"] += 1
                        details.append({"memory_id": meta["memory_id"], "result": "duplicate"})
                        continue
                    conflicts = [
                        str(entry.get("canonical_destination", entry.get("memory_id")))
                        for entry in index["entries"]
                        if entry.get("normalized_key") == meta["normalized_key"]
                        and entry.get("content_fingerprint") != meta["content_fingerprint"]
                    ]
                    destination = str(meta.get("canonical_destination", ""))
                    if destination and (root / destination).exists() and not any(entry.get("content_fingerprint") == meta["content_fingerprint"] for entry in index["entries"]):
                        conflicts.append(destination)
                    if conflicts:
                        write_review(root, path, meta, summary, "conflict", sorted(set(conflicts)))
                        counts["review"] += 1
                        details.append({"memory_id": meta["memory_id"], "result": "conflict"})
                        continue
                    if mode == "ASSISTED":
                        write_review(root, path, meta, summary, "assisted-mode", [])
                        counts["review"] += 1
                        details.append({"memory_id": meta["memory_id"], "result": "review"})
                        continue
                    eligible, reason = auto_eligible(meta, root)
                    if not eligible:
                        write_review(root, path, meta, summary, reason, [])
                        counts["review"] += 1
                        details.append({"memory_id": meta["memory_id"], "result": "review", "reason": reason})
                        continue
                    target = promote_solution_transaction(root, state_dir, path, meta, summary, index, git_context)
                    counts["promoted"] += 1
                    details.append({"memory_id": meta["memory_id"], "result": "promoted", "target": str(target)})
                except Exception as exc:
                    counts["failed"] += 1
                    details.append({"path": str(path), "result": "failed", "reason": str(exc)})
    except Exception as exc:
        counts["failed"] += 1
        emit("failed", reason=str(exc), **counts)
        return 1
    emit("curated", mode=mode, details=details, **counts)
    return 1 if counts["failed"] else 0


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def markdown_link_errors(root: Path, paths: Iterable[Path]) -> list[str]:
    errors: list[str] = []
    pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        for raw in pattern.findall(text):
            target = raw.strip().strip("<>").split("#", 1)[0]
            if not target or re.match(r"^(?:https?://|mailto:)", target):
                continue
            target_path = (path.parent / target).resolve()
            try:
                target_path.relative_to(root)
            except ValueError:
                errors.append(f"{path.relative_to(root)}: link escapes repository: {target}")
                continue
            if not target_path.exists():
                errors.append(f"{path.relative_to(root)}: missing link target: {target}")
    return errors


def task_statuses(root: Path) -> list[tuple[str, str]]:
    statuses: list[tuple[str, str]] = []
    for path in sorted((root / "tasks").glob("TASK-*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"^- Status:\s*(.+)$", text, re.M)
        if match:
            statuses.append((path.name, match.group(1).strip()))
    return statuses


def repository_state(root: Path, sync: bool) -> dict[str, Any]:
    if not (root / ".git").exists():
        return {"status": "not-git", "head": "", "branch": "", "dirty": False, "sync": "not-requested"}
    branch = git(["branch", "--show-current"], root).stdout.strip()
    head = git(["rev-parse", "HEAD"], root).stdout.strip()
    dirty = bool(git(["status", "--porcelain"], root).stdout.strip())
    sync_status = "not-requested"
    if sync:
        if dirty:
            sync_status = "skipped-dirty"
        else:
            result = git(["pull", "--ff-only"], root, check=False)
            sync_status = "up-to-date" if result.returncode == 0 else "failed"
            if result.returncode == 0:
                head = git(["rev-parse", "HEAD"], root).stdout.strip()
    return {"status": "available", "head": head, "branch": branch, "dirty": dirty, "sync": sync_status}


def registered_repository_states(state_dir: Path, include: bool, sync: bool) -> tuple[list[dict[str, Any]], str]:
    registry = state_dir / "repositories.json"
    if not include:
        return [], "not read"
    if not registry.exists():
        return [], "registry unavailable"
    data = json.loads(registry.read_text(encoding="utf-8"))
    entries = data.get("repositories", [])
    if not isinstance(entries, list):
        raise ValueError("local repositories registry must contain a repositories list")
    results: list[dict[str, Any]] = []
    for entry in entries:
        alias = str(entry.get("alias", "unnamed"))
        path = Path(str(entry.get("path", ""))).resolve()
        if not entry.get("enabled", False):
            results.append({"alias": alias, "status": "disabled"})
            continue
        if not path.exists():
            results.append({"alias": alias, "status": "unavailable"})
            continue
        state = repository_state(path, sync)
        results.append({"alias": alias, **state})
    return results, "processed locally; details withheld from public manifest"


def managed_current_state(root: Path, mode: str, generated_at: str) -> None:
    path = root / "bootstrap" / "chatgpt" / "02_CURRENT_STATE.md"
    text = path.read_text(encoding="utf-8")
    active = [(name, status) for name, status in task_statuses(root) if status.lower() in {"in progress", "review", "ready"}]
    lines = [
        "<!-- MEMORY-CONTEXT:START -->",
        "## Automatic Memory Context",
        "",
        f"- Generated: {generated_at}",
        f"- Effective mode during refresh: `{mode}`",
        "- Context Manifest: `CONTEXT_MANIFEST.yaml`",
        "- Project Sources update: `manual upload required`",
        "- Private repositories: not read by default; explicit registry and authorization required",
        "",
        "### Active public control-plane tasks",
        "",
    ]
    lines.extend(f"- `{name}` — {status}" for name, status in active)
    lines.append("<!-- MEMORY-CONTEXT:END -->")
    block = "\n".join(lines)
    pattern = re.compile(r"<!-- MEMORY-CONTEXT:START -->.*?<!-- MEMORY-CONTEXT:END -->", re.S)
    updated = pattern.sub(block, text) if pattern.search(text) else text.rstrip() + "\n\n" + block + "\n"
    atomic_write_text(path, updated)


def managed_handoff(root: Path, mode: str, generated_at: str) -> None:
    path = root / "handoff" / "CODEX.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    block = "\n".join([
        "<!-- MEMORY-REFRESH:START -->",
        "## Memory Context Refresh",
        "",
        f"- Generated: {generated_at}",
        f"- Effective mode: `{mode}`",
        "- Manifest: `CONTEXT_MANIFEST.yaml`",
        "- ChatGPT Project Sources: `manual upload required`",
        "- Private repositories: not read unless explicitly registered and authorized",
        "<!-- MEMORY-REFRESH:END -->",
    ])
    pattern = re.compile(r"<!-- MEMORY-REFRESH:START -->.*?<!-- MEMORY-REFRESH:END -->\n*", re.S)
    text = pattern.sub("", text).rstrip() + "\n"
    marker = "\n## Exact Next Action"
    if marker in text:
        text = text.replace(marker, "\n\n" + block + marker, 1)
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    atomic_write_text(path, text)


def refresh_command(args: argparse.Namespace) -> int:
    root, state_dir = Path(args.root).resolve(), Path(args.state_dir).resolve()
    mode, mode_source = get_mode(root, state_dir)
    generated_at = utc_now()
    include_roots = ["capabilities", "standards", "docs/adr", "skills", "workflows", "solutions", "tasks", "handoff", "bootstrap/chatgpt"]
    try:
        repo_state = repository_state(root, args.sync)
        registered_states, private_status = registered_repository_states(
            state_dir, args.include_registered_repositories, args.sync
        )
        with FileLock(root, state_dir):
            managed_current_state(root, mode, generated_at)
            managed_handoff(root, mode, generated_at)
            files: list[Path] = []
            for relative in include_roots:
                base = root / relative
                if base.exists():
                    files.extend(path for path in base.rglob("*") if path.is_file() and "generated" not in path.parts)
            files = sorted(set(files), key=lambda item: item.relative_to(root).as_posix())
            secret_issues = [
                f"{path.relative_to(root)}:{','.join(scan_secrets(path.read_text(encoding='utf-8', errors='replace')))}"
                for path in files if scan_secrets(path.read_text(encoding="utf-8", errors="replace"))
            ]
            link_issues = markdown_link_errors(root, files)
            manifest_lines = [
                f'schema_version: "{SCHEMA_VERSION}"',
                f'generated_at: "{generated_at}"',
                f'memory_mode: "{mode}"',
                'repository_scope: "public-control-plane"',
                f'repository_head: {json.dumps(repo_state["head"])}',
                f'repository_branch: {json.dumps(repo_state["branch"])}',
                f'repository_dirty_before_refresh: {str(repo_state["dirty"]).lower()}',
                f'repository_sync: {json.dumps(repo_state["sync"])}',
                f'private_repositories: {json.dumps(private_status)}',
                "sources:",
            ]
            for path in files:
                relative = path.relative_to(root).as_posix()
                manifest_lines.extend([
                    f'  - path: {json.dumps(relative, ensure_ascii=False)}',
                    f'    sha256: "{file_sha256(path)}"',
                    f'    bytes: {path.stat().st_size}',
                ])
            manifest_lines.extend(["checks:", f"  secret_issues: {len(secret_issues)}", f"  broken_links: {len(link_issues)}", 'project_source_update: "manual upload required"', ""])
            manifest_text = "\n".join(manifest_lines)
            manifest_path = root / "CONTEXT_MANIFEST.yaml"
            atomic_write_text(manifest_path, manifest_text)
            source_files = [
                root / "bootstrap" / "chatgpt" / name for name in
                ("PROJECT_INSTRUCTIONS.md", "00_CORE_RULES.md", "01_SYSTEM_CONTEXT.md", "02_CURRENT_STATE.md", "03_NEW_CHAT_BOOTSTRAP.md")
            ]
            pack_lines = ["# ChatGPT Project Source Pack", "", f"Generated: {generated_at}", "", "本文件只组合 AI-Workspace 中已经审阅的 public control-plane sources；Git 仍是最新真相源。", ""]
            for path in source_files:
                pack_lines.extend([f"<!-- SOURCE: {path.name} -->", path.read_text(encoding="utf-8").rstrip(), ""])
            pack_path = root / "bootstrap" / "chatgpt" / "generated" / "PROJECT_SOURCE_PACK.md"
            atomic_write_text(pack_path, "\n".join(pack_lines).rstrip() + "\n")
            replacement_lines = [
                "# Project Source Replacement List", "", f"Generated: {generated_at}", "",
                "Status: **manual upload required**", "",
                "当前没有在本任务范围内获批的安全 API 用于自动替换 ChatGPT Project Sources。请在 ChatGPT Project 设置中手动替换以下来源：", "",
            ]
            replacement_lines.extend(f"- `{path.relative_to(root).as_posix()}` — `{file_sha256(path)}`" for path in source_files)
            replacement_lines.extend(["", f"可选单文件包：`{pack_path.relative_to(root).as_posix()}` — `{file_sha256(pack_path)}`", "", "不要同时上传单文件包和五个拆分来源，以免重复。", ""])
            replacement_path = root / "bootstrap" / "chatgpt" / "generated" / "PROJECT_SOURCE_REPLACEMENT_LIST.md"
            atomic_write_text(replacement_path, "\n".join(replacement_lines))
        registered_sync_failures = [
            item.get("alias", "unnamed") for item in registered_states
            if args.sync and item.get("status") == "available" and item.get("sync") != "up-to-date"
        ]
        sync_complete = not args.sync or (repo_state["sync"] == "up-to-date" and not registered_sync_failures)
        emit(
            "refreshed", mode=mode, mode_source=mode_source, manifest=str(manifest_path),
            source_pack=str(pack_path), replacement_list=str(replacement_path),
            manual_upload_required=True, sources=len(files), secret_issues=secret_issues,
            broken_links=link_issues, repository=repo_state,
            private_repositories=private_status, registered_repositories=registered_states,
            sync_complete=sync_complete, registered_sync_failures=registered_sync_failures,
        )
        return 1 if secret_issues or link_issues or not sync_complete else 0
    except Exception as exc:
        outbox = write_outbox(state_dir, "failed", {"title": "Context refresh failed", "source_host": "memory-cli", "source_project": root.name, "summary": str(exc)}, f"refresh failed: {type(exc).__name__}")
        emit("failed", reason=str(exc), outbox=str(outbox))
        return 1


def status_command(args: argparse.Namespace) -> int:
    root, state_dir = Path(args.root).resolve(), Path(args.state_dir).resolve()
    mode, source = get_mode(root, state_dir)
    counts = {}
    for name in ("inbox", "review", "archive"):
        directory = root / "memory" / name
        counts[name] = len([path for path in directory.glob("*.md") if not path.name.endswith(".review.md")]) if directory.exists() else 0
    outbox = state_dir / "outbox"
    counts["outbox"] = len(list(outbox.rglob("*.json"))) if outbox.exists() else 0
    emit("status", mode=mode, mode_source=source, state_dir=str(state_dir), queues=counts, subagent_dependency="none")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI-Workspace Git-backed memory tooling")
    parser.add_argument("--root", default=str(repo_root_from_script()))
    parser.add_argument("--state-dir", default=str(default_state_dir()))
    sub = parser.add_subparsers(dest="command", required=True)

    capture = sub.add_parser("capture")
    capture.add_argument("--event")
    for name in ("title", "type", "scope", "sensitivity", "source-host", "source-project", "source-actor-alias", "source-reference", "related-task", "related-commit", "summary", "canonical-destination", "repository-alias"):
        capture.add_argument(f"--{name}", dest=name.replace("-", "_"))
    for name in ("durability-score", "reuse-score", "evidence-score"):
        capture.add_argument(f"--{name}", dest=name.replace("-", "_"), type=int)
    capture.add_argument("--confidence", type=float)
    capture.add_argument("--evidence", action="append")
    capture.add_argument("--constraint", dest="constraints", action="append")
    capture.add_argument("--supersedes", action="append")
    capture.add_argument("--force-outbox", action="store_true")
    capture.add_argument("--git-commit", action="store_true")
    capture.add_argument("--git-push", action="store_true")
    capture.set_defaults(func=capture_command)

    validate = sub.add_parser("validate")
    validate.add_argument("path")
    validate.set_defaults(func=validate_command)

    curate = sub.add_parser("curate")
    curate.set_defaults(func=curate_command)

    refresh = sub.add_parser("refresh")
    refresh.add_argument("--sync", action="store_true", help="ff-only pull clean registered repositories before refresh")
    refresh.add_argument("--include-registered-repositories", action="store_true", help="read the Host-local repositories.json registry")
    refresh.set_defaults(func=refresh_command)

    status = sub.add_parser("status")
    status.set_defaults(func=status_command)

    mode = sub.add_parser("set-mode")
    mode.add_argument("mode", choices=["Off", "Assisted", "Auto", "OFF", "ASSISTED", "AUTO"])
    mode.set_defaults(func=lambda args: (set_mode(Path(args.root).resolve(), Path(args.state_dir).resolve(), args.mode), emit("mode-set", mode=args.mode.upper(), path=str(mode_paths(Path(args.root).resolve(), Path(args.state_dir).resolve())[0])), 0)[2])
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
