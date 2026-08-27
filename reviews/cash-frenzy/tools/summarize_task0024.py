from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


VALUE_KEYS = {"value", "identity", "captured_at", "error"}


def iter_records(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def collect_value(node: Any, path: str, fields: Counter[tuple[str, str]], truncations: Counter[str]) -> None:
    if not isinstance(node, dict):
        return
    value_type = str(node.get("type", "unknown"))
    fields[(path, value_type)] += 1
    if node.get("truncated"):
        truncations[str(node.get("reason", "unspecified"))] += 1
    if value_type != "table":
        return
    for field in node.get("fields", []):
        if not isinstance(field, dict):
            continue
        key = str(field.get("key", "<missing-key>"))
        collect_value(field.get("value"), f"{path}.{key}", fields, truncations)


def summarize(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    kinds: Counter[str] = Counter()
    message_types: Counter[str] = Counter()
    fields: Counter[tuple[str, str]] = Counter()
    truncations: Counter[str] = Counter()
    scope_threads: Counter[str] = Counter()
    record_count = 0

    for record in records:
        record_count += 1
        kind = str(record.get("kind", "unknown"))
        kinds[kind] += 1
        if "messageType" in record:
            message_types[str(record["messageType"])] += 1
        if kind in {"probe-truncated", "host-truncated"} or record.get("truncated"):
            truncations[str(record.get("reason", "unspecified"))] += 1
        if kind == "inbound-scope-summary":
            scope_threads[str(record.get("threadId", "unknown"))] += 1
        if kind != "lua-pcall-args":
            continue
        for argument in record.get("arguments", []):
            if not isinstance(argument, dict):
                continue
            index = argument.get("index", "?")
            collect_value(argument.get("value"), f"arg[{index}]", fields, truncations)

    return {
        "schema_version": "task0024-structure-summary-v1",
        "record_count": record_count,
        "event_kinds": dict(sorted(kinds.items())),
        "message_types": dict(sorted(message_types.items())),
        "scope_thread_count": len(scope_threads),
        "field_paths": [
            {"path": path, "type": value_type, "count": count}
            for (path, value_type), count in sorted(fields.items())
        ],
        "truncations": dict(sorted(truncations.items())),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a value-free TASK-0024 structure summary")
    parser.add_argument("events", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = summarize(iter_records(args.events))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
