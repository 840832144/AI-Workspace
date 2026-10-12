"""固定版本原始工作簿读取。openpyxl仅只读，不保存或修改源表。"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

REVISION = 7013


def export_sources(lock_path: Path, names: list[str], output: Path) -> dict:
    """使用已有SVN身份定向export；不打印内部URL或完整响应。"""
    lock = json.loads(lock_path.read_text(encoding='utf-8-sig'))
    assert lock['environment'] == 'trunk' and lock['selected_revision'] == REVISION
    root = output / 'source' / 'r7013'
    root.mkdir(parents=True, exist_ok=True)
    receipt_path = output / 'export-receipt.json'
    receipt = json.loads(receipt_path.read_text(encoding='utf-8')) if receipt_path.exists() else {
        'revision': REVISION, 'environment': 'trunk', 'method': 'svn export -r7013 URL@7013',
        'files': [], 'no_hash': True,
    }
    completed = {r['table'] for r in receipt['files']}
    for name in names:
        filename = name + '.xlsx'
        target = root / filename
        if name in completed:
            assert (root / next(r['file'] for r in receipt['files'] if r['table']==name)).is_file()
            continue
        # 一个未登记的既有文件不被覆盖；第一次手动只读导出的LevelCfg需显式纳入记录。
        if target.exists():
            target = root / (name + '.fresh.xlsx')
            assert not target.exists()
        result = subprocess.run(['svn', 'export', '-r', str(REVISION),
            lock['config_url'].rstrip('/') + '/' + filename + '@7013', str(target)], capture_output=True)
        if result.returncode:
            raise RuntimeError(f'固定版本导出失败：{filename}，exit={result.returncode}；未输出内部响应')
        if target.name != filename:
            # 两次均为本任务导出；原文件保留，清单和外链以fresh文件为真实源。
            filename = target.name
        receipt['files'].append({'table': name, 'file': filename,
            'exported_at': datetime.now(timezone.utc).isoformat(), 'revision': REVISION})
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    return receipt


def read_source(path: Path) -> dict[str, Any]:
    """保留原格坐标、空值与缓存错误；原始公式不重算、不补零。"""
    wb = load_workbook(path, read_only=True, data_only=True, keep_links=False)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    fields = [(i, str(value)) for i, value in enumerate(rows[0]) if value is not None]
    records = []
    errors = []
    for excel_row, values in enumerate(rows[4:], 5):
        if all(v is None for v in values):
            continue
        record = {name: values[i] if i < len(values) else None for i, name in fields}
        record['_excel_row'] = excel_row
        record['_row_id'] = str(values[fields[0][0]])
        records.append(record)
        for i, name in fields:
            if isinstance(record[name], str) and record[name] in ('#REF!', '#DIV/0!', '#VALUE!', '#NAME?', '#N/A', '#NUM!', '#NULL!'):
                errors.append({'row': excel_row, 'field': name, 'error': record[name]})
    result = {'sheet': ws.title, 'fields': fields, 'comments': rows[3], 'records': records, 'errors': errors}
    wb.close()
    return result


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lock',type=Path,required=True)
    parser.add_argument('--catalog',type=Path,required=True,help='结构摘要，包含source_tables；不含内部地址')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert not any((p/'.git').exists() for p in (args.output.resolve(),*args.output.resolve().parents))
    catalog=json.loads(args.catalog.read_text(encoding='utf-8'))
    receipt=export_sources(args.lock,catalog['source_tables'],args.output)
    print(json.dumps({'revision':REVISION,'exported_workbooks':len(receipt['files']),'operation':'read-only export'}))
