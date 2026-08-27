from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).resolve().parents[1] / "memory_cli.py"
CAPTURE_PS1 = CLI.with_name("Capture-MemoryCandidate.ps1")


class MemoryCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="memory-cli-test-")
        base = Path(self.temp.name)
        self.root = base / "repo"
        self.state = base / "state"
        for relative in (
            "memory/inbox", "memory/review", "memory/archive", "memory/index",
            "solutions", "tasks", "handoff", "capabilities", "standards",
            "docs/adr", "skills", "workflows", "bootstrap/chatgpt/generated",
        ):
            (self.root / relative).mkdir(parents=True, exist_ok=True)
        (self.root / "memory/index/default-mode.json").write_text(
            json.dumps({"schema_version": "1.0", "default_mode": "ASSISTED"}), encoding="utf-8"
        )
        (self.root / "memory/index/memory-index.json").write_text(
            json.dumps({"schema_version": "1.0", "entries": []}), encoding="utf-8"
        )
        for name in ("PROJECT_INSTRUCTIONS.md", "00_CORE_RULES.md", "01_SYSTEM_CONTEXT.md", "03_NEW_CHAT_BOOTSTRAP.md"):
            (self.root / "bootstrap/chatgpt" / name).write_text(f"# {name}\n\nPublic source.\n", encoding="utf-8")
        (self.root / "bootstrap/chatgpt/02_CURRENT_STATE.md").write_text("# Current\n", encoding="utf-8")
        (self.root / "tasks/TASK-TEST.md").write_text("# Task\n\n- Status: In Progress\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_cli(self, *args: str, expect: int | None = 0) -> tuple[subprocess.CompletedProcess[str], dict]:
        command = [sys.executable, str(CLI), "--root", str(self.root), "--state-dir", str(self.state), *args]
        result = subprocess.run(command, text=True, encoding="utf-8", capture_output=True)
        if expect is not None:
            self.assertEqual(expect, result.returncode, msg=result.stdout + result.stderr)
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        self.assertTrue(lines, msg=result.stderr)
        return result, json.loads(lines[-1])

    def capture_args(self, *, title: str = "Reusable solution", summary: str = "A durable public summary.", scope: str = "public", sensitivity: str = "public", destination: str = "solutions/reusable-solution/README.md", memory_type: str = "solution") -> list[str]:
        return [
            "capture", "--title", title, "--type", memory_type, "--scope", scope,
            "--sensitivity", sensitivity, "--source-host", "codex",
            "--source-project", "AI-Workspace", "--source-actor-alias", "Codex",
            "--source-reference", "TASK-TEST", "--related-task", "TASK-TEST",
            "--durability-score", "5", "--reuse-score", "5", "--evidence-score", "5",
            "--confidence", "0.95", "--summary", summary, "--evidence", "commit:test",
            "--canonical-destination", destination,
        ]

    def set_mode(self, mode: str) -> dict:
        return self.run_cli("set-mode", mode)[1]

    def test_off_suppresses_capture(self) -> None:
        self.set_mode("Off")
        _, output = self.run_cli(*self.capture_args())
        self.assertEqual("rejected", output["status"])
        self.assertFalse(list((self.root / "memory/inbox").glob("*.md")))

    def test_assisted_capture_and_review(self) -> None:
        _, capture = self.run_cli(*self.capture_args())
        self.assertEqual("captured", capture["status"])
        candidate = Path(capture["path"])
        _, validated = self.run_cli("validate", str(candidate))
        self.assertTrue(validated["valid"])
        _, curated = self.run_cli("curate")
        self.assertEqual(1, curated["review"])
        self.assertFalse(candidate.exists())
        self.assertEqual(1, len([p for p in (self.root / "memory/review").glob("*.md") if not p.name.endswith(".review.md")]))

    def test_private_and_local_routes_never_touch_public_inbox(self) -> None:
        for index, (scope, sensitivity) in enumerate((
            ("project-private", "internal"),
            ("cross-project-private", "confidential"),
            ("local-only", "secret"),
        )):
            _, output = self.run_cli(*self.capture_args(title=f"Private {index}", scope=scope, sensitivity=sensitivity))
            self.assertEqual("local-only", output["status"])
            self.assertTrue(Path(output["outbox"]).exists())
        self.assertFalse(list((self.root / "memory/inbox").glob("*.md")))

    def test_secret_is_redacted_in_outbox(self) -> None:
        secret = "sk-ABCDEFGHIJKLMNOPQRSTUV"
        _, output = self.run_cli(*self.capture_args(summary=f"Accidental {secret}"))
        self.assertEqual("local-only", output["status"])
        text = Path(output["outbox"]).read_text(encoding="utf-8")
        self.assertNotIn(secret, text)
        self.assertIn("REDACTED", text)
        self.assertFalse(list((self.root / "memory/inbox").glob("*.md")))

    def test_deterministic_duplicate_rejected(self) -> None:
        _, first = self.run_cli(*self.capture_args())
        _, second = self.run_cli(*self.capture_args())
        self.assertEqual("captured", first["status"])
        self.assertEqual("rejected", second["status"])
        self.assertEqual("duplicate", second["reason"])
        self.assertEqual(1, len(list((self.root / "memory/inbox").glob("*.md"))))

    def test_auto_promotes_new_solution_and_archives_candidate(self) -> None:
        self.set_mode("Auto")
        self.run_cli(*self.capture_args())
        _, curated = self.run_cli("curate")
        self.assertEqual(1, curated["promoted"])
        target = self.root / "solutions/reusable-solution/README.md"
        self.assertTrue(target.exists())
        self.assertIn("Source candidate", target.read_text(encoding="utf-8"))
        self.assertEqual(1, len(list((self.root / "memory/archive").glob("*.md"))))
        index = json.loads((self.root / "memory/index/memory-index.json").read_text(encoding="utf-8"))
        self.assertEqual(1, len(index["entries"]))

    def test_existing_destination_is_reviewed_without_overwrite(self) -> None:
        self.set_mode("Auto")
        target = self.root / "solutions/reusable-solution/README.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("KEEP\n", encoding="utf-8")
        self.run_cli(*self.capture_args())
        _, curated = self.run_cli("curate")
        self.assertEqual(1, curated["review"])
        self.assertEqual("KEEP\n", target.read_text(encoding="utf-8"))

    def test_conflict_with_promoted_key_goes_to_review(self) -> None:
        self.set_mode("Auto")
        self.run_cli(*self.capture_args(summary="Version one."))
        self.run_cli("curate")
        self.run_cli(*self.capture_args(summary="Version two.", destination="solutions/reusable-solution-v2/README.md"))
        _, curated = self.run_cli("curate")
        self.assertEqual(1, curated["review"])
        self.assertEqual("conflict", curated["details"][0]["result"])

    def test_tampered_candidate_fails_validation(self) -> None:
        _, capture = self.run_cli(*self.capture_args())
        path = Path(capture["path"])
        path.write_text(path.read_text(encoding="utf-8").replace("A durable public summary.", "Tampered."), encoding="utf-8")
        _, output = self.run_cli("validate", str(path), expect=1)
        self.assertFalse(output["valid"])
        self.assertIn("content_fingerprint mismatch", output["errors"])

    def test_invalid_destination_fails_before_public_write(self) -> None:
        _, output = self.run_cli(
            *self.capture_args(destination="../outside.md"),
            expect=2,
        )
        self.assertEqual("failed", output["status"])
        self.assertIn("canonical_destination escapes the repository", output["errors"])
        self.assertFalse(list((self.root / "memory/inbox").glob("*.md")))
        self.assertTrue(Path(output["outbox"]).exists())

    def test_concurrent_duplicate_capture_is_serialized(self) -> None:
        command = [sys.executable, str(CLI), "--root", str(self.root), "--state-dir", str(self.state), *self.capture_args()]
        processes = [subprocess.Popen(command, text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
        outputs = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=20)
            self.assertEqual(0, process.returncode, msg=stdout + stderr)
            outputs.append(json.loads(stdout.splitlines()[-1]))
        self.assertEqual(["captured", "rejected"], sorted((item["status"] for item in outputs)))
        self.assertEqual(1, len(list((self.root / "memory/inbox").glob("*.md"))))

    def test_force_outbox_simulates_read_only_host(self) -> None:
        _, output = self.run_cli(*self.capture_args(), "--force-outbox")
        self.assertEqual("local-only", output["status"])
        self.assertEqual("writer unavailable", output["reason"])

    def test_refresh_generates_manifest_pack_and_manual_upload_list(self) -> None:
        _, output = self.run_cli("refresh")
        self.assertEqual("refreshed", output["status"])
        self.assertTrue(output["manual_upload_required"])
        self.assertEqual("not read", output["private_repositories"])
        self.assertTrue((self.root / "CONTEXT_MANIFEST.yaml").exists())
        self.assertTrue((self.root / "bootstrap/chatgpt/generated/PROJECT_SOURCE_PACK.md").exists())
        replacement = (self.root / "bootstrap/chatgpt/generated/PROJECT_SOURCE_REPLACEMENT_LIST.md").read_text(encoding="utf-8")
        self.assertIn("manual upload required", replacement)
        current = (self.root / "bootstrap/chatgpt/02_CURRENT_STATE.md").read_text(encoding="utf-8")
        self.assertIn("MEMORY-CONTEXT:START", current)

    def test_refresh_sync_does_not_claim_latest_when_repository_is_dirty(self) -> None:
        subprocess.run(["git", "init", "-b", "main"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Memory Test"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "memory-test@example.invalid"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "baseline"], cwd=self.root, check=True, capture_output=True)
        (self.root / "tasks/TASK-TEST.md").write_text("# Task\n\n- Status: Review\n", encoding="utf-8")
        _, output = self.run_cli("refresh", "--sync", expect=1)
        self.assertFalse(output["sync_complete"])
        self.assertEqual("skipped-dirty", output["repository"]["sync"])

    def test_git_commit_requires_non_main_and_clean_tree(self) -> None:
        subprocess.run(["git", "init", "-b", "main"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Memory Test"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "memory-test@example.invalid"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "baseline"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "switch", "-c", "memory/test"], cwd=self.root, check=True, capture_output=True)
        _, output = self.run_cli(*self.capture_args(), "--git-commit")
        self.assertEqual("captured", output["status"])
        self.assertEqual("memory/test", output["git"]["branch"])
        status = subprocess.run(["git", "status", "--porcelain"], cwd=self.root, text=True, capture_output=True, check=True).stdout
        self.assertEqual("", status)

    @unittest.skipUnless(sys.platform.startswith("win"), "PowerShell wrapper test is Windows-specific")
    def test_powershell_capture_wrapper(self) -> None:
        result = subprocess.run(
            [
                "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(CAPTURE_PS1),
                "-Root", str(self.root), "-StateDir", str(self.state),
                "-Title", "PowerShell wrapper", "-Type", "lesson", "-Scope", "public",
                "-Sensitivity", "public", "-SourceHost", "Codex", "-SourceProject", "AI-Workspace",
                "-SourceActorAlias", "Codex", "-SourceReference", "TASK-TEST",
                "-DurabilityScore", "4", "-ReuseScore", "4", "-EvidenceScore", "4",
                "-Confidence", "0.95", "-Summary", "PowerShell named parameters reach the Python validator.",
                "-Evidence", "wrapper-test",
            ],
            text=True,
            encoding="utf-8",
            capture_output=True,
        )
        self.assertEqual(0, result.returncode, msg=result.stdout + result.stderr)
        output = json.loads(result.stdout.splitlines()[-1])
        self.assertEqual("captured", output["status"])
        self.assertTrue(Path(output["path"]).exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
