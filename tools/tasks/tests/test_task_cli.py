from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "task_cli.py"
SPEC = importlib.util.spec_from_file_location("task_cli", MODULE_PATH)
assert SPEC and SPEC.loader
task_cli = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = task_cli
SPEC.loader.exec_module(task_cli)


def canonical(task_id: str, title: str, *, status: str = "Ready", project: str = "WORKSPACE", goal: str = "建立可验证的治理能力。") -> str:
    return f"""# {task_id} — {title}

- Status: {status}
- Project key: {project}
- Owner: User / ChatGPT
- Executor: Codex
- Priority: P1
- Date: 2026-08-27

## Goal

{goal}

## Scope

只处理测试夹具。

## Non-goals

不访问外部业务仓库。

## Deliverables

确定性结果。

## Safety

仅使用临时目录。

## Validation

运行测试。

## Handoff

记录结果。
"""


def candidate(candidate_id: str, title: str, *, decision: str = "Pending", goal: str = "研究新的治理能力。", project: str = "WORKSPACE") -> str:
    return f"""# {candidate_id} — {title}

- Kind: candidate
- Status: Candidate
- Project key: {project}
- Suggested priority: P1 candidate
- User decision: {decision}
- Source: disposable-test
- Created: 2026-08-27
- Updated: 2026-08-27
- Migrated to:
- Migrated at:

## Goal

{goal}

## Dependencies

None.

## Risks

Test only.
"""


class RepositoryFixture:
    def __init__(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        self.remote = self.base / "remote.git"
        self.worktree = self.base / "worktree"
        self.source.mkdir()
        self.git(self.source, "init", "-b", "main")
        self.git(self.source, "config", "user.name", "Task Tests")
        self.git(self.source, "config", "user.email", "task-tests@example.invalid")
        (self.source / "tasks" / "candidates").mkdir(parents=True)
        (self.source / "reviews").mkdir()
        (self.source / "tasks" / "README.md").write_text("# Tasks\n", encoding="utf-8")
        self.write_source("tasks/TASK-0019-EXISTING.md", canonical("TASK-0019", "Existing Task", goal="建立现有任务治理。"))
        self.refresh_registry(self.source)
        self.git(self.source, "add", ".")
        self.git(self.source, "commit", "-m", "test: initialize fixture")
        self.git(self.base, "init", "--bare", str(self.remote))
        self.git(self.source, "remote", "add", "origin", str(self.remote))
        self.git(self.source, "push", "-u", "origin", "main")
        self.git(self.source, "worktree", "add", "-b", "test/task", str(self.worktree), "main")
        self.git(self.worktree, "config", "user.name", "Task Tests")
        self.git(self.worktree, "config", "user.email", "task-tests@example.invalid")

    def close(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", *args], cwd=cwd, check=check, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def write_source(self, relative: str, text: str) -> Path:
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def write(self, relative: str, text: str) -> Path:
        path = self.worktree / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    @staticmethod
    def refresh_registry(root: Path) -> None:
        result = task_cli.scan_repository(root)
        if result.errors:
            raise AssertionError(result.errors)
        (root / "tasks" / "TASK_REGISTRY.yaml").write_text(task_cli.render_registry(result), encoding="utf-8", newline="\n")

    def run(self, *args: str) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        process = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--root", str(self.worktree), *args],
            text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        lines = [line for line in process.stdout.splitlines() if line.strip()]
        payload = json.loads(lines[-1]) if lines else {}
        return process, payload


class TaskCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = RepositoryFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def test_duplicate_canonical_id_fails(self) -> None:
        self.fixture.write("tasks/TASK-0019-DUPLICATE.md", canonical("TASK-0019", "Duplicate"))
        process, payload = self.fixture.run("validate")
        self.assertNotEqual(process.returncode, 0)
        self.assertTrue(any("duplicate canonical ID TASK-0019" in item for item in payload["errors"]))

    def test_companion_with_same_id_is_classified_not_collided(self) -> None:
        self.fixture.write("tasks/TASK-0019-AUTHORIZATION.md", """# TASK-0019 Execution Authorization

- Kind: companion
- Status: Ready
- Canonical task: `tasks/TASK-0019-EXISTING.md`
""")
        self.fixture.refresh_registry(self.fixture.worktree)
        process, payload = self.fixture.run("validate")
        self.assertEqual(process.returncode, 0, payload)
        scan_process, scan_payload = self.fixture.run("scan")
        self.assertEqual(scan_process.returncode, 0)
        kinds = [item["kind"] for item in scan_payload["records"] if item["id"] == "TASK-0019"]
        self.assertEqual(sorted(kinds), ["canonical", "companion"])

    def test_filename_heading_id_mismatch_fails(self) -> None:
        self.fixture.write("tasks/TASK-0020-WRONG.md", canonical("TASK-0021", "Wrong ID"))
        process, payload = self.fixture.run("validate")
        self.assertNotEqual(process.returncode, 0)
        self.assertTrue(any("does not match heading ID" in item for item in payload["errors"]))

    def test_registry_id_drift_fails(self) -> None:
        registry = self.fixture.worktree / "tasks" / "TASK_REGISTRY.yaml"
        registry.write_text(registry.read_text(encoding="utf-8").replace('id: "TASK-0019"', 'id: "TASK-0099"', 1), encoding="utf-8")
        process, payload = self.fixture.run("validate")
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("tasks/TASK_REGISTRY.yaml drift detected; rebuild from Task Markdown", payload["errors"])

    def test_pending_candidate_has_no_task_id_and_cannot_promote(self) -> None:
        candidate_id = "CANDIDATE-20260827-WORKSPACE-PENDING"
        path = self.fixture.write(f"tasks/candidates/{candidate_id}.md", candidate(candidate_id, "Pending Candidate"))
        self.fixture.refresh_registry(self.fixture.worktree)
        process, payload = self.fixture.run("promote", path.relative_to(self.fixture.worktree).as_posix())
        self.assertNotEqual(process.returncode, 0)
        self.assertTrue(any("not explicitly approved" in item for item in payload["errors"]))
        self.assertFalse(any(item.name.startswith("TASK-0020") for item in (self.fixture.worktree / "tasks").glob("TASK-*.md")))

    def test_approved_candidate_promotes_to_unique_task_and_keeps_provenance(self) -> None:
        candidate_id = "CANDIDATE-20260827-WORKSPACE-APPROVED"
        path = self.fixture.write(f"tasks/candidates/{candidate_id}.md", candidate(candidate_id, "Approved Candidate", decision="Approved", goal="建立独立候选治理流程。"))
        self.fixture.refresh_registry(self.fixture.worktree)
        process, payload = self.fixture.run("promote", path.relative_to(self.fixture.worktree).as_posix())
        self.assertEqual(process.returncode, 0, payload)
        self.assertEqual(payload["task_id"], "TASK-0020")
        promoted = self.fixture.worktree / payload["file"]
        self.assertIn("Candidate provenance", promoted.read_text(encoding="utf-8"))
        self.assertIn("- Status: Migrated", path.read_text(encoding="utf-8"))
        validate_process, validate_payload = self.fixture.run("validate")
        self.assertEqual(validate_process.returncode, 0, validate_payload)

    def test_active_goal_overlap_blocks_without_subtask_decision(self) -> None:
        candidate_id = "CANDIDATE-20260827-WORKSPACE-OVERLAP"
        path = self.fixture.write(f"tasks/candidates/{candidate_id}.md", candidate(candidate_id, "Existing Task", decision="Approved", goal="建立现有任务治理。"))
        self.fixture.refresh_registry(self.fixture.worktree)
        process, payload = self.fixture.run("promote", path.relative_to(self.fixture.worktree).as_posix())
        self.assertNotEqual(process.returncode, 0)
        self.assertTrue(any("overlap requires explicit subtask decision" in item for item in payload["errors"]))

    def test_concurrent_next_requests_receive_different_ids(self) -> None:
        command = [sys.executable, str(MODULE_PATH), "--root", str(self.fixture.worktree), "next", "--lock-timeout", "5"]
        first = subprocess.Popen(command, text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        second = subprocess.Popen(command, text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        first_out, _ = first.communicate(timeout=15)
        second_out, _ = second.communicate(timeout=15)
        first_payload = json.loads(first_out.strip().splitlines()[-1])
        second_payload = json.loads(second_out.strip().splitlines()[-1])
        self.assertEqual(first.returncode, 0, first_payload)
        self.assertEqual(second.returncode, 0, second_payload)
        self.assertEqual({first_payload["task_id"], second_payload["task_id"]}, {"TASK-0020", "TASK-0021"})

    def test_lock_conflict_fails_closed(self) -> None:
        common = Path(self.fixture.git(self.fixture.worktree, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
        lock = common / "ai-workspace-task-allocator" / "allocation.lock"
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text("busy\n", encoding="utf-8")
        try:
            process, payload = self.fixture.run("next", "--lock-timeout", "0.1")
        finally:
            lock.unlink(missing_ok=True)
        self.assertNotEqual(process.returncode, 0)
        self.assertTrue(any("lock is busy" in item for item in payload["errors"]))

    def test_release_returns_unused_id_to_allocator(self) -> None:
        first_process, first = self.fixture.run("next")
        self.assertEqual(first_process.returncode, 0, first)
        release_process, release = self.fixture.run(
            "release", "--id", first["task_id"], "--token", first["reservation_token"]
        )
        self.assertEqual(release_process.returncode, 0, release)
        second_process, second = self.fixture.run("next")
        self.assertEqual(second_process.returncode, 0, second)
        self.assertEqual(first["task_id"], second["task_id"])
        self.fixture.run("release", "--id", second["task_id"], "--token", second["reservation_token"])

    def test_incomplete_directory_detected_as_registry_drift(self) -> None:
        (self.fixture.worktree / "tasks" / "TASK-0019-EXISTING.md").unlink()
        process, payload = self.fixture.run("validate")
        self.assertNotEqual(process.returncode, 0)
        self.assertTrue(any("Registry drift" in item or "registry" in item.lower() for item in payload["errors"]))

    def test_parse_error_fails_closed(self) -> None:
        path = self.fixture.worktree / "tasks" / "TASK-0020-BROKEN.md"
        path.write_bytes(b"# TASK-0020 \x00 broken")
        process, payload = self.fixture.run("validate")
        self.assertNotEqual(process.returncode, 0)
        self.assertTrue(any("NUL byte" in item for item in payload["errors"]))

    def test_non_latest_branch_fails_closed(self) -> None:
        self.fixture.write_source("remote-change.txt", "new main state\n")
        self.fixture.git(self.fixture.source, "add", "remote-change.txt")
        self.fixture.git(self.fixture.source, "commit", "-m", "test: advance main")
        self.fixture.git(self.fixture.source, "push", "origin", "main")
        process, payload = self.fixture.run("validate")
        self.assertNotEqual(process.returncode, 0)
        self.assertTrue(any("does not contain latest origin/main" in item for item in payload["errors"]))

    def test_candidate_command_does_not_allocate_task_id(self) -> None:
        process, payload = self.fixture.run(
            "candidate", "--title", "New Direction", "--project-key", "WORKSPACE", "--slug", "NEW-DIRECTION",
            "--source", "test", "--goal", "记录尚未批准的新方向。",
        )
        self.assertEqual(process.returncode, 0, payload)
        self.assertFalse(payload["task_id_allocated"])
        self.assertTrue((self.fixture.worktree / payload["file"]).exists())


if __name__ == "__main__":
    unittest.main()
