#!/usr/bin/env python3
"""Run TASK-0016 Host/routing Pilot in a disposable repository."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


CLI = Path(__file__).resolve().with_name("memory_cli.py")


def invoke(root: Path, state: Path, *args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(CLI), "--root", str(root), "--state-dir", str(state), *args],
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError(result.stderr or "memory CLI returned no output")
    payload = json.loads(lines[-1])
    payload["exit_code"] = result.returncode
    return payload


def event(
    title: str,
    host: str,
    memory_type: str,
    scope: str,
    sensitivity: str,
    summary: str,
    destination: str = "",
    reference: str = "TASK-0016-PILOT",
    project: str = "AI-Workspace-Pilot",
    repository_alias: str = "",
) -> list[str]:
    args = [
        "capture", "--title", title, "--type", memory_type, "--scope", scope,
        "--sensitivity", sensitivity, "--source-host", host,
        "--source-project", project, "--source-actor-alias", host,
        "--source-reference", reference, "--related-task", "TASK-0016",
        "--durability-score", "5", "--reuse-score", "5", "--evidence-score", "5",
        "--confidence", "0.96", "--summary", summary,
        "--evidence", "TASK-0016 authorization and isolated pilot output",
    ]
    if destination:
        args.extend(["--canonical-destination", destination])
    if repository_alias:
        args.extend(["--repository-alias", repository_alias])
    return args


def prepare(root: Path) -> None:
    for relative in (
        "memory/inbox", "memory/review", "memory/archive", "memory/index",
        "solutions", "tasks", "handoff", "capabilities", "standards",
        "docs/adr", "skills", "workflows", "bootstrap/chatgpt/generated",
    ):
        (root / relative).mkdir(parents=True, exist_ok=True)
    (root / "memory/index/default-mode.json").write_text(
        json.dumps({"schema_version": "1.0", "default_mode": "ASSISTED"}), encoding="utf-8"
    )
    (root / "memory/index/memory-index.json").write_text(
        json.dumps({"schema_version": "1.0", "entries": []}), encoding="utf-8"
    )
    for name in ("PROJECT_INSTRUCTIONS.md", "00_CORE_RULES.md", "01_SYSTEM_CONTEXT.md", "03_NEW_CHAT_BOOTSTRAP.md"):
        (root / "bootstrap/chatgpt" / name).write_text(f"# {name}\n\nPublic Pilot source.\n", encoding="utf-8")
    (root / "bootstrap/chatgpt/02_CURRENT_STATE.md").write_text("# Pilot Current State\n", encoding="utf-8")
    (root / "tasks/TASK-0016.md").write_text("# TASK-0016\n\n- Status: In Progress\n", encoding="utf-8")


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, text=True, encoding="utf-8", capture_output=True)


def initialize_git(root: Path) -> None:
    git(root, "init", "-b", "main")
    git(root, "config", "user.name", "Memory Pilot")
    git(root, "config", "user.email", "memory-pilot@example.invalid")
    git(root, "add", ".")
    git(root, "commit", "-m", "pilot baseline")


def prepare_private_repository(path: Path) -> None:
    path.mkdir(parents=True)
    git(path, "init", "-b", "main")
    git(path, "config", "user.name", "Memory Pilot")
    git(path, "config", "user.email", "memory-pilot@example.invalid")
    (path / "README.md").write_text("# Disposable private Pilot repository\n", encoding="utf-8")
    git(path, "add", ".")
    git(path, "commit", "-m", "private pilot baseline")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="task-0016-pilot-") as temp:
        base = Path(temp)
        source, root, state = base / "source", base / "worktree", base / "state"
        private_root = base / "private-repo"
        prepare(source)
        initialize_git(source)
        git(source, "worktree", "add", "-b", "memory/task-0016-pilot", str(root))
        prepare_private_repository(private_root)
        state.mkdir(parents=True, exist_ok=True)
        registry = {
            "schema_version": "1.0",
            "repositories": [
                {
                    "alias": "private-pilot",
                    "path": str(private_root),
                    "enabled": True,
                    "writer_enabled": True,
                    "classification": "project-private",
                    "allowed_scopes": ["project-private"],
                    "allowed_sensitivities": ["internal"],
                    "allowed_source_projects": ["Disposable-Private-Pilot"],
                },
                {
                    "alias": "wrong-classification",
                    "path": str(private_root),
                    "enabled": True,
                    "writer_enabled": True,
                    "classification": "public-control-plane",
                    "allowed_scopes": ["project-private"],
                    "allowed_sensitivities": ["internal"],
                    "allowed_source_projects": ["Disposable-Private-Pilot"],
                },
            ],
        }
        (state / "repositories.json").write_text(json.dumps(registry, indent=2), encoding="utf-8")
        scenarios: list[dict] = []

        invoke(root, state, "set-mode", "Assisted")
        chatgpt = invoke(
            root,
            state,
            *event(
                "Production memory mode remains ASSISTED",
                "ChatGPT",
                "decision",
                "public",
                "public",
                "User-authorized Pilot tests AUTO in isolation, while production remains ASSISTED pending Review.",
                reference="TASK-0016-EXECUTION-AUTHORIZATION",
            ),
        )
        chatgpt_curate = invoke(root, state, "curate")
        scenarios.append({"scenario": "ChatGPT explicit decision", "capture": chatgpt, "curate": chatgpt_curate})
        git(root, "add", ".")
        git(root, "commit", "-m", "pilot assisted review state")

        invoke(root, state, "set-mode", "Auto")
        codex = invoke(
            root,
            state,
            *event(
                "Transcript-free Codex memory check",
                "Codex",
                "solution",
                "public",
                "public",
                "Use source-side structured events and a transcript-free SessionEnd marker; never upload rollout JSONL.",
                destination="solutions/transcript-free-codex-memory-check/README.md",
            ),
        )
        codex_curate = invoke(root, state, "curate")
        scenarios.append({"scenario": "Codex completed solution", "capture": codex, "curate": codex_curate})

        generic = invoke(
            root,
            state,
            *event(
                "Private Generic Agent skill candidate",
                "GenericIDE",
                "skill",
                "project-private",
                "internal",
                "A reusable private project procedure that must remain outside public AI-Workspace.",
                project="Disposable-Private-Pilot",
                repository_alias="private-pilot",
            ),
        )
        scenarios.append({
            "scenario": "Generic IDE approved private skill",
            "capture": generic,
            "private_candidate_exists": Path(generic.get("path", "missing")).exists(),
            "public_inbox_count": len(list((root / "memory/inbox").glob("*.md"))),
        })

        unauthorized = invoke(
            root,
            state,
            *event(
                "Unapproved private writer",
                "GenericIDE",
                "skill",
                "project-private",
                "internal",
                "This private event must remain in Outbox without an approved alias.",
                project="Disposable-Private-Pilot",
                repository_alias="not-approved",
            ),
        )
        scenarios.append({"scenario": "Unapproved private writer Outbox", "capture": unauthorized})

        wrong_classification = invoke(
            root,
            state,
            *event(
                "Wrong private repository classification",
                "GenericIDE",
                "skill",
                "project-private",
                "internal",
                "A classification mismatch must fail closed to Outbox.",
                project="Disposable-Private-Pilot",
                repository_alias="wrong-classification",
            ),
        )
        scenarios.append({"scenario": "Wrong classification Outbox", "capture": wrong_classification})

        read_only = invoke(
            root,
            state,
            *event(
                "Read-only ChatGPT public candidate",
                "ChatGPT",
                "lesson",
                "public",
                "public",
                "A public-safe event produced on a Host without an approved Git writer.",
            ),
            "--force-outbox",
        )
        scenarios.append({"scenario": "Read-only Host Outbox", "capture": read_only})

        secret_value = "sk-PILOTSECRET0123456789"
        secret = invoke(
            root,
            state,
            *event(
                "Secret scan route",
                "GenericIDE",
                "lesson",
                "public",
                "public",
                f"This accidental value must be redacted: {secret_value}",
            ),
        )
        outbox_text = Path(secret["outbox"]).read_text(encoding="utf-8")
        scenarios.append({
            "scenario": "Secret scan",
            "capture": secret,
            "secret_literal_absent_from_outbox": secret_value not in outbox_text,
        })

        invoke(root, state, "set-mode", "Off")
        off = invoke(
            root,
            state,
            *event("OFF suppression", "Codex", "lesson", "public", "public", "This must not be captured."),
        )
        scenarios.append({"scenario": "OFF kill switch", "capture": off})

        invoke(root, state, "set-mode", "Assisted")
        refresh = invoke(root, state, "refresh")
        final_status = invoke(root, state, "status")

        metrics = {
            "captured": sum(1 for item in scenarios if item["capture"].get("status") == "captured"),
            "private_git_captured": sum(1 for item in scenarios if item["capture"].get("repository_classification") == "project-private"),
            "promoted": sum(item.get("curate", {}).get("promoted", 0) for item in scenarios),
            "review": sum(item.get("curate", {}).get("review", 0) for item in scenarios),
            "local_only_or_outbox": sum(1 for item in scenarios if item["capture"].get("status") == "local-only"),
            "suppressed": sum(1 for item in scenarios if item["capture"].get("status") == "rejected" and item["capture"].get("reason") == "memory mode OFF"),
            "conflicts": 0,
            "failed": sum(1 for item in scenarios if item["capture"].get("status") == "failed"),
            "false_positive_count": "not measured; requires User review",
            "missed_capture_count": "not measured; requires live Host observation",
        }
        report = {
            "pilot": "TASK-0016",
            "environment": "disposable linked worktree and disposable private Git repository; no production hook or real private repository access",
            "scenarios": scenarios,
            "refresh": refresh,
            "final_status": final_status,
            "metrics": metrics,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if metrics["failed"] == 0 and final_status.get("mode") == "ASSISTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
