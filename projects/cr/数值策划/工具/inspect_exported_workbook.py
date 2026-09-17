#!/usr/bin/env python3
"""从最终 XLSX 的实际 <f> 元素计数，不把以 = 开头的说明文字当公式。

python inspect_exported_workbook.py <PRIVATE_FINAL_XLSX>
只读、标准库；输出各页公式/缓存数量，不输出业务数值或公式正文。
"""
from __future__ import annotations

import argparse
import json
import posixpath
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}


def inspect_workbook(path: Path) -> dict:
    sheets = []
    with ZipFile(path) as archive:
        book = ET.fromstring(archive.read('xl/workbook.xml'))
        relationships = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        targets = {r.get('Id'): r.get('Target') for r in relationships}
        for sheet in book.findall('s:sheets/s:sheet', NS):
            target = targets[sheet.get('{' + NS['r'] + '}id')]
            part = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
            xml = ET.fromstring(archive.read(part))
            cells = [c for c in xml.findall('.//s:sheetData/s:row/s:c', NS) if c.find('s:f', NS) is not None]
            missing = [c.get('r') for c in cells if c.find('s:v', NS) is None
                       or (c.find('s:v', NS).text is None and c.get('t') != 'str')]
            errors = [c.get('r') for c in cells if c.get('t') == 'e']
            sheets.append({'sheet': sheet.get('name'), 'formula_cells': len(cells),
                           'missing_cache_cells': missing, 'error_cache_cells': errors})
    return {'formula_cells': sum(s['formula_cells'] for s in sheets),
            'formula_count_source': 'final XLSX XML <f> elements', 'sheets': sheets,
            'missing_formula_caches': sum(len(s['missing_cache_cells']) for s in sheets),
            'formula_error_caches': sum(len(s['error_cache_cells']) for s in sheets)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('xlsx', type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect_workbook(args.xlsx), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
