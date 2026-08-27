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
) -> list[str]:
    args = [
        "capture", "--title", title, "--type", memory_type, "--scope", scope,
        "--sensitivity", sensitivity, "--source-host", host,
        "--source-project", "AI-Workspace-Pilot", "--source-actor-alias", host,
        "--source-reference", reference, "--related-task", "TASK-0016",
        "--durability-score", "5", "--reuse-score", "5", "--evidence-score", "5",
        "--confidence", "0.96", "--summary", summary,
        "--evidence", "TASK-0016 authorization and isolated pilot output",
    ]
    if destination:
        args.extend(["--canonical-destination", destination])
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


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="task-0016-pilot-") as temp:
        base = Path(temp)
        root, state = base / "repo", base / "state"
        prepare(root)
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
            ),
        )
        scenarios.append({"scenario": "Generic IDE private skill", "capture": generic})

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
            "environment": "disposable repository; no production hook or private repository access",
            "scenarios": scenarios,
            "refresh": refresh,
            "final_status": final_status,
            "metrics": metrics,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if metrics["failed"] == 0 and final_status.get("mode") == "ASSISTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
