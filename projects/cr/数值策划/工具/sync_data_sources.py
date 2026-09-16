"""将外部 CR 数值资料增量同步为仓库快照。

默认仅预览，不写文件。使用 --apply 才会复制新增或内容变化的文件。
脚本不会删除目标目录中多出的文件，避免误删历史资料。
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from cr_tools.common import file_sha256, load_json, repository_root, write_json


@dataclass(frozen=True)
class Source:
    key: str
    label: str
    source_env: str
    source: Path
    destination: Path
    patterns: tuple[str, ...]
    exclude: tuple[str, ...]
    recursive: bool
    authority: str
    notes: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parent / "config" / "data_sources.json",
        help="数据源 JSON 配置路径。",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="实际复制文件；不传时只做 dry-run。",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="只输出每个数据源的小计和最终结果。",
    )
    return parser.parse_args()


def load_sources(config_path: Path, repo_root: Path) -> list[Source]:
    config = load_json(config_path)
    sources: list[Source] = []
    for raw in config.get("sources", []):
        source_env = raw["source_env"]
        source_value = os.environ.get(source_env, "").strip()
        if not source_value:
            raise ValueError(
                f"未配置数据源环境变量 {source_env}。"
                f"请将它设置为“{raw['label']}”在本机的目录。"
            )
        destination = (repo_root / raw["destination"].replace("\\", "/")).resolve()
        try:
            destination.relative_to(repo_root.resolve())
        except ValueError as error:
            raise ValueError(f"目标目录越出仓库：{destination}") from error
        sources.append(
            Source(
                key=raw["key"],
                label=raw["label"],
                source_env=source_env,
                source=Path(source_value).expanduser().resolve(),
                destination=destination,
                patterns=tuple(raw.get("patterns", ["*"])),
                exclude=tuple(raw.get("exclude", [])),
                recursive=bool(raw.get("recursive", False)),
                authority=raw.get("authority", ""),
                notes=raw.get("notes", ""),
            )
        )
    return sources


def matches(path: Path, source: Source) -> bool:
    file_name = path.name.casefold()
    return (
        any(fnmatch.fnmatch(file_name, pattern.casefold()) for pattern in source.patterns)
        and not any(
            fnmatch.fnmatch(file_name, pattern.casefold()) for pattern in source.exclude
        )
    )


def iter_files(source: Source) -> Iterable[Path]:
    if not source.source.is_dir():
        raise FileNotFoundError(f"数据源目录不存在：{source.source}")
    candidates = source.source.rglob("*") if source.recursive else source.source.glob("*")
    for path in sorted(candidates, key=lambda item: str(item).casefold()):
        if path.is_file() and matches(path, source):
            yield path


def needs_copy(source_path: Path, destination_path: Path) -> bool:
    if not destination_path.exists():
        return True
    if source_path.stat().st_size != destination_path.stat().st_size:
        return True
    return file_sha256(source_path) != file_sha256(destination_path)


def main() -> int:
    args = parse_args()
    repo_root = repository_root()
    sources = load_sources(args.config.resolve(), repo_root)
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[{mode}] 仓库：{repo_root}")

    manifest_sources: list[dict[str, object]] = []
    total_seen = total_changed = 0

    for source in sources:
        entries: list[dict[str, object]] = []
        changed = 0
        print(f"\n{source.label}\n  来源：{source.source}\n  目标：{source.destination}")
        for source_path in iter_files(source):
            relative = source_path.relative_to(source.source)
            destination_path = source.destination / relative
            should_copy = needs_copy(source_path, destination_path)
            action = "COPY" if should_copy else "OK"
            if not args.quiet:
                print(f"  {action:4} {relative}")
            if should_copy:
                changed += 1
                if args.apply:
                    destination_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, destination_path)
            hash_path = destination_path if args.apply and destination_path.exists() else source_path
            entries.append(
                {
                    "relative_path": relative.as_posix(),
                    "size_bytes": source_path.stat().st_size,
                    "sha256": file_sha256(hash_path),
                }
            )
        total_seen += len(entries)
        total_changed += changed
        manifest_sources.append(
            {
                "key": source.key,
                "label": source.label,
                "source_ref": f"${{{source.source_env}}}",
                "destination": str(source.destination.relative_to(repo_root)),
                "authority": source.authority,
                "notes": source.notes,
                "file_count": len(entries),
                "changed_count": changed,
                "files": entries,
            }
        )
        print(f"  小计：{len(entries)} 个文件，{changed} 个需更新")

    if args.apply:
        manifest = {
            "schema_version": 1,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "sources": manifest_sources,
        }
        write_json(repo_root / "数值策划" / "知识库" / "同步清单.json", manifest)

    print(f"\n完成：扫描 {total_seen} 个文件，{total_changed} 个需更新。")
    if not args.apply:
        print("当前为 dry-run；确认后加 --apply 执行复制。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
