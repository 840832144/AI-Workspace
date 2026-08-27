from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


CLI = Path(__file__).resolve().parents[1] / "memory_cli.py"
CAPTURE_PS1 = CLI.with_name("Capture-MemoryCandidate.ps1")
STATUS_PS1 = CLI.with_name("Get-MemoryStatus.ps1")
MODE_PS1 = CLI.with_name("Set-MemoryMode.ps1")
CURATE_PS1 = CLI.with_name("Curate-MemoryCandidates.ps1")
REFRESH_PS1 = CLI.with_name("Refresh-ProjectContext.ps1")


class MemoryCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="memory-cli-test-")
        base = Path(self.temp.name)
        self.base = base
        self.root = base / "repo"
        self.state = base / "state"
        for relative in (
            "memory/inbox", "memory/review", "memory/archive", "memory/index",
            "solutions", "tasks", "handoff", "capabilities", "standards",
            "docs/adr", "docs/incidents", "skills", "workflows", "bootstrap/chatgpt/generated",
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

    def run_cli(self, *args: str, expect: int | None = 0, env: dict[str, str] | None = None) -> tuple[subprocess.CompletedProcess[str], dict]:
        command = [sys.executable, str(CLI), "--root", str(self.root), "--state-dir", str(self.state), *args]
        process_env = None
        if env:
            process_env = dict(os.environ, **env)
        result = subprocess.run(command, text=True, encoding="utf-8", capture_output=True, env=process_env)
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

    def git(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", *args], cwd=root, text=True, encoding="utf-8", capture_output=True, check=True)

    def initialize_git(self, root: Path, *, allow_faults: bool = False) -> None:
        if allow_faults:
            (root / ".memory-test-allow-faults").write_text("disposable tests only\n", encoding="utf-8")
        self.git(root, "init", "-b", "main")
        self.git(root, "config", "user.name", "Memory Test")
        self.git(root, "config", "user.email", "memory-test@example.invalid")
        self.git(root, "add", ".")
        self.git(root, "commit", "-m", "baseline")

    def use_auto_worktree(self, *, allow_faults: bool = False) -> None:
        source = self.root
        self.initialize_git(source, allow_faults=allow_faults)
        worktree = self.base / "auto-worktree"
        self.git(source, "worktree", "add", "-b", "memory/test", str(worktree))
        self.root = worktree

    def commit_all(self, message: str) -> None:
        self.git(self.root, "add", ".")
        self.git(self.root, "commit", "-m", message)

    def prepare_private_registry(self, *, classification: str = "project-private", writer_enabled: bool = True) -> Path:
        private = self.base / "private-repo"
        private.mkdir()
        self.git(private, "init", "-b", "main")
        self.git(private, "config", "user.name", "Memory Test")
        self.git(private, "config", "user.email", "memory-test@example.invalid")
        (private / "README.md").write_text("# Disposable private repository\n", encoding="utf-8")
        self.git(private, "add", ".")
        self.git(private, "commit", "-m", "baseline")
        self.state.mkdir(parents=True, exist_ok=True)
        registry = {
            "schema_version": "1.0",
            "repositories": [{
                "alias": "private-pilot",
                "path": str(private),
                "enabled": True,
                "writer_enabled": writer_enabled,
                "classification": classification,
                "allowed_scopes": ["project-private"],
                "allowed_sensitivities": ["internal"],
                "allowed_source_projects": ["Private-Pilot"],
            }],
        }
        (self.state / "repositories.json").write_text(json.dumps(registry), encoding="utf-8")
        return private

    def private_capture_args(self) -> list[str]:
        return self.capture_args(scope="project-private", sensitivity="internal") + [
            "--source-project", "Private-Pilot", "--repository-alias", "private-pilot",
        ]

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

    def test_approved_project_private_route_writes_only_private_git_repo(self) -> None:
        private = self.prepare_private_registry()
        _, output = self.run_cli(*self.private_capture_args())
        self.assertEqual("captured", output["status"])
        self.assertEqual("project-private", output["repository_classification"])
        self.assertTrue(Path(output["path"]).is_relative_to(private))
        self.assertEqual(1, len(list((private / "memory/inbox").glob("*.md"))))
        self.assertFalse(list((self.root / "memory/inbox").glob("*.md")))

    def test_unapproved_private_writer_routes_to_outbox(self) -> None:
        _, output = self.run_cli(*self.private_capture_args())
        self.assertEqual("local-only", output["status"])
        self.assertTrue(Path(output["outbox"]).exists())
        self.assertFalse(list((self.root / "memory/inbox").glob("*.md")))

    def test_invalid_private_registry_routes_to_outbox(self) -> None:
        self.state.mkdir(parents=True, exist_ok=True)
        (self.state / "repositories.json").write_text('{"schema_version":"bad","repositories":[]}', encoding="utf-8")
        _, output = self.run_cli(*self.private_capture_args())
        self.assertEqual("local-only", output["status"])
        self.assertIn("registry rejected", output["reason"])
        self.assertTrue(Path(output["outbox"]).exists())

    def test_public_candidate_cannot_use_private_repository_alias(self) -> None:
        _, output = self.run_cli(*self.capture_args(), "--repository-alias", "private-pilot")
        self.assertEqual("local-only", output["status"])
        self.assertIn("cannot target", output["reason"])
        self.assertFalse(list((self.root / "memory/inbox").glob("*.md")))

    def test_wrong_private_repository_classification_fails_closed(self) -> None:
        private = self.prepare_private_registry(classification="public-control-plane")
        _, output = self.run_cli(*self.private_capture_args())
        self.assertEqual("local-only", output["status"])
        self.assertIn("classification", output["reason"])
        self.assertFalse((private / "memory/inbox").exists())
        self.assertFalse(list((self.root / "memory/inbox").glob("*.md")))

    def test_private_registry_cannot_point_to_public_control_plane(self) -> None:
        self.initialize_git(self.root)
        self.state.mkdir(parents=True, exist_ok=True)
        registry = {
            "schema_version": "1.0",
            "repositories": [{
                "alias": "private-pilot", "path": str(self.root), "enabled": True,
                "writer_enabled": True, "classification": "project-private",
                "allowed_scopes": ["project-private"], "allowed_sensitivities": ["internal"],
                "allowed_source_projects": ["Private-Pilot"],
            }],
        }
        (self.state / "repositories.json").write_text(json.dumps(registry), encoding="utf-8")
        _, output = self.run_cli(*self.private_capture_args())
        self.assertEqual("local-only", output["status"])
        self.assertIn("outside the public control-plane", output["reason"])
        self.assertFalse(list((self.root / "memory/inbox").glob("*.md")))

    def test_private_sensitivity_mismatch_fails_closed(self) -> None:
        private = self.prepare_private_registry()
        args = self.private_capture_args()
        args[args.index("--sensitivity") + 1] = "confidential"
        _, output = self.run_cli(*args)
        self.assertEqual("local-only", output["status"])
        self.assertIn("sensitivity", output["reason"])
        self.assertFalse((private / "memory/inbox").exists())

    def test_non_git_routes_stay_in_outbox(self) -> None:
        for index, (scope, sensitivity) in enumerate((
            ("cross-project-private", "confidential"),
            ("local-only", "secret"),
            ("unknown", "unknown"),
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
        self.use_auto_worktree()
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
        self.use_auto_worktree()
        self.set_mode("Auto")
        target = self.root / "solutions/reusable-solution/README.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("KEEP\n", encoding="utf-8")
        self.commit_all("add existing solution")
        self.run_cli(*self.capture_args())
        _, curated = self.run_cli("curate")
        self.assertEqual(1, curated["review"])
        self.assertEqual("KEEP\n", target.read_text(encoding="utf-8"))

    def test_conflict_with_promoted_key_goes_to_review(self) -> None:
        self.use_auto_worktree()
        self.set_mode("Auto")
        self.run_cli(*self.capture_args(summary="Version one."))
        self.run_cli("curate")
        self.commit_all("commit first promotion")
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

    def test_cli_placeholder_provenance_routes_to_outbox(self) -> None:
        args = self.capture_args()
        args[args.index("--source-host") + 1] = "unknown"
        _, output = self.run_cli(*args)
        self.assertEqual("local-only", output["status"])
        self.assertEqual("Git provenance required", output["reason"])
        self.assertFalse(list((self.root / "memory/inbox").glob("*.md")))

    def test_event_file_placeholder_provenance_routes_to_outbox(self) -> None:
        event = self.base / "event.yaml"
        event.write_text(
            "\n".join([
                'schema_version: "1.0"', 'title: "Event provenance"', 'type: "solution"',
                'scope: "public"', 'sensitivity: "public"', 'source_host: "codex"',
                'source_project: "AI-Workspace"', 'source_actor_alias: "Codex"',
                'source_reference: "n/a"', 'summary: "Event-file provenance must be stable."',
                'durability_score: 5', 'reuse_score: 5', 'evidence_score: 5', 'confidence: 0.95',
                'evidence: ["event-test"]', 'constraints: []', 'supersedes: []',
                'canonical_destination: "solutions/event-provenance/README.md"',
            ]) + "\n",
            encoding="utf-8",
        )
        _, output = self.run_cli("capture", "--event", str(event))
        self.assertEqual("local-only", output["status"])
        self.assertEqual("Git provenance required", output["reason"])
        self.assertFalse(list((self.root / "memory/inbox").glob("*.md")))

    def test_generic_agent_placeholder_actor_routes_to_outbox(self) -> None:
        args = self.capture_args()
        args[args.index("--source-host") + 1] = "GenericIDE"
        args[args.index("--source-actor-alias") + 1] = "none"
        _, output = self.run_cli(*args)
        self.assertEqual("local-only", output["status"])
        self.assertEqual("Git provenance required", output["reason"])
        self.assertFalse(list((self.root / "memory/inbox").glob("*.md")))

    def test_refresh_generates_manifest_pack_and_manual_upload_list(self) -> None:
        (self.root / "docs/incidents/INCIDENT-TEST.md").write_text("# Incident\n", encoding="utf-8")
        _, output = self.run_cli("refresh")
        self.assertEqual("refreshed", output["status"])
        self.assertTrue(output["manual_upload_required"])
        self.assertEqual("not read", output["private_repositories"])
        self.assertTrue((self.root / "CONTEXT_MANIFEST.yaml").exists())
        manifest = (self.root / "CONTEXT_MANIFEST.yaml").read_text(encoding="utf-8")
        self.assertIn("docs/incidents/INCIDENT-TEST.md", manifest)
        self.assertTrue((self.root / "bootstrap/chatgpt/generated/PROJECT_SOURCE_PACK.md").exists())
        replacement = (self.root / "bootstrap/chatgpt/generated/PROJECT_SOURCE_REPLACEMENT_LIST.md").read_text(encoding="utf-8")
        self.assertIn("manual upload required", replacement)
        current = (self.root / "bootstrap/chatgpt/02_CURRENT_STATE.md").read_text(encoding="utf-8")
        self.assertIn("MEMORY-CONTEXT:START", current)

    def test_refresh_active_tasks_excludes_companion(self) -> None:
        (self.root / "tasks/TASK-0001-CANONICAL.md").write_text(
            "# TASK-0001 — Canonical\n\n- Status: Review\n", encoding="utf-8"
        )
        (self.root / "tasks/TASK-0001-AUTHORIZATION.md").write_text(
            "# TASK-0001 Authorization\n\n- Kind: companion\n- Status: Ready\n", encoding="utf-8"
        )
        self.run_cli("refresh")
        current = (self.root / "bootstrap/chatgpt/02_CURRENT_STATE.md").read_text(encoding="utf-8")
        self.assertIn("TASK-0001-CANONICAL.md", current)
        self.assertNotIn("TASK-0001-AUTHORIZATION.md", current)

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

    def test_auto_curate_rejects_main_branch_without_mutation(self) -> None:
        self.initialize_git(self.root)
        self.set_mode("Auto")
        _, capture = self.run_cli(*self.capture_args())
        candidate = Path(capture["path"])
        before = candidate.read_bytes()
        _, output = self.run_cli("curate", expect=1)
        self.assertEqual("failed", output["status"])
        self.assertEqual(0, output["promoted"])
        self.assertTrue(candidate.exists())
        self.assertEqual(before, candidate.read_bytes())
        self.assertFalse((self.root / "solutions/reusable-solution/README.md").exists())

    def test_auto_curate_rejects_unrelated_dirty_worktree(self) -> None:
        self.use_auto_worktree()
        self.set_mode("Auto")
        _, capture = self.run_cli(*self.capture_args())
        candidate = Path(capture["path"])
        (self.root / "unrelated.txt").write_text("unrelated\n", encoding="utf-8")
        _, output = self.run_cli("curate", expect=1)
        self.assertEqual("failed", output["status"])
        self.assertEqual(0, output["promoted"])
        self.assertTrue(candidate.exists())

    def assert_fault_rolls_back(self, stage: str) -> None:
        self.use_auto_worktree(allow_faults=True)
        self.set_mode("Auto")
        _, capture = self.run_cli(*self.capture_args())
        candidate = Path(capture["path"])
        candidate_before = candidate.read_bytes()
        index_path = self.root / "memory/index/memory-index.json"
        index_before = index_path.read_bytes()
        target = self.root / "solutions/reusable-solution/README.md"
        archive = self.root / "memory/archive" / candidate.name
        _, output = self.run_cli(
            "curate", expect=1, env={"AI_WORKSPACE_MEMORY_FAULT_INJECTION": stage},
        )
        self.assertEqual("curated", output["status"])
        self.assertEqual(0, output["promoted"])
        self.assertEqual(1, output["failed"])
        self.assertTrue(candidate.exists())
        self.assertEqual(candidate_before, candidate.read_bytes())
        self.assertFalse(target.exists())
        self.assertFalse(archive.exists())
        self.assertEqual(index_before, index_path.read_bytes())
        self.assertFalse(list((self.state / "recovery").glob("*.json")) if (self.state / "recovery").exists() else [])

    def test_auto_transaction_rolls_back_after_target_failure(self) -> None:
        self.assert_fault_rolls_back("after-target")

    def test_auto_transaction_rolls_back_before_archive_failure(self) -> None:
        self.assert_fault_rolls_back("before-archive")

    def test_auto_transaction_rolls_back_after_archive_failure(self) -> None:
        self.assert_fault_rolls_back("after-archive")

    def test_auto_transaction_rolls_back_index_save_failure(self) -> None:
        self.assert_fault_rolls_back("index-save")

    def test_auto_transaction_rolls_back_on_git_status_change(self) -> None:
        self.assert_fault_rolls_back("git-status-change")

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

    @unittest.skipUnless(sys.platform.startswith("win"), "PowerShell wrapper test is Windows-specific")
    def test_powershell_thin_wrappers_do_not_append_empty_argument(self) -> None:
        commands = (
            [str(STATUS_PS1), "-Root", str(self.root), "-StateDir", str(self.state)],
            [str(MODE_PS1), "-Mode", "Assisted", "-Root", str(self.root), "-StateDir", str(self.state)],
            [str(CURATE_PS1), "-Root", str(self.root), "-StateDir", str(self.state)],
            [str(REFRESH_PS1), "-Root", str(self.root), "-StateDir", str(self.state)],
        )
        for command in commands:
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", *command],
                text=True,
                encoding="utf-8",
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, msg=result.stdout + result.stderr)
            self.assertTrue(result.stdout.strip(), msg=result.stderr)
            json.loads(result.stdout.splitlines()[-1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
