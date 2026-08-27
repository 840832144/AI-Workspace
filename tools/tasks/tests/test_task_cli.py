from __future__ import annotations

import importlib.util
import json
import os
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


def canonical(task_id: str, title: str, *, status: str = "Ready", project: str | None = "WORKSPACE", goal: str = "建立可验证的治理能力。") -> str:
    project_line = f"- Project key: {project}\n" if project is not None else ""
    return f"""# {task_id} — {title}

- Status: {status}
{project_line}- Owner: User / ChatGPT
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

    @staticmethod
    def run_at(root: Path, *args: str, env: dict[str, str] | None = None) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        process_env = os.environ.copy()
        if env:
            process_env.update(env)
        process = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--root", str(root), *args],
            text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=process_env,
        )
        lines = [line for line in process.stdout.splitlines() if line.strip()]
        payload = json.loads(lines[-1]) if lines else {}
        return process, payload

    def run(self, *args: str, env: dict[str, str] | None = None) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        return self.run_at(self.worktree, *args, env=env)

    def independent_allocator(self, name: str) -> Path:
        clone = self.base / f"{name}-clone"
        worktree = self.base / f"{name}-worktree"
        self.git(self.base, "clone", "--branch", "main", str(self.remote), str(clone))
        self.git(clone, "config", "user.name", "Task Tests")
        self.git(clone, "config", "user.email", "task-tests@example.invalid")
        self.git(clone, "worktree", "add", "-b", f"test/{name}", str(worktree), "main")
        return worktree


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

    def test_next_writer_gate_rejects_main_and_ordinary_checkout(self) -> None:
        main_process, main_payload = self.fixture.run_at(self.fixture.source, "next")
        self.assertNotEqual(main_process.returncode, 0)
        self.assertTrue(any("non-main branch" in item for item in main_payload["errors"]))

        ordinary = self.fixture.base / "ordinary-clone"
        self.fixture.git(
            self.fixture.base, "clone", "--branch", "main", str(self.fixture.remote), str(ordinary)
        )
        self.fixture.git(ordinary, "checkout", "-b", "test/ordinary")
        ordinary_process, ordinary_payload = self.fixture.run_at(ordinary, "next")
        self.assertNotEqual(ordinary_process.returncode, 0)
        self.assertTrue(
            any("independent linked worktree" in item for item in ordinary_payload["errors"])
        )

    def test_cross_clone_concurrent_next_uses_remote_cas(self) -> None:
        first_root = self.fixture.independent_allocator("host-a")
        second_root = self.fixture.independent_allocator("host-b")
        commands = [
            [sys.executable, str(MODULE_PATH), "--root", str(root), "next"]
            for root in (first_root, second_root)
        ]
        processes = [
            subprocess.Popen(command, text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for command in commands
        ]
        payloads: list[dict[str, object]] = []
        for process in processes:
            stdout, _ = process.communicate(timeout=20)
            payload = json.loads(stdout.strip().splitlines()[-1])
            self.assertEqual(process.returncode, 0, payload)
            payloads.append(payload)
        self.assertEqual({item["task_id"] for item in payloads}, {"TASK-0020", "TASK-0021"})

    def test_remote_reservation_does_not_publish_requesting_branch_graph(self) -> None:
        sentinel_name = "unreviewed-sentinel.txt"
        self.fixture.write(sentinel_name, "must remain local to the requesting branch\n")
        self.fixture.git(self.fixture.worktree, "add", sentinel_name)
        self.fixture.git(
            self.fixture.worktree, "commit", "-m", "test: add unpushed sentinel"
        )
        sentinel_oid = self.fixture.git(
            self.fixture.worktree, "rev-parse", "HEAD"
        ).stdout.strip()
        origin_main_oid = self.fixture.git(
            self.fixture.worktree, "rev-parse", "origin/main"
        ).stdout.strip()

        process, payload = self.fixture.run("next", "--purpose", "sentinel-isolation")
        self.assertEqual(process.returncode, 0, payload)
        task_id = str(payload["task_id"])
        remote_ref = f"refs/heads/task-reservations/{task_id}"

        observer = self.fixture.base / "sentinel-observer"
        self.fixture.git(
            self.fixture.base, "clone", "--branch", "main", str(self.fixture.remote), str(observer)
        )
        observer_ref = "refs/remotes/origin/sentinel-reservation"
        self.fixture.git(observer, "fetch", "origin", f"{remote_ref}:{observer_ref}")
        reservation_parent = self.fixture.git(
            observer, "rev-parse", f"{observer_ref}^"
        ).stdout.strip()
        reservation_tree = self.fixture.git(
            observer, "rev-parse", f"{observer_ref}^{{tree}}"
        ).stdout.strip()
        main_tree = self.fixture.git(
            observer, "rev-parse", f"{origin_main_oid}^{{tree}}"
        ).stdout.strip()
        self.assertEqual(reservation_parent, origin_main_oid)
        self.assertEqual(reservation_tree, main_tree)
        self.assertNotEqual(
            self.fixture.git(
                observer, "cat-file", "-e", f"{observer_ref}:{sentinel_name}", check=False
            ).returncode,
            0,
        )
        self.assertNotEqual(
            self.fixture.git(observer, "cat-file", "-e", sentinel_oid, check=False).returncode,
            0,
        )
        self.assertNotEqual(
            self.fixture.git(
                observer, "merge-base", "--is-ancestor", sentinel_oid, observer_ref, check=False
            ).returncode,
            0,
        )

        common = Path(
            self.fixture.git(
                self.fixture.worktree, "rev-parse", "--path-format=absolute", "--git-common-dir"
            ).stdout.strip()
        )
        metadata = json.loads(
            (task_cli.reservation_dir(common) / f"{task_id}.json").read_text(encoding="utf-8")
        )
        self.assertEqual(metadata["head"], sentinel_oid)
        self.assertEqual(metadata["base_ref"], "origin/main")
        self.assertEqual(metadata["base_oid"], origin_main_oid)

        release_process, released = self.fixture.run(
            "release", "--id", task_id, "--token", str(payload["reservation_token"])
        )
        self.assertEqual(release_process.returncode, 0, released)

    def test_promote_reservation_blocks_next_until_main_and_finalize(self) -> None:
        candidate_id = "CANDIDATE-20260827-WORKSPACE-LIFECYCLE"
        path = self.fixture.write(
            f"tasks/candidates/{candidate_id}.md",
            candidate(candidate_id, "Lifecycle Candidate", decision="Approved"),
        )
        self.fixture.refresh_registry(self.fixture.worktree)
        promote_process, promoted = self.fixture.run(
            "promote", path.relative_to(self.fixture.worktree).as_posix()
        )
        self.assertEqual(promote_process.returncode, 0, promoted)
        self.assertEqual(promoted["task_id"], "TASK-0020")
        early_release, early_payload = self.fixture.run(
            "release",
            "--id", promoted["task_id"],
            "--token", promoted["reservation_token"],
        )
        self.assertNotEqual(early_release.returncode, 0)
        self.assertTrue(any("use finalize" in item for item in early_payload["errors"]))

        other_root = self.fixture.independent_allocator("before-merge")
        next_process, next_payload = self.fixture.run_at(other_root, "next")
        self.assertEqual(next_process.returncode, 0, next_payload)
        self.assertEqual(next_payload["task_id"], "TASK-0021")

        self.fixture.git(self.fixture.worktree, "add", "tasks")
        self.fixture.git(self.fixture.worktree, "commit", "-m", "test: promote task")
        self.fixture.git(self.fixture.source, "merge", "--ff-only", "test/task")
        self.fixture.git(self.fixture.source, "push", "origin", "main")
        finalize_process, finalized = self.fixture.run(
            "finalize",
            "--id", promoted["task_id"],
            "--token", promoted["reservation_token"],
        )
        self.assertEqual(finalize_process.returncode, 0, finalized)
        self.assertEqual(finalized["status"], "finalized")

    def test_fault_after_remote_reservation_recovers_without_leak(self) -> None:
        (self.fixture.worktree / ".task-test-allow-faults").write_text("test only\n", encoding="utf-8")
        process, payload = self.fixture.run(
            "next", env={"AI_WORKSPACE_TASK_FAULT_INJECTION": "after-remote-reservation"}
        )
        self.assertNotEqual(process.returncode, 0)
        self.assertTrue(any("injected failure" in item for item in payload["errors"]))
        remote = task_cli.remote_reservations(self.fixture.worktree)
        self.assertEqual(remote, {})
        common = Path(
            self.fixture.git(
                self.fixture.worktree, "rev-parse", "--path-format=absolute", "--git-common-dir"
            ).stdout.strip()
        )
        self.assertEqual(task_cli.reserved_ids(common), set())

    def test_concurrent_promote_across_clones_allocates_distinct_ids(self) -> None:
        first_id = "CANDIDATE-20260827-WORKSPACE-FIRST"
        second_id = "CANDIDATE-20260827-WORKSPACE-SECOND"
        self.fixture.write_source(
            f"tasks/candidates/{first_id}.md", candidate(first_id, "First Promotion", decision="Approved")
        )
        self.fixture.write_source(
            f"tasks/candidates/{second_id}.md", candidate(second_id, "Second Promotion", decision="Approved")
        )
        self.fixture.refresh_registry(self.fixture.source)
        self.fixture.git(self.fixture.source, "add", "tasks")
        self.fixture.git(self.fixture.source, "commit", "-m", "test: add promotion candidates")
        self.fixture.git(self.fixture.source, "push", "origin", "main")
        roots = [
            self.fixture.independent_allocator("promote-a"),
            self.fixture.independent_allocator("promote-b"),
        ]
        candidate_paths = [
            f"tasks/candidates/{first_id}.md",
            f"tasks/candidates/{second_id}.md",
        ]
        processes = [
            subprocess.Popen(
                [sys.executable, str(MODULE_PATH), "--root", str(root), "promote", candidate_path],
                text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            for root, candidate_path in zip(roots, candidate_paths)
        ]
        allocated: set[str] = set()
        for process in processes:
            stdout, _ = process.communicate(timeout=25)
            payload = json.loads(stdout.strip().splitlines()[-1])
            self.assertEqual(process.returncode, 0, payload)
            allocated.add(str(payload["task_id"]))
        self.assertEqual(allocated, {"TASK-0020", "TASK-0021"})

    def test_project_key_is_required_validated_and_grandfathered(self) -> None:
        missing = self.fixture.write(
            "tasks/TASK-0020-MISSING-PROJECT.md",
            canonical("TASK-0020", "Missing Project", project=None),
        )
        result = task_cli.scan_repository(self.fixture.worktree)
        self.assertTrue(any("missing '- Project key:'" in item for item in result.errors))
        missing.unlink()

        illegal = self.fixture.write(
            "tasks/TASK-0020-ILLEGAL-PROJECT.md",
            canonical("TASK-0020", "Illegal Project", project="bad key"),
        )
        result = task_cli.scan_repository(self.fixture.worktree)
        self.assertTrue(any("Project key must use uppercase" in item for item in result.errors))
        illegal.unlink()

        self.fixture.write(
            "tasks/TASK-0014-GRANDFATHERED.md",
            canonical("TASK-0014", "Grandfathered", project=None),
        )
        result = task_cli.scan_repository(self.fixture.worktree)
        self.assertFalse(result.errors, result.errors)
        record = next(item for item in result.canonical if item.id == "TASK-0014")
        self.assertEqual(record.project_key, "WORKSPACE")
        self.assertTrue(any("grandfather map" in item for item in result.warnings))

    def test_draft_task_participates_in_candidate_overlap(self) -> None:
        existing = self.fixture.worktree / "tasks" / "TASK-0019-EXISTING.md"
        existing.write_text(
            canonical("TASK-0019", "Existing Task", status="Draft", goal="建立现有任务治理。"),
            encoding="utf-8",
        )
        candidate_id = "CANDIDATE-20260827-WORKSPACE-DRAFT-OVERLAP"
        path = self.fixture.write(
            f"tasks/candidates/{candidate_id}.md",
            candidate(candidate_id, "Existing Task", decision="Approved", goal="建立现有任务治理。"),
        )
        self.fixture.refresh_registry(self.fixture.worktree)
        process, payload = self.fixture.run("promote", path.relative_to(self.fixture.worktree).as_posix())
        self.assertNotEqual(process.returncode, 0)
        self.assertTrue(any("overlap requires explicit subtask" in item for item in payload["errors"]))

    def test_companion_requires_explicit_kind_and_valid_matching_target(self) -> None:
        implicit = self.fixture.write(
            "tasks/TASK-0020-IMPLICIT.md",
            """# TASK-0020 Companion\n\n- Status: Ready\n- Canonical task: `tasks/TASK-0019-EXISTING.md`\n""",
        )
        result = task_cli.scan_repository(self.fixture.worktree)
        self.assertTrue(any("canonical heading" in item for item in result.errors))
        implicit.unlink()

        nonexistent = self.fixture.write(
            "tasks/TASK-0020-NONEXISTENT.md",
            """# TASK-0020 Companion\n\n- Kind: companion\n- Status: Ready\n- Canonical task: `tasks/TASK-0020-NOPE.md`\n""",
        )
        result = task_cli.scan_repository(self.fixture.worktree)
        self.assertTrue(any("does not resolve" in item for item in result.errors))
        nonexistent.unlink()

        mismatch = self.fixture.write(
            "tasks/TASK-0020-MISMATCH.md",
            """# TASK-0020 Companion\n\n- Kind: companion\n- Status: Ready\n- Canonical task: `tasks/TASK-0019-EXISTING.md`\n""",
        )
        result = task_cli.scan_repository(self.fixture.worktree)
        self.assertTrue(any("does not match canonical ID" in item for item in result.errors))
        mismatch.unlink()

        malformed = self.fixture.write(
            "tasks/TASK-0020-MALFORMED.md",
            """# TASK-0020 Malformed\n\n- Kind: canonical\n- Status: Ready\n- Project key: WORKSPACE\n""",
        )
        result = task_cli.scan_repository(self.fixture.worktree)
        self.assertTrue(any("canonical heading" in item for item in result.errors))
        malformed.unlink()


if __name__ == "__main__":
    unittest.main()
