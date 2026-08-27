from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "workspace_context.py"
SPEC = importlib.util.spec_from_file_location("workspace_context", MODULE_PATH)
assert SPEC and SPEC.loader
wc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wc)


class WorkspaceContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "repo"
        self.root.mkdir()
        self.state_dir = Path(self.temporary.name) / "state"
        (self.root / "tasks").mkdir()
        (self.root / "standards").mkdir()
        (self.root / "bootstrap" / "chatgpt").mkdir(parents=True)
        (self.root / "tasks" / "TASK-0001-Test.md").write_text(
            "# TASK-0001 — Test\n\n- Status: Ready\n", encoding="utf-8"
        )
        (self.root / "standards" / "STYLE.md").write_text(
            "# 行文规范\n\n默认使用完整中文段落，先给出结论，再说明依据和下一步。\n", encoding="utf-8"
        )
        (self.root / "bootstrap" / "chatgpt" / "00_CORE_RULES.md").write_text(
            "# Core Rules\n\nGit 是规则真相源。\n", encoding="utf-8"
        )
        self.git("init", "-b", "main")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Workspace Test")
        self.git("add", ".")
        self.git("commit", "-m", "fixture")
        self.manifest_path = self.root / "LIVE_CONTEXT_MANIFEST.json"
        self.write_manifest()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", *args], cwd=self.root, text=True, capture_output=True, check=True)

    def write_manifest(self, contexts: list[dict] | None = None) -> None:
        if contexts is None:
            contexts = [
                {
                    "context_id": "core-rules",
                    "title": "核心规则",
                    "authority": "git",
                    "scope": "public",
                    "sensitivity": "public",
                    "git_path": "bootstrap/chatgpt/00_CORE_RULES.md",
                    "provider_alias": "workspace-core-rules",
                    "sync_direction": "git-to-provider",
                    "sharing": "company_readable",
                    "include_in_pack": True,
                },
                {
                    "context_id": "current-state",
                    "title": "当前状态",
                    "authority": "git",
                    "scope": "public",
                    "sensitivity": "public",
                    "generator": "git-current-state",
                    "provider_alias": "workspace-current-state",
                    "sync_direction": "git-to-provider",
                    "sharing": "company_readable",
                    "include_in_pack": True,
                },
                {
                    "context_id": "collaboration-notes",
                    "title": "协作与待确认事项",
                    "authority": "feishu",
                    "scope": "public",
                    "sensitivity": "public",
                    "provider_alias": "workspace-collaboration-notes",
                    "sync_direction": "provider-to-candidate",
                    "sharing": "company_editable",
                    "include_in_pack": False,
                },
            ]
        self.manifest_path.write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "context_set_id": "workspace-live-context",
                    "provider_binding": {"type": "feishu-drive-docx", "folder_alias": "workspace-context-hub"},
                    "contexts": contexts,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def args(self, **overrides: object) -> argparse.Namespace:
        values = {
            "root": str(self.root),
            "state_dir": str(self.state_dir),
            "manifest": str(self.manifest_path),
            "provider_snapshot": None,
            "lock_timeout": 0.2,
        }
        values.update(overrides)
        return argparse.Namespace(**values)

    def snapshot(self, contexts: list[dict]) -> Path:
        path = Path(self.temporary.name) / f"snapshot-{len(list(Path(self.temporary.name).glob('snapshot-*')))}.json"
        path.write_text(json.dumps({"contexts": contexts}, ensure_ascii=False), encoding="utf-8")
        return path

    def test_manifest_and_doctor_pass_for_public_sources(self) -> None:
        manifest = wc.load_manifest(self.root, self.manifest_path)
        checks = wc.doctor(self.root, manifest)
        self.assertEqual(checks["manifest"], "ok")
        self.assertEqual(len(checks["sources"]), 2)

    def test_generated_current_state_fingerprint_is_stable_for_same_git_state(self) -> None:
        manifest = wc.load_manifest(self.root, self.manifest_path)
        current = next(item for item in manifest["contexts"] if item["context_id"] == "current-state")
        first = wc.context_fingerprint(self.root, current)
        second = wc.context_fingerprint(self.root, current)
        self.assertEqual(first, second)

    def test_manifest_rejects_path_traversal(self) -> None:
        contexts = [
            {
                "context_id": "bad-path",
                "title": "Bad",
                "authority": "git",
                "scope": "public",
                "sensitivity": "public",
                "git_path": "../secret.md",
                "provider_alias": "bad",
            }
        ]
        self.write_manifest(contexts)
        with self.assertRaisesRegex(ValueError, "escapes root"):
            wc.load_manifest(self.root, self.manifest_path)

    def test_doctor_blocks_secret_assignment(self) -> None:
        path = self.root / "bootstrap" / "chatgpt" / "00_CORE_RULES.md"
        path.write_text('app_secret="super-secret-value"\n', encoding="utf-8")
        manifest = wc.load_manifest(self.root, self.manifest_path)
        with self.assertRaisesRegex(ValueError, "secret scan failed"):
            wc.doctor(self.root, manifest)

    def test_initial_sync_writes_local_pack_and_publish_plan(self) -> None:
        result = wc.cmd_sync(self.args())
        self.assertEqual(result, 0)
        pack = self.state_dir / "LOCAL_CONTEXT_PACK.md"
        plan = json.loads((self.state_dir / "publish-plan.json").read_text(encoding="utf-8"))
        self.assertIn("TASK-0001", pack.read_text(encoding="utf-8"))
        self.assertEqual({item["context_id"] for item in plan["contexts"]}, {"core-rules", "current-state"})

    def test_acknowledged_matching_provider_is_current(self) -> None:
        manifest = wc.load_manifest(self.root, self.manifest_path)
        fingerprint = wc.context_fingerprint(self.root, manifest["contexts"][0])
        wc.cmd_acknowledge(
            self.args(
                context_id="core-rules",
                provider_revision="rev-1",
                provider_fingerprint=fingerprint,
                provider_ref="private-ref",
            )
        )
        snapshot = self.snapshot(
            [{"context_id": "core-rules", "revision": "rev-1", "content_sha256": fingerprint}]
        )
        state = wc.load_state(self.state_dir)
        statuses = wc.compare_status(self.root, manifest, state, wc.load_snapshot(snapshot))
        core = next(item for item in statuses if item["context_id"] == "core-rules")
        self.assertEqual(core["status"], "current")
        self.assertNotIn("private-ref", json.dumps(wc.sanitized_statuses(statuses)))

    def test_two_sided_change_becomes_conflict(self) -> None:
        manifest = wc.load_manifest(self.root, self.manifest_path)
        original = wc.context_fingerprint(self.root, manifest["contexts"][0])
        wc.cmd_acknowledge(
            self.args(context_id="core-rules", provider_revision="rev-1", provider_fingerprint=original, provider_ref=None)
        )
        source = self.root / "bootstrap" / "chatgpt" / "00_CORE_RULES.md"
        source.write_text(source.read_text(encoding="utf-8") + "\nGit side changed.\n", encoding="utf-8")
        snapshot = self.snapshot(
            [{"context_id": "core-rules", "revision": "rev-2", "content": "Provider side changed."}]
        )
        statuses = wc.compare_status(self.root, manifest, wc.load_state(self.state_dir), wc.load_snapshot(snapshot))
        self.assertEqual(next(i for i in statuses if i["context_id"] == "core-rules")["status"], "conflict")

    def test_provider_draft_enters_git_memory_candidate(self) -> None:
        snapshot = self.snapshot(
            [{"context_id": "collaboration-notes", "revision": "rev-2", "content": "策划建议：下一轮先验证同步状态。"}]
        )
        memory_cli = MODULE_PATH.parents[1] / "memory" / "memory_cli.py"
        result = wc.cmd_capture_draft(
            self.args(
                context_id="collaboration-notes",
                provider_snapshot=str(snapshot),
                source_host="generic-agent-pilot",
                source_actor_alias="PilotAgent",
                memory_cli=str(memory_cli),
                memory_root=str(self.root),
                memory_state_dir=str(Path(self.temporary.name) / "memory-state"),
                timeout=20.0,
            )
        )
        self.assertEqual(result, 0)
        candidates = list((self.root / "memory" / "inbox").glob("MEM-*.md"))
        self.assertEqual(len(candidates), 1)
        self.assertIn("Candidate only", candidates[0].read_text(encoding="utf-8"))

    def test_offline_sync_keeps_local_pack_and_marks_provider_unavailable(self) -> None:
        wc.cmd_sync(self.args())
        payload = json.loads((self.state_dir / "last-sync.json").read_text(encoding="utf-8"))
        notes = next(item for item in payload["contexts"] if item["context_id"] == "collaboration-notes")
        self.assertEqual(notes["status"], "unavailable")
        self.assertTrue((self.state_dir / "LOCAL_CONTEXT_PACK.md").exists())

    def test_lock_refuses_second_writer(self) -> None:
        with wc.FileLock(self.state_dir, timeout_seconds=0.1):
            with self.assertRaisesRegex(TimeoutError, "another Workspace Sync writer"):
                with wc.FileLock(self.state_dir, timeout_seconds=0.1):
                    pass

    def test_transaction_rolls_back_fault(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / ".allow-fault-injection").touch()
        target = self.state_dir / "state.json"
        target.write_text("before\n", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "test fault"):
            wc.transaction_write(self.state_dir, [(target, "after\n")], "after-write-1")
        self.assertEqual(target.read_text(encoding="utf-8"), "before\n")

    def test_watch_mode_requires_explicit_approval(self) -> None:
        with self.assertRaisesRegex(ValueError, "explicit"):
            wc.cmd_set_mode(self.args(mode="WATCH", user_approved=False))
        self.assertEqual(wc.cmd_set_mode(self.args(mode="ON_DEMAND", user_approved=False)), 0)
        self.assertEqual(wc.load_state(self.state_dir)["mode"], "ON_DEMAND")

    def test_conflict_resolution_records_decision_without_overwrite(self) -> None:
        manifest = wc.load_manifest(self.root, self.manifest_path)
        original = wc.context_fingerprint(self.root, manifest["contexts"][0])
        wc.cmd_acknowledge(
            self.args(context_id="core-rules", provider_revision="rev-1", provider_fingerprint=original, provider_ref=None)
        )
        source = self.root / "bootstrap" / "chatgpt" / "00_CORE_RULES.md"
        source.write_text("# Changed in Git\n", encoding="utf-8")
        snapshot = self.snapshot(
            [{"context_id": "core-rules", "revision": "rev-2", "content": "Changed in provider"}]
        )
        result = wc.cmd_resolve_conflict(
            self.args(
                context_id="core-rules",
                provider_snapshot=str(snapshot),
                decision="keep-git",
                decision_reference="TASK-0021-PILOT",
            )
        )
        self.assertEqual(result, 0)
        self.assertEqual(len(list((self.state_dir / "conflict-resolutions").glob("*.json"))), 1)
        self.assertEqual(source.read_text(encoding="utf-8"), "# Changed in Git\n")


if __name__ == "__main__":
    unittest.main()
