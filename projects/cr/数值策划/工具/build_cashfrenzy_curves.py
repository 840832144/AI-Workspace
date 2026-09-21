"""TASK-0036 历史CF曲线：只读提取与定向验收，不接触SVN或Collector。

extract --source <CashRoyal数值.xlsx> --output <受控目录>
verify --source <CashRoyal数值.xlsx> --output <受控目录>
依赖 openpyxl（仅用于读取）；XLSX由配套Artifact JS生成。
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

NAMES = ['VIP_消费门槛', 'VIP_膨胀系数', '等级_升级消耗', '等级_Bet曲线', '等级_升级消耗返还']
FILE = 'CashFrenzy_数值曲线对照.xlsx'
SRC = 'SRC_CashFrenzy'


def extract(source: Path) -> dict:
    """限定为旧表CF区块；拒绝变更后的来源结构，不混用其他游戏列。"""
    wb = openpyxl.load_workbook(source, read_only=True, data_only=False)
    cache = openpyxl.load_workbook(source, read_only=True, data_only=True)
    ws = list(wb['cashFrenzy等级'].values)
    values = list(cache['cashFrenzy等级'].values)
    vip = list(wb['vip加成'].values)
    assert ws[0][:9] == ('等级', '最大bet', 'sipn', '消耗', '升级奖励', '奖励美金', '消耗美金', '返还比', '倍数')
    assert vip[0][5:9] == ('vip', 'frenzy', '经验', '美金')
    assert ws[0][23:25] == ('抽水', '单位美金')
    assert ws[0][35:37] == ('bet', '解锁等级')
    rate = re.fullmatch(r'=H3/([0-9.]+)', vip[2][8])
    assert rate, 'VIP换算公式需重新审阅'
    points_per_usd = float(rate[1])
    rake, coins_usd = values[1][23:25]
    unlocks = [[r[36], r[35], f'cashFrenzy等级!AJ{i}:AK{i}'] for i, r in enumerate(ws[1:], 2)
               if isinstance(r[35], (int, float)) and isinstance(r[36], (int, float))]
    rows, mismatches = [], []
    for r, (form, val) in enumerate(zip(ws[1:], values[1:]), 2):
        level, bet, spins, _, reward, _, _, _, multiplier = val[:9]
        assert level == r - 1
        assert all(isinstance(x, (int, float)) for x in (level, bet, spins, reward, multiplier))
        assert bet > 0 and spins > 0 and multiplier > 0
        expected_formulas = {3: f'=B{r}*C{r}*$X$2', 5: f'=E{r}/$Y$2/I{r}',
                             6: f'=D{r}/$Y$2/I{r}', 7: f'=E{r}/D{r}'}
        for col, formula in expected_formulas.items():
            assert form[col] == formula, f'来源公式变化：{r}/{col}'
        cost = bet * spins * rake / coins_usd / multiplier
        reward_usd = reward / coins_usd / multiplier
        for actual, expected in [(val[3], bet * spins * rake), (val[5], reward_usd),
                                 (val[6], cost), (val[7], reward_usd / cost)]:
            assert math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-9)
        unlocked = max(v for lv, v, _ in unlocks if lv <= level)
        confirmed = bet == unlocked
        if not confirmed:
            mismatches.append(level)
        rows.append([level, bet, spins, reward, multiplier, unlocked,
                     int(confirmed), val[6], val[5], val[7], f'cashFrenzy等级!A{r}:I{r}'])
    vips = []
    for r, row in enumerate(vip[1:], 2):
        if row[5] is None:
            continue
        assert row[8] == f'=H{r}/{rate[1]}'
        vips.append([row[5], row[7], points_per_usd, f'vip加成!F{r}:I{r}'])
    assert [v[0] for v in vips] == list(range(8)) and vips[0][1] == 0
    assert len(rows) == 300
    result = {'source': source.name, 'source_sheet': 'cashFrenzy等级',
              'source_modified_metadata': str(wb.properties.modified),
              'version': '历史资料；游戏采样日期/版本未标注',
              'levels': rows, 'vip': vips, 'unlocks': unlocks,
              'rake': rake, 'coins_per_usd': coins_usd,
              'bet_conflict_levels': mismatches,
              'gaps': [
                  'VIP经验未注明累计或本级；仅VIP0/1无歧义，VIP2–7累计/新增与绝对指数均N/A。',
                  '普通Bet主表与同页解锁表不一致的等级，最大Bet及其美元折算为N/A。',
                  'highroller单列上限的附加可用条件未说明；前台只对照普通Bet，不宣称全模式绝对上限。',
                  '300级以后缺逐级Spin、奖励、价值倍率；不外推。历史表采样版本未说明。',
                  '$1等值推荐Bet为历史金币估值的逆换算，不保证命中实际可下注档。',
                  '奖励只计来源升级金币列，其他升级奖励未提供；消耗为历史抽水折算，不是实付金额。']}
    wb.close()
    cache.close()
    return result


def verify(source: Path, output: Path) -> dict:
    data = extract(source)
    wb = openpyxl.load_workbook(output / FILE, data_only=False)
    cache = openpyxl.load_workbook(output / FILE, data_only=True)
    visible = [s.title for s in wb if s.sheet_state == 'visible']
    assert visible == NAMES and wb[SRC].sheet_state == 'hidden'
    errors, absent = [], []
    for sheet in wb:
        for row in sheet:
            for cell in row:
                if cell.data_type == 'f':
                    got = cache[sheet.title][cell.coordinate]
                    if got.value is None:
                        absent.append((sheet.title, cell.coordinate))
                    if got.data_type == 'e':
                        errors.append((sheet.title, cell.coordinate, got.value))
    assert not errors and not absent, (errors[:5], absent[:5])
    def same(actual: object, expected: object) -> None:
        if isinstance(expected, (int, float)):
            assert isinstance(actual, (int, float)) and math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-9)
        else:
            assert actual == expected
    # 每个交付数据点的直接来源/复算，而不是旧CR底稿重复验收。
    for idx, row in enumerate(data['levels'], 6):
        lv, bet, spins, reward, mult, unlock, confirmed, cost, ret, ratio, _ = row
        for col, expected in zip('ABCD', [lv, cost, ret, cost-ret]):
            same(cache[NAMES[2]][f'{col}{idx}'].value, expected)
        rec = data['coins_per_usd'] * mult
        for col, expected in zip('ABCDEF', [lv, bet if confirmed else 'N/A', bet/1e6 if confirmed else 'N/A',
                                          rec, rec/1e6, bet/rec if confirmed else 'N/A']):
            same(cache[NAMES[3]][f'{col}{idx}'].value, expected)
        for col, expected in zip('ABCD', [lv, ratio, cost, ret]):
            same(cache[NAMES[4]][f'{col}{idx}'].value, expected)
        assert wb[NAMES[4]][f'B{idx}'].value == f'=D{idx}/C{idx}'
    for idx, (vip, points, rate, _) in enumerate(data['vip'], 6):
        cost = points/rate if vip < 2 else 'N/A'
        same(cache[NAMES[0]][f'B{idx}'].value, cost)
        same(cache[NAMES[0]][f'C{idx}'].value, cost)
        same(cache[NAMES[1]][f'B{idx}'].value, vip if vip < 2 else 'N/A')
    assert wb[NAMES[1]]['B7'].value == '=C7/$C$7'
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
          'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'}
    with ZipFile(output/FILE) as z:
        assert not any(n.startswith('xl/externalLinks/') for n in z.namelist())
        core = ET.fromstring(z.read('docProps/core.xml'))
        assert not any(e.text for e in core if e.tag.rsplit('}', 1)[-1] in ('creator', 'lastModifiedBy'))
        assert not any(re.search(r'(?<![A-Za-z])(?:[A-Za-z]:[\\/]|file:/)', z.read(n).decode('utf-8'))
                       for n in z.namelist() if n.endswith(('.xml', '.rels')))
        chart_paths = sorted(n for n in z.namelist() if re.fullmatch(r'xl/charts/chart\d+\.xml', n))
        assert len(chart_paths) == 5
        counts = []
        for i, name in enumerate(chart_paths):
            root = ET.fromstring(z.read(name))
            lines = root.findall('.//c:lineChart', ns)
            assert len(lines) == 1
            series = lines[0].findall('c:ser', ns)
            assert len(series) == (2 if i == 3 else 1)
            points = []
            for s in series:
                ref = s.find('c:val/c:numRef/c:f', ns).text
                assert str(13 if i < 2 else 305) in ref
                p = s.findall('c:val/c:numRef/c:numCache/c:pt', ns)
                points.append(sum(x.find('c:v', ns).text not in ('', None) for x in p))
            counts.append(points)
            assert root.find('.//c:dispBlanksAs', ns).get('val') == 'gap'
        assert counts == [[2], [2], [300], [244, 300], [300]], counts
    for name in NAMES:
        assert wb[name].freeze_panes is None
    summary = {'task': 'TASK-0036', 'status': 'Review', 'source': data['source'],
               'source_sheets': ['cashFrenzy等级', 'vip加成（仅F:I竞品区块）'],
               'visible_sheets': visible, 'vip_rows': 8, 'vip_resolved': 2, 'vip_NA': 6,
               'level_rows': 300, 'max_bet_confirmed_points': 244, 'max_bet_NA_points': 56,
               'chart_types': ['line']*5, 'chart_numeric_points': counts,
               'formula_errors': len(errors), 'missing_formula_caches': len(absent),
               'external_links': 0, 'frozen_visible_sheets': 0, 'source_cache_mismatches': 0,
               'gaps': data['gaps']}
    wb.close()
    cache.close()
    return summary


def sanitize(output: Path) -> dict:
    """原生保存会回填Host作者；只去除输出包的作者元数据，保留计算缓存。"""
    book = output/FILE
    temporary = output/'metadata-clean.tmp'
    with ZipFile(book) as old, ZipFile(temporary, 'w') as new:
        for item in old.infolist():
            raw = old.read(item.filename)
            if item.filename == 'docProps/core.xml':
                root = ET.fromstring(raw)
                for child in list(root):
                    if child.tag.rsplit('}', 1)[-1] in ('creator', 'lastModifiedBy'):
                        root.remove(child)
                raw = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            elif item.filename == 'xl/workbook.xml':
                # 仅删原生保存补写的本机目录提示；不重写XML命名空间或公式。
                raw = re.sub(rb'<(?:\w+:)?absPath\b[^>]*/>', b'', raw)
            new.writestr(item, raw)
    temporary.replace(book)
    return {'author_and_absolute_path_metadata': 'removed'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['extract', 'sanitize', 'verify'])
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[4]
    assert not args.output.resolve().is_relative_to(repo), '完整商业数据必须留在受控目录'
    args.output.mkdir(parents=True, exist_ok=True)
    if args.action == 'sanitize':
        print(json.dumps(sanitize(args.output)))
        return
    data = extract(args.source) if args.action == 'extract' else verify(args.source, args.output)
    name = 'cf-inputs.json' if args.action == 'extract' else 'validation.json'
    (args.output/name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'action': args.action, 'result': 'passed', 'output': name}, ensure_ascii=False))


if __name__ == '__main__':
    main()
