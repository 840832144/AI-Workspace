from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


probe = load_module("task0024_inbound_probe", ROOT / "tools" / "task0024_inbound_probe.py")
summary = load_module("summarize_task0024", ROOT / "tools" / "summarize_task0024.py")


class Task0024InboundProbeTests(unittest.TestCase):
    def test_contract_limits_are_embedded_in_runtime_script(self) -> None:
        source = probe.build_javascript("lua")
        self.assertIn("const MAX_DEPTH = 4;", source)
        self.assertIn("const MAX_ELEMENTS = 64;", source)
        self.assertIn("const MAX_MESSAGE_BYTES = 65536;", source)
        self.assertIn("onUIThreadReceiveMessage", source)
        self.assertIn("lua_pcall", source)
        self.assertIn("scope === undefined || scope.depth <= 0", source)

    def test_host_budget_fails_closed(self) -> None:
        payload = {"kind": "lua-pcall-args", "blob": "x" * probe.MAX_MESSAGE_BYTES}
        bounded = probe.bounded_record(payload)
        self.assertEqual("host-truncated", bounded["kind"])
        self.assertEqual("host-message-budget", bounded["reason"])
        self.assertNotIn("blob", bounded)

    def test_summary_keeps_paths_and_drops_values(self) -> None:
        records = [
            {
                "kind": "lua-pcall-args",
                "messageType": 3,
                "arguments": [
                    {
                        "index": 1,
                        "value": {
                            "type": "table",
                            "identity": "0xsecret",
                            "fields": [
                                {"key": "result", "value": {"type": "string", "value": "SECRET_RESULT"}},
                                {"key": "win", "value": {"type": "number", "value": 987654321}},
                                {
                                    "key": "feature",
                                    "value": {"type": "table", "fields": [], "truncated": True,
                                              "reason": "depth-budget"},
                                },
                            ],
                        },
                    }
                ],
            }
        ]
        result = summary.summarize(records)
        rendered = json.dumps(result, ensure_ascii=False)
        self.assertIn("arg[1].result", rendered)
        self.assertIn("arg[1].win", rendered)
        self.assertIn("arg[1].feature", rendered)
        self.assertNotIn("SECRET_RESULT", rendered)
        self.assertNotIn("987654321", rendered)
        self.assertNotIn("0xsecret", rendered)
        self.assertEqual(1, result["truncations"]["depth-budget"])


if __name__ == "__main__":
    unittest.main()
