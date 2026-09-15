"""Python 3 标准库无损读取 XLSX 单元格值和公式；不重算、不修改源表。

示例：python tools/extract_xlsx.py --input config/trunk/CardPack.xlsx --output data/trunk/CardPack.json
"""
from __future__ import annotations
import argparse
import json
import posixpath
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

def extract(path: Path) -> dict[str, Any]:
    """只读取实际单元格，忽略 Excel 的虚高 used range，保留行号与空值。"""
    with zipfile.ZipFile(path) as archive:
        strings=[]
        if 'xl/sharedStrings.xml' in archive.namelist():
            strings=[''.join(x.itertext()) for x in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('m:si',NS)]
        rels={x.attrib['Id']:x.attrib['Target'] for x in ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))}
        sheets=[]
        for sheet in ET.fromstring(archive.read('xl/workbook.xml')).findall('m:sheets/m:sheet',NS):
            target=rels[sheet.attrib[f'{{{REL}}}id']]
            member=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
            rows=[]
            for row in ET.fromstring(archive.read(member)).findall('m:sheetData/m:row',NS):
                cells={}
                for c in row.findall('m:c',NS):
                    v=c.find('m:v',NS); f=c.find('m:f',NS); inline=c.find('m:is',NS)
                    if v is None and f is None and inline is None:
                        continue
                    kind=c.attrib.get('t','n'); raw=v.text if v is not None else None
                    value: Any=raw
                    if kind=='s' and raw is not None:
                        value=strings[int(raw)]
                    elif kind=='inlineStr':
                        value=''.join(inline.itertext()) if inline is not None else ''
                    elif kind=='b' and raw is not None:
                        value=raw=='1'
                    elif kind=='n' and raw is not None:
                        try:
                            value=float(raw) if any(x in raw.lower() for x in ['.','e']) else int(raw)
                        except ValueError:
                            value=raw
                    cell={'value':value}
                    if f is not None:
                        cell['formula']='='+(f.text or '')
                        if f.attrib:
                            cell['formula_attributes']=f.attrib
                    if kind=='e':
                        cell['error']=raw
                    cells[c.attrib['r']]=cell
                if cells:
                    rows.append({'row':int(row.attrib['r']),'cells':cells})
            sheets.append({'name':sheet.attrib['name'],'rows':rows})
        return {'source_file':path.name,'value_note':'公式值为原文件保存的缓存，未重新计算；null不是0。','sheets':sheets}

def records(extracted: dict[str, Any], sheet_index: int = 0) -> list[dict[str, Any]]:
    """转换四行表头的程序配置，保留源 Excel 行号和每个命名字段。"""
    rows=extracted['sheets'][sheet_index]['rows']
    if not rows:
        return []
    header=next((r for r in rows if r['row']==1),{'cells':{}})['cells']
    fields={''.join(c for c in ref if c.isalpha()):cell['value'] for ref,cell in header.items() if cell['value'] is not None}
    result=[]
    for row in rows:
        if row['row']<=4:
            continue
        values={''.join(c for c in ref if c.isalpha()):cell['value'] for ref,cell in row['cells'].items()}
        if not any(values.get(col) is not None for col in fields):
            continue
        result.append({'_excel_row':row['row'],**{str(field):values.get(col) for col,field in fields.items()}})
    return result

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=extract(args.input)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"sheets={len(result['sheets'])}")

if __name__=='__main__':
    main()
