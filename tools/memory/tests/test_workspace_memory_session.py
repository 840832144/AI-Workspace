from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]


class WorkspaceMemorySessionTests(unittest.TestCase):
    def test_public_seed_read_view_is_unique_and_safe(self) -> None:
        index = json.loads((ROOT / "memory/index/memory-index.json").read_text(encoding="utf-8"))
        entries = [
            item for item in index["entries"]
            if item.get("canonical_destination") == "memory/context/WORKSPACE.md"
            and item.get("workspace_status") != "Superseded"
        ]
        self.assertEqual(3, len(entries))
        self.assertEqual(3, len({item["memory_key"] for item in entries}))
        self.assertEqual(3, len({item["source_reference"] for item in entries}))
        self.assertTrue(all(item["scope"] == "public" for item in entries))

        view = (ROOT / "memory/context/WORKSPACE.md").read_text(encoding="utf-8")
        for key in (
            "workspace.git-memory-truth",
            "research.cash-frenzy.task-0024",
            "governance.task-0023-roadmap-writing",
        ):
            self.assertEqual(1, view.count(f"### `{key}`"))
        self.assertIn("F3 strengthened，F4 未证明", view)
        self.assertIn("不得在同一 Task 重复进入已按 Gate 停止", view)
        self.assertNotIn("F4 已证明", view)

    def test_new_chat_bootstrap_is_git_live_first(self) -> None:
        bootstrap = (ROOT / "bootstrap/chatgpt/03_NEW_CHAT_BOOTSTRAP.md").read_text(encoding="utf-8")
        core_position = bootstrap.index("00_CORE_RULES.md")
        memory_position = bootstrap.index("memory/context/WORKSPACE.md")
        evidence_position = bootstrap.index("最新 Task、Review、Status、Handoff")
        fallback_position = bootstrap.index("只有 Git unavailable")
        self.assertLess(core_position, memory_position)
        self.assertLess(memory_position, evidence_position)
        self.assertLess(evidence_position, fallback_position)
        self.assertIn("snapshot may be stale", bootstrap)

    def test_source_pack_contains_ordered_workspace_memory_snapshot(self) -> None:
        pack = (ROOT / "bootstrap/chatgpt/generated/PROJECT_SOURCE_PACK.md").read_text(encoding="utf-8")
        self.assertLess(pack.index("<!-- SOURCE: 00_CORE_RULES.md -->"), pack.index("<!-- SOURCE: 01_SYSTEM_CONTEXT.md -->"))
        self.assertLess(pack.index("<!-- SOURCE: 01_SYSTEM_CONTEXT.md -->"), pack.index("<!-- SOURCE: PLANNER_WRITING_STYLE.md -->"))
        self.assertLess(pack.index("<!-- SOURCE: PLANNER_WRITING_STYLE.md -->"), pack.index("<!-- SOURCE: WORKSPACE.md -->"))
        self.assertIn("Project Source Pack 是离线快照", pack)


if __name__ == "__main__":
    unittest.main(verbosity=2)
