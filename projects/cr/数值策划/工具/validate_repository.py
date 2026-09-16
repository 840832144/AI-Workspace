"""校验 CR 数值资源库的结构、Python 代码和知识库产物。"""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path

from cr_tools.common import file_sha256, repository_root


LOCAL_ONLY_DIR_NAMES = {
    ".svn",
    ".venv",
    ".local",
    ".codex_tmp",
    ".codex_tmp_model_read",
    "outputs",
    "__pycache__",
}


def is_local_only(path: Path, root: Path) -> bool:
    """Return whether a path belongs to ignored machine-local runtime state."""

    return any(
        part in LOCAL_ONLY_DIR_NAMES for part in path.relative_to(root).parts
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=repository_root())
    parser.add_argument("--verify-hashes", action="store_true", help="仅在明确需要时核对历史清单哈希；默认只检查结构、大小与目录一致性。")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    required = [
        "README.md",
        "AGENTS.md",
        ".trae/rules/numerical-design.md",
        ".agents/skills/cr-numerical-design/SKILL.md",
        "数值策划/数值文档/00_规范/数值方案模板.md",
        "数值策划/工具/config/data_sources.json",
        "数值策划/知识库/工作簿目录.csv",
        "数值策划/知识库/工作簿结构.json",
        "数值策划/知识库/同步清单.json",
    ]
    for relative in required:
        if not (root / relative).exists():
            errors.append(f"缺少必需文件：{relative}")

    retired_snapshot = root / "数值策划" / "数据源" / "程序配置导出快照"
    if retired_snapshot.exists():
        errors.append("程序配置本地快照结构已退役，不应重新创建。")

    temporary_files = [
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file()
        and not is_local_only(path, root)
        and (
            path.name.startswith("~$")
            or path.suffix.lower() in {".pyc", ".log", ".tmp"}
            or "__pycache__" in path.parts
        )
    ]
    for path in temporary_files:
        errors.append(f"不应提交临时文件：{path}")

    for path in root.rglob("*.py"):
        if is_local_only(path, root):
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError, UnicodeError) as error:
            errors.append(f"Python 语法/编码错误：{path.relative_to(root)}：{error}")

    skill_paths = sorted((root / ".agents" / "skills").glob("*/SKILL.md"))
    for skill_path in skill_paths:
        text = skill_path.read_text(encoding="utf-8")
        frontmatter = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
        if not frontmatter:
            errors.append(
                f"Skill 缺少合法 YAML frontmatter：{skill_path.relative_to(root)}"
            )
        else:
            keys = {
                line.split(":", 1)[0].strip()
                for line in frontmatter.group(1).splitlines()
                if ":" in line
            }
            if keys != {"name", "description"}:
                errors.append(
                    "Skill frontmatter 只能包含 name 和 description："
                    f"{skill_path.relative_to(root)}"
                )
            name_match = re.search(
                r"^name:\s*([a-z0-9-]+)\s*$",
                frontmatter.group(1),
                flags=re.MULTILINE,
            )
            description_match = re.search(
                r"^description:\s*(.+?)\s*$",
                frontmatter.group(1),
                flags=re.MULTILINE,
            )
            if not name_match or name_match.group(1) != skill_path.parent.name:
                errors.append(
                    f"Skill 名称与目录不一致：{skill_path.relative_to(root)}"
                )
            if not description_match or "TODO" in description_match.group(1):
                errors.append(
                    f"Skill description 无效：{skill_path.relative_to(root)}"
                )
            if "TODO" in text:
                errors.append(f"Skill 仍含 TODO：{skill_path.relative_to(root)}")

        interface_path = skill_path.parent / "agents" / "openai.yaml"
        if not interface_path.exists():
            errors.append(
                f"Skill 缺少 agents/openai.yaml：{skill_path.parent.relative_to(root)}"
            )
        else:
            interface_text = interface_path.read_text(encoding="utf-8")
            skill_name = skill_path.parent.name
            if f"${skill_name}" not in interface_text:
                errors.append(
                    f"Skill 默认提示未引用自身名称：{interface_path.relative_to(root)}"
                )

    structure_path = root / "数值策划" / "知识库" / "工作簿结构.json"
    structure_count = 0
    structure_paths: set[str] = set()
    if structure_path.exists():
        try:
            structure = json.loads(structure_path.read_text(encoding="utf-8"))
            structure_count = int(structure.get("workbook_count", 0))
            structure_paths = {
                str(item.get("relative_path", "")).replace("\\", "/")
                for item in structure.get("workbooks", [])
            }
            if structure.get("workbook_count", 0) == 0:
                warnings.append("知识库目录中没有工作簿。")
            failed = [
                item.get("relative_path", "")
                for item in structure.get("workbooks", [])
                if item.get("status") != "ok"
            ]
            for item in failed[:20]:
                errors.append(f"工作簿目录读取失败：{item}")
            if len(failed) > 20:
                errors.append(f"另有 {len(failed) - 20} 个工作簿读取失败。")
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"工作簿结构 JSON 无效：{error}")

    manifest_path = root / "数值策划" / "知识库" / "同步清单.json"
    manifest_count = 0
    manifest_destinations: list[str] = []
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for source in manifest.get("sources", []):
                destination = root / source["destination"].replace("\\", "/")
                manifest_destinations.append(
                    str(source["destination"]).replace("\\", "/").rstrip("/") + "/"
                )
                for entry in source.get("files", []):
                    manifest_count += 1
                    path = destination / entry["relative_path"].replace("\\", "/")
                    if not path.is_file():
                        errors.append(f"同步文件缺失：{path.relative_to(root)}")
                        continue
                    if path.stat().st_size != entry["size_bytes"]:
                        errors.append(f"同步文件大小不一致：{path.relative_to(root)}")
                        continue
                    if args.verify_hashes and file_sha256(path) != entry["sha256"]:
                        errors.append(f"同步文件哈希不一致：{path.relative_to(root)}")
            synced_structure_count = sum(
                1
                for path in structure_paths
                if any(path.startswith(prefix) for prefix in manifest_destinations)
            )
            if structure_count and manifest_count != synced_structure_count:
                errors.append(
                    "数据源目录与同步清单数量不一致："
                    f"{synced_structure_count} != {manifest_count}"
                )
        except (KeyError, OSError, TypeError, json.JSONDecodeError) as error:
            errors.append(f"同步清单 JSON 无效：{error}")

    for message in warnings:
        print(f"WARN  {message}")
    for message in errors:
        print(f"ERROR {message}")
    print(f"校验完成：{len(errors)} 个错误，{len(warnings)} 个警告。")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
