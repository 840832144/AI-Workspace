"""扫描仓库中的 XLSX，生成面向人和 AI 的结构化知识目录。"""

from __future__ import annotations

import argparse
import csv
import posixpath
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree

from cr_tools.common import file_sha256, repository_root, write_json

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CELL_REF_RE = re.compile(r"([A-Z]+)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=repository_root(),
        help="CR 项目目录（AI-Workspace/projects/cr），不依赖当前工作目录。",
    )
    parser.add_argument(
        "--max-header-values",
        type=int,
        default=12,
        help="每个 Sheet 最多保留多少个表头预览值。",
    )
    parser.add_argument("--with-hashes", action="store_true", help="仅在明确需要时生成文件哈希；默认跳过。")
    return parser.parse_args()


def column_number(cell_reference: str) -> int:
    match = CELL_REF_RE.match(cell_reference)
    if not match:
        return 0
    value = 0
    for char in match.group(1):
        value = value * 26 + ord(char) - ord("A") + 1
    return value


def read_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        with archive.open("xl/sharedStrings.xml") as stream:
            root = ElementTree.parse(stream).getroot()
    except KeyError:
        return []
    values: list[str] = []
    for item in root.findall(f"{{{MAIN_NS}}}si"):
        values.append("".join(node.text or "" for node in item.iter(f"{{{MAIN_NS}}}t")))
    return values


def workbook_sheets(archive: zipfile.ZipFile) -> list[tuple[str, str]]:
    with archive.open("xl/workbook.xml") as stream:
        workbook = ElementTree.parse(stream).getroot()
    with archive.open("xl/_rels/workbook.xml.rels") as stream:
        relationships = ElementTree.parse(stream).getroot()
    relation_targets = {
        relation.attrib["Id"]: relation.attrib["Target"]
        for relation in relationships.findall(f"{{{PACKAGE_REL_NS}}}Relationship")
    }
    result: list[tuple[str, str]] = []
    for sheet in workbook.findall(f".//{{{MAIN_NS}}}sheet"):
        relation_id = sheet.attrib.get(f"{{{REL_NS}}}id", "")
        target = relation_targets.get(relation_id, "")
        if target.startswith("/"):
            archive_path = target.lstrip("/")
        else:
            archive_path = posixpath.normpath(posixpath.join("xl", target))
        result.append((sheet.attrib.get("name", ""), archive_path))
    return result


def cell_text(cell: ElementTree.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t", "")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.iter(f"{{{MAIN_NS}}}t"))
    value_node = cell.find(f"{{{MAIN_NS}}}v")
    if value_node is None or value_node.text is None:
        formula = cell.find(f"{{{MAIN_NS}}}f")
        return f"={formula.text}" if formula is not None and formula.text else ""
    raw = value_node.text
    if cell_type == "s":
        try:
            return shared_strings[int(raw)]
        except (ValueError, IndexError):
            return raw
    if cell_type == "b":
        return "TRUE" if raw == "1" else "FALSE"
    return raw


def inspect_sheet(
    archive: zipfile.ZipFile,
    archive_path: str,
    shared_strings: list[str],
    max_header_values: int,
) -> dict[str, Any]:
    nonempty_rows = 0
    max_row = 0
    max_column = 0
    candidate_rows: list[list[str]] = []

    try:
        stream = archive.open(archive_path)
    except KeyError:
        return {
            "rows": 0,
            "columns": 0,
            "nonempty_rows": 0,
            "header_preview": [],
            "error": f"缺少工作表 XML：{archive_path}",
        }

    with stream:
        for _, row in ElementTree.iterparse(stream, events=("end",)):
            if row.tag != f"{{{MAIN_NS}}}row":
                continue
            row_number = int(row.attrib.get("r", max_row + 1))
            values: list[str] = []
            row_has_value = False
            for cell in row.findall(f"{{{MAIN_NS}}}c"):
                text = cell_text(cell, shared_strings).strip()
                if text:
                    row_has_value = True
                    values.append(text.replace("\r", " ").replace("\n", " "))
                max_column = max(
                    max_column, column_number(cell.attrib.get("r", ""))
                )
            if row_has_value:
                nonempty_rows += 1
                max_row = max(max_row, row_number)
                if len(candidate_rows) < 10:
                    candidate_rows.append(values)
            row.clear()

    header_preview: list[str] = []
    if candidate_rows:
        best_index, best = max(
            enumerate(candidate_rows), key=lambda item: (len(item[1]), -item[0])
        )
        del best_index
        header_preview = best[:max_header_values]
    return {
        "rows": max_row,
        "columns": max_column,
        "nonempty_rows": nonempty_rows,
        "header_preview": header_preview,
    }


def inspect_workbook(path: Path, max_header_values: int) -> dict[str, Any]:
    try:
        with zipfile.ZipFile(path) as archive:
            shared_strings = read_shared_strings(archive)
            sheets = []
            for name, archive_path in workbook_sheets(archive):
                detail = inspect_sheet(
                    archive, archive_path, shared_strings, max_header_values
                )
                detail["name"] = name
                sheets.append(detail)
        return {"status": "ok", "sheets": sheets}
    except (OSError, zipfile.BadZipFile, ElementTree.ParseError, KeyError) as error:
        return {"status": "error", "error": str(error), "sheets": []}


def source_key(relative_path: Path) -> str:
    parts = relative_path.parts
    if "策划源表" in parts:
        return "designer_workbooks"
    return "other"


def iter_workbooks(data_root: Path) -> Iterable[Path]:
    for path in sorted(data_root.rglob("*.xlsx"), key=lambda item: str(item).casefold()):
        if path.is_file() and not path.name.startswith("~$"):
            yield path


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "source_key",
        "relative_path",
        "filename",
        "size_bytes",
        "modified_at",
        "sha256",
        "status",
        "sheet_count",
        "sheet_names",
        "header_preview",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    data_root = root / "数值策划" / "数据源"
    knowledge_root = root / "数值策划" / "知识库"
    if not data_root.is_dir():
        raise FileNotFoundError(f"数据源目录不存在：{data_root}")

    details: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []
    totals: dict[str, int] = {}

    for index, path in enumerate(iter_workbooks(data_root), start=1):
        relative_path = path.relative_to(root)
        key = source_key(relative_path)
        totals[key] = totals.get(key, 0) + 1
        inspection = inspect_workbook(path, args.max_header_values)
        stat = path.stat()
        record = {
            "source_key": key,
            "relative_path": relative_path.as_posix(),
            "filename": path.name,
            "size_bytes": stat.st_size,
            "modified_at": datetime.fromtimestamp(
                stat.st_mtime, tz=timezone.utc
            ).isoformat(),
            "sha256": file_sha256(path) if args.with_hashes else "",
            **inspection,
        }
        details.append(record)
        sheet_names = [sheet.get("name", "") for sheet in inspection["sheets"]]
        header_parts = [
            f"{sheet.get('name', '')}: {' | '.join(sheet.get('header_preview', []))}"
            for sheet in inspection["sheets"][:5]
        ]
        csv_rows.append(
            {
                "source_key": key,
                "relative_path": relative_path.as_posix(),
                "filename": path.name,
                "size_bytes": stat.st_size,
                "modified_at": record["modified_at"],
                "sha256": record["sha256"],
                "status": inspection["status"],
                "sheet_count": len(inspection["sheets"]),
                "sheet_names": " | ".join(sheet_names),
                "header_preview": " || ".join(header_parts),
            }
        )
        if index % 100 == 0:
            print(f"已扫描 {index} 个工作簿...")

    generated_at = datetime.now(timezone.utc).isoformat()
    write_csv(knowledge_root / "工作簿目录.csv", csv_rows)
    write_json(
        knowledge_root / "工作簿结构.json",
        {
            "schema_version": 1,
            "hashes_included": args.with_hashes,
            "generated_at_utc": generated_at,
            "workbook_count": len(details),
            "source_counts": totals,
            "workbooks": details,
        },
    )

    error_count = sum(1 for item in details if item["status"] != "ok")
    markdown = f"""# CR 数值数据目录

> 由 `数值策划/工具/build_catalog.py` 自动生成，请勿手工维护。

- 生成时间（UTC）：`{generated_at}`
- 工作簿总数：**{len(details)}**
- 策划源表：**{totals.get("designer_workbooks", 0)}**
- 读取异常：**{error_count}**

## 检索入口

- `工作簿目录.csv`：适合 Excel、文本搜索和 AI 快速定位。
- `工作簿结构.json`：包含各 Sheet 的有效行列与表头预览。
- `同步清单.json`：保留来源、目标、文件大小及历史来源记录。
- 目录默认不计算文件哈希；只有显式 `--with-hashes` 才生成，未计算的字段为空。

## 使用原则

1. 先用目录按文件名、Sheet 或字段定位候选文件。
2. 再打开具体工作簿核对业务含义、单位、公式和版本。
3. 自动目录不是业务权威源，不应直接据此发布配置。
"""
    knowledge_root.mkdir(parents=True, exist_ok=True)
    (knowledge_root / "数据目录.md").write_text(
        markdown, encoding="utf-8", newline="\n"
    )
    print(f"完成：{len(details)} 个工作簿，{error_count} 个读取异常。")
    return 1 if error_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
