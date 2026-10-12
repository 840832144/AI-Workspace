"""TASK-0036 合并曲线：读取已交付缓存，不重算CR/CF既有模型。

extract/verify --cr <CR曲线v2.xlsx> --cf <CF曲线.xlsx> --output <受控目录>
--price-setting 固定r7013导出；--history 旧正式表，仅补CF商城VIP倍率。
汇率固定采用Task的0.78408，不提供可编辑输入。
作者为Artifact JS；本脚本的openpyxl只读。sanitize只清理输出元数据。
"""
from __future__ import annotations
import argparse
import json
import math
import re
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import openpyxl
from build_cashfrenzy_curves import NAMES, sanitize

FILE = 'CR_vs_CashFrenzy_数值曲线对照.xlsx'
FIRST = 32
FX = 0.78408


def read_cache(path: Path) -> list[list]:
    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    result = []
    for i, name in enumerate(NAMES):
        if i == 1:  # 旧累计门槛指数退出交付，不再读取。
            result.append([])
            continue
        width = [3, 4, 4, 6, 4][i]
        rows = [list(r) for r in book[name].iter_rows(min_row=6, max_col=width, values_only=True)
                if isinstance(r[0], (int, float))]
        result.append(rows)
    book.close()
    return result


def extract(cr: Path, cf: Path, price_setting: Path, history: Path) -> dict:
    """只复制既有结果；新计算仅限本轮授权的CF VIP边界/汇率。"""
    repo = Path(__file__).resolve().parents[4]
    spec = repo/'projects/cr/REPORTS/CR-20260922-PRODUCER-EXPERIENCE/CR_CF_CURVE_COMPARISON.md'
    text = spec.read_text(encoding='utf-8')
    points = [[int(a), int(b.replace(',', ''))] for a, b in re.findall(r'^\| ([0-7]) \| ([\d,]+) \|$', text, re.M)]
    high = float(re.search(r'最高兑换效率：([\d.]+)', text)[1])
    low = float(re.search(r'最低兑换效率：([\d.]+)', text)[1])
    shops = [[float(a), int(b.replace(',', ''))] for a, b in re.findall(r'^\| S\$([\d.]+) \| ([\d,]+) \|', text, re.M)]
    assert len(points) == 8 and len(shops) == 9
    assert round(min(p/v for v, p in shops), 4) == low
    assert round(max(p/v for v, p in shops), 4) == high
    cr_rows, cf_rows = read_cache(cr), read_cache(cf)
    assert [len(r) for r in cr_rows] == [15, 0, 4999, 5000, 4999]
    assert [len(r) for r in cf_rows] == [8, 0, 300, 300, 300]
    for rows in cr_rows + cf_rows[2:]:
        assert [r[0] for r in rows] == list(range(1, len(rows)+1))
    assert sum(r[1] == 'N/A' for r in cf_rows[3]) == 56
    assert '**1 SGD = 0.78408 USD**' in text
    assert price_setting.name == 'PriceSetting.xlsx' and price_setting.parent.name == 'r7013'
    book = openpyxl.load_workbook(price_setting, read_only=True, data_only=True)
    sheet = book['Sheet1']
    assert list(next(sheet.iter_rows(max_row=1, max_col=4, values_only=True))) == ['money','currencyType','vipType','vip0']
    shop_rows = [(r, row) for r, row in enumerate(sheet.iter_rows(min_row=5, max_col=19, values_only=True), 5)
                 if row[1:3] == (1, 1)]
    assert shop_rows
    expected = [1, 1.25, 1.5, 1.75, 2, 2.25] + [2.5]*10
    for _, row in shop_rows:
        assert all(math.isclose(coin/row[3], want) for coin, want in zip(row[3:19], expected))
    r, row = shop_rows[0]
    cr_rows[1] = [[vip, row[vip+3], row[3], f'PriceSetting.xlsx/Sheet1!{openpyxl.utils.get_column_letter(vip+4)}{r}/D{r}; r7013'] for vip in range(16)]
    book.close()
    book = openpyxl.load_workbook(history, read_only=True, data_only=True)
    historical = list(book['vip加成'].iter_rows(min_row=2, max_row=9, min_col=6, max_col=8, values_only=True))
    assert [(r[0], r[2]) for r in historical] == [tuple(r) for r in points]
    assert [r[1] for r in historical[2:]] == [2.5,4,7,10,20,40]  # 已登记截图口径
    assert historical[1][1] == 1.5
    book.close()
    return {'cr_file': cr.name, 'cf_file': cf.name, 'cr': cr_rows, 'cf': cf_rows[2:],
            'vip': [[v, p, f'VIP{v}', historical[v][1], f'CashRoyal数值.xlsx/vip加成!G{v+2}' if v <= 1 else 'User 2026-09-21商城金币截图口径']
                    for v, p in points], 'shops': shops, 'high': high, 'low': low,
            'fx': FX, 'cr_shop_tiers_checked':len(shop_rows),
            'evidence': 'User 2026-09-21确认及CR_CF_CURVE_COMPARISON.md；本轮未独立读取原截图，不含账号当前点数'}


def verify(data: dict, output: Path) -> dict:
    f = openpyxl.load_workbook(output/FILE, data_only=False)
    v = openpyxl.load_workbook(output/FILE, data_only=True)
    assert [s.title for s in f if s.sheet_state == 'visible'] == NAMES
    assert f['SRC_CR'].sheet_state == f['SRC_CF'].sheet_state == 'hidden'
    fx = v['SRC_CF']['X5'].value
    assert fx == data['fx'] == FX
    assert f[NAMES[0]]['B4'].value is None
    assert 'CF_SGD_TO_USD' not in f.defined_names
    def same(got: object, expected: object) -> None:
        if isinstance(expected, (float, int)):
            assert isinstance(got, (float, int)) and math.isclose(got, expected, rel_tol=1e-10, abs_tol=1e-8), (got, expected)
        else:
            assert got == expected, (got, expected)
    for i in range(5):
        for j, row in enumerate(data['cr'][i]):
            r = FIRST+j
            cf = data['cf'][i-2][j] if i >= 2 and j < 300 else None
            if i == 0:
                vip = data['vip'][j+1] if j < 7 else None
                expected = [row[0], row[1], vip[2] if vip else 'N/A', vip[1] if vip else 'N/A',
                            vip[1]/data['high'] if vip else 'N/A', vip[1]/data['low'] if vip else 'N/A',
                            vip[1]/data['high']*fx if vip else 'N/A',
                            vip[1]/data['low']*fx if vip else 'N/A',
                            data['high'] if vip else 'N/A', data['low'] if vip else 'N/A', row[2]]
            elif i == 1:
                vip = data['vip'][j] if 1 <= j <= 7 else None
                expected = [row[0], row[1]/row[2], vip[3] if vip else 'N/A', row[1]/row[2], vip[3] if vip else 'N/A',
                            '历史正式表' if j == 1 else 'User截图口径' if vip else 'CF不在展示范围']
            elif i == 2:
                expected = [row[0], row[1], cf[1] if cf else 'N/A', row[2], cf[2] if cf else 'N/A', row[3], cf[3] if cf else 'N/A']
            elif i == 3:
                expected = [row[0], row[1], row[3], cf[1] if cf else 'N/A', cf[3] if cf else 'N/A',
                            row[2], row[4], cf[2] if cf else 'N/A', cf[4] if cf else 'N/A',row[5],cf[5] if cf else 'N/A']
            else:
                expected = [row[0],row[1],cf[1] if cf else 'N/A',row[2],cf[2] if cf else 'N/A',row[3],cf[3] if cf else 'N/A']
            for c, want in enumerate(expected, 1):
                same(v[NAMES[i]].cell(r, c).value, want)
    for j, (price, pts) in enumerate(data['shops'], 32):
        for col, expected in zip('LMN', [price,pts,pts/price]):
            same(v[NAMES[0]][f'{col}{j}'].value, expected)
    for r in range(32,39):
        # 原生引擎会去除简单Sheet名两侧的非必需引号。
        assert f[NAMES[0]][f'G{r}'].value.replace("'SRC_CF'", 'SRC_CF') == f"=E{r}*SRC_CF!$X$5"
        assert f[NAMES[0]][f'H{r}'].value.replace("'SRC_CF'", 'SRC_CF') == f"=F{r}*SRC_CF!$X$5"
    errors, blanks = [], []
    for s in f:
        for row in s:
            for c in row:
                if c.data_type != 'f':
                    continue
                actual = v[s.title][c.coordinate]
                if actual.value is None:
                    blanks.append((s.title, c.coordinate))
                if actual.data_type == 'e':
                    errors.append((s.title,c.coordinate))
    assert not errors and not blanks, (errors[:5], blanks[:5])
    ns = {'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
    points = []
    with ZipFile(output/FILE) as z:
        assert not any(n.startswith('xl/externalLinks/') for n in z.namelist())
        assert not any(re.search(r'(?<![A-Za-z])(?:[A-Za-z]:[\\/]|file:/)', z.read(n).decode()) for n in z.namelist() if n.endswith(('.xml','.rels')))
        core=ET.fromstring(z.read('docProps/core.xml'))
        assert not any(e.text for e in core if e.tag.rsplit('}',1)[-1] in ('creator','lastModifiedBy'))
        charts=sorted(n for n in z.namelist() if re.fullmatch(r'xl/charts/chart\d+\.xml',n))
        assert len(charts)==5
        for i, name in enumerate(charts):
            root=ET.fromstring(z.read(name));lines=root.findall('.//c:lineChart',ns)
            assert len(lines)==1
            series=lines[0].findall('c:ser',ns)
            assert len(series)==[3,2,2,4,2][i]
            count=[]
            for item in series:
                ref=item.find('c:val/c:numRef/c:f',ns).text
                assert ref.endswith(str([46,47,331,331,331][i])), ref
                pts=item.findall('c:val/c:numRef/c:numCache/c:pt/c:v',ns)
                count.append(sum(p.text not in (None,'','#N/A') for p in pts))
            points.append(count)
            assert len(root.findall('.//c:valAx',ns)) == 1  # 同图同一金额/倍率轴
    expected=[[15,7,7],[16,7],[300,300],[300,300,244,300],[300,300]]
    assert points==expected, points
    for name in NAMES:
        assert f[name].freeze_panes is None
        for row in v[name].iter_rows(max_row=48, max_col=14):
            assert not any(any(x in str(c.value) for x in ['黄金','铂金','钛金','尊徽','百夫长','王者风范','绝对指数','VIP1=100%','待汇率']) for c in row)
    result={'task':'TASK-0036','status':'Review','visible_sheets':NAMES,'charts':5,'series':[3,2,2,4,2],
            'chart_numeric_points':points,'cr_full_rows':[15,16,4999,5000,4999],'cf_level_rows':300,
            'cf_bet_conflict_points':56,'vip_cumulative_resolved':True,'CF_SGD_TO_USD':fx,
            'usd_cost_comparison':'固定分析汇率；SGD原值与USD上下界同时保留','editable_fx_inputs':0,
            'shop_multipliers_max':{'CR':2.5,'CF':40},'cf_vip1_source':'历史正式表vip加成!G3',
            'cr_shop_tiers_checked':data['cr_shop_tiers_checked'],'visible_shop_samples':9,
            'intentional_chart_NA':0,'unexpected_formula_errors':0,'missing_formula_caches':0,
            'prior_model_values_changed':0,'external_links':0,'frozen_sheets':0}
    f.close();v.close()
    return result


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['extract','sanitize','verify'])
    p.add_argument('--cr',type=Path,required=True);p.add_argument('--cf',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--price-setting',type=Path,required=True);p.add_argument('--history',type=Path,required=True)
    a=p.parse_args()
    assert not a.output.resolve().is_relative_to(Path(__file__).resolve().parents[4])
    a.output.mkdir(parents=True,exist_ok=True)
    if a.action=='sanitize':
        print(sanitize(a.output,FILE));return
    data=extract(a.cr,a.cf,a.price_setting,a.history)
    result=data if a.action=='extract' else verify(data,a.output)
    name='comparison-inputs.json' if a.action=='extract' else 'validation.json'
    (a.output/name).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'action':a.action,'status':'passed','output':name}))


if __name__=='__main__':
    main()
