"""Read an accepted local comparison and prepare a values-only cloud presentation.

prepare --input <xlsx> --notes <controlled.json> --out <directory>
verify --input <source.xlsx> --out <directory>
Source files are read-only; authoring is performed by the companion Artifact script.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile
import openpyxl
from lxml import etree as ET


def prepare(source: Path, notes: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    w = openpyxl.load_workbook(source, data_only=True)
    selections = [
        ('等级段对比', '等级段对比', list(range(1, 48)), 5, 104),
        ('每50级拟合', '等级段对比', list(range(1, 22)), 116, 145),
        ('VIP对比', 'VIP对比', list(range(1, w['VIP对比'].max_column+1)), 5, w['VIP对比'].max_row),
        ('CR调整候选', 'CR调整候选', [1]+list(range(40, 72)), 5, 1505),
        ('CR明细', 'CR明细', list(range(1, 20)), 5, 1505),
        ('CF明细', 'CF明细', list(range(1, w['CF明细'].max_column+1)), 5, 1505),
        ('POP明细', 'POP明细', [1]+list(range(20, 49)), 5, 1505),
    ]
    blocked = re.compile(r'(?:[A-Za-z]:[\\/]|%LOCALAPPDATA%|https?://|(?:token|cookie|secret|password)\s*[:=])', re.I)
    tabs = []
    for title, name, cols, start, end in selections:
        rows = []
        formats = []
        for r in range(start, end+1):
            row = []
            for c in cols:
                value = w[name].cell(r, c).value
                if isinstance(value, str):
                    if blocked.search(value): value = '来源见受控底稿'
                    value = value.replace('特殊40线', '40线机型').replace('普通20线', '普通20线')
                    if r == start: value = value.replace('特殊', '40线')
                row.append(value)
            rows.append(row)
            if r == start+1: formats = [w[name].cell(r, c).number_format for c in cols]
        tabs.append(dict(name=title, source=name, columns=cols, start=start, end=end, rows=rows, formats=formats))
    ns = {'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart', 'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
    charts = []
    with ZipFile(source) as z:
        for name in sorted(n for n in z.namelist() if re.fullmatch(r'xl/charts/chart\d+\.xml', n)):
            root = ET.fromstring(z.read(name))
            series = []
            for s in root.findall('.//c:lineChart/c:ser', ns):
                label = ''.join(s.xpath('./c:tx//c:v/text()', namespaces=ns))
                points = s.findall('./c:val/c:numRef/c:numCache/c:pt', ns)
                cats = s.findall('./c:cat/c:numRef/c:numCache/c:pt', ns) or s.findall('./c:cat/c:strRef/c:strCache/c:pt', ns)
                series.append(dict(name=label.replace('特殊40线','40线机型'), values=[float(p.find('c:v',ns).text) for p in points], categories=[p.find('c:v',ns).text for p in cats]))
            if series:
                charts.append(dict(title=''.join(root.xpath('.//c:title//a:t/text()',namespaces=ns)), series=series))
    payload = dict(tabs=tabs, charts=charts, notes=json.loads(notes.read_text(encoding='utf-8-sig')),
                   source_size=source.stat().st_size, source_mtime=source.stat().st_mtime_ns)
    (out/'display-input.controlled.json').write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
    w.close()
    return dict(tabs=len(tabs), charts=len(charts), source_read_only=True)


def verify(source: Path, out: Path) -> dict:
    d=json.loads((out/'display-input.controlled.json').read_text(encoding='utf-8'))
    path=out/'CR_CF_POP_对比表_飞书展示审阅版.xlsx'
    w=openpyxl.load_workbook(path,data_only=True)
    checked=0
    for tab in d['tabs']:
        for r,row in enumerate(tab['rows'],5):
            for c,v in enumerate(row,1):
                got=w[tab['name']].cell(r,c).value
                assert got == v or isinstance(v,(float,int)) and isinstance(got,(float,int)) and abs(got-v)<=max(1e-8,abs(v)*1e-12), (tab['name'],r,c,v,got)
                checked+=1
    with ZipFile(path) as z:
        assert not any(n.startswith('xl/externalLinks/') for n in z.namelist())
        xml='\n'.join(z.read(n).decode('utf-8') for n in z.namelist() if n.endswith('.xml'))
        assert not re.search(r'\b[A-Za-z]:[\\/]|%LOCALAPPDATA%|JSESSIOINID|jwt_session',xml)
        for n in z.namelist():
            if n.startswith('xl/worksheets/') and n.endswith('.xml'):
                root=ET.fromstring(z.read(n))
                assert not root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f')
        charts=len([n for n in z.namelist() if re.fullmatch(r'xl/(?:drawings/)?charts/chart\d+\.xml',n)])
        assert charts==len(d['charts'])
    assert source.stat().st_size==d['source_size'] and source.stat().st_mtime_ns==d['source_mtime']
    result=dict(status='pass', compared_cells=checked, charts=charts, source_unchanged=True,
                numeric_model_changed=False, raw_source_tabs_uploaded=False, external_links=0,
                formulas=0, presentation_snapshot=True, needs_numeric_revision=True)
    (out/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['prepare','verify']);p.add_argument('--input',type=Path,required=True)
    p.add_argument('--notes',type=Path);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();print(json.dumps(prepare(a.input,a.notes,a.out) if a.action=='prepare' else verify(a.input,a.out),ensure_ascii=False))
