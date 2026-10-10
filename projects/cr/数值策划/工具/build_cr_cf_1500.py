"""TASK-0036: prepare a controlled CR/CF comparison; never writes configuration.

prepare --current <source lock directory> --history <bet-dev-inputs.json> --out <output>
verify --out <output>  (XLSX is authored separately with Artifact Tool.)
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import openpyxl
from build_cashfrenzy_curves import sanitize

BOOK = 'CR_vs_CF_数值对比_1500级_trunk_r7502.xlsx'


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def save(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def prepare_pop(baseline: Path, source: Path, history: Path, out: Path) -> dict:
    """Append only the supplied POP evidence; preserve prepared CR/CF inputs."""
    out.mkdir(parents=True, exist_ok=True)
    data = read(baseline/'inputs.controlled.json')
    expected = read(baseline/'expected.controlled.json')
    raw = read(source/'PS_DATASET.json')
    levels = raw['level_table']
    assert [r['level'] for r in levels] == list(range(1,42))
    assert all(r['next_xp']-r['start_xp']==r['span_xp'] for r in levels)
    assert all(a['next_xp']==b['start_xp'] for a,b in zip(levels,levels[1:]))
    anchors = {1: raw['bet_ladders']['MGM Grand MegaStars (20 lines)']['min']}
    for r in levels:
        if r['max_bet_per_line_after'] is not None:
            anchors[r['level']] = r['max_bet_per_line_after']*20
    rows = [[r['level'],r['start_xp'],r['next_xp'],r['span_xp'],
             anchors[max(l for l in anchors if l<=r['level'])]] for r in levels]
    # Anchored fits: XP uses the last observed regime; Bet includes its plateau.
    xp_slope = sum((r[0]-41)*(r[3]-rows[-1][3]) for r in rows[29:])/sum((r[0]-41)**2 for r in rows[29:])
    bet_slope = sum((r[0]-41)*(r[4]-rows[-1][4]) for r in rows[14:])/sum((r[0]-41)**2 for r in rows[14:])
    assert xp_slope>0 and bet_slope>0
    old_vip = read(history)['pop']
    tiers = raw['vip']['tiers']
    assert [r['tp_to_obtain'] for r in tiers]==old_vip[:len(tiers)]
    vip = [[i+1,v, float(tiers[i]['chip_package_bonus'].strip('%'))/100 if i<len(tiers) else None,
            '10/09界面' if i<len(tiers) else '历史正式截图'] for i,v in enumerate(old_vip)]
    store = sorted([[s['usd'],s['coins']] for s in raw['store']['skus']])
    data['pop'] = {'levels':rows,'vip':vip,'store':store,'bet_anchors':sorted(anchors),
                   'xp_fit_window':[30,41],'bet_fit_window':[15,41],
                   'xp_rounding':100000,'bet_step':50000,'historical_tp_usd':80,
                   'source':'PS_DATASET.json / 2026-10-09 handoff',
                   'xp_slope':xp_slope,'bet_slope':bet_slope}
    data['book'] = 'CR_vs_CF_vs_POP_数值对比_1500级_trunk_r7502.xlsx'
    data['overview'] = sorted(set(data['overview'])|set(anchors))
    coin_low=store[0][1]/store[0][0]
    coin_high=store[-1][1]/store[-1][0]
    result=[]
    cumulative=0
    for level in range(1,1501):
        if level<=41:
            _,start,end,need,bet=rows[level-1]
        else:
            start=cumulative
            need=math.floor((rows[-1][3]+xp_slope*(level-41))/100000+0.5)*100000
            bet=math.floor((rows[-1][4]+bet_slope*(level-41))/50000)*50000
            end=start+need
        cumulative=end
        result.append([level,bet,need,need/bet,need/coin_low,need/coin_high,
                       need/rows[0][3],start,end,need/(bet if level<=41 else rows[-1][4])])
    assert all(b[2]>=a[2] and b[1]>=a[1] for a,b in zip(result,result[1:]))
    save(out/'inputs.controlled.json',data)
    save(out/'expected.controlled.json',expected)
    save(out/'pop-expected.controlled.json',result)
    summary={'cr_cf_inputs_reused':True,'pop_observed_level_rows':41,'pop_fitted_level_rows':1459,
             'pop_current_vip_tiers':4,'pop_historical_vip_tiers':6,
             'pop_vip_bonus_fitted_tiers':6,'pop_currency_level_multiplier':'N/A',
             'pop_spin_rule':'supplied standard paid-spin model; not independently observed',
             'overview_rows':len(data['overview']),'configuration_write':False}
    save(out/'preparation-validation.json',summary)
    return summary


def prepare(current: Path, history: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    tables = read(current/'cr-current-tables.controlled.json')
    lock = read(current/'source-lock.local.json')
    cf = read(current/'cf-confirmed-reference.controlled.json')
    old = read(history)
    assert lock['revision'] == 7502 and lock['environment'] == 'CR trunk'
    assert len(old['cf']) == 300 and len(cf['cf']) == 124
    bets = {r['levelId']: r for r in tables['SlotsCasinoBetList']['records']}
    unlocks = [r for r in tables['SlotsCasinoBetUnlock']['records'] if r['highroller'] == 0]
    rates = {r['level']: r for r in tables['PriceCheatSheet']['records']
             if (r['priceType'], r['vipType'], r['money']) == (17, 1, 100)}
    vip_price = next(r for r in tables['PriceCheatSheet']['records']
                     if (r['priceType'], r['vipType'], r['level'], r['money']) == (2, 1, 0, 99))
    vip_coin = next(r for r in tables['PriceCheatSheet']['records']
                    if (r['priceType'], r['vipType'], r['level'], r['money']) == (9, 1, 0, 99))
    cr = []
    for rec in tables['LevelCfg']['records'][:1500]:
        level = rec['level']
        stage = max(r['level'] for r in unlocks if r['level'] <= level)
        pool = [r for r in unlocks if r['level'] == stage]
        chosen = max(pool, key=lambda r: bets[r['betlevel']]['bet2'])
        bet = bets[chosen['betlevel']]
        price = rates[max(k for k in rates if k <= level)]
        cr.append([level, rec['levelUpType'] or 0, rec['levelUpExp'], bet['bet2'],
                   bet['levelExp'], price['vip_16_0'], rates[0]['vip_16_0'],
                   f"LevelCfg/{tables['LevelCfg']['sheet']}!B{rec['_excel_row']}:C{rec['_excel_row']}",
                   f"BetList!E{bet['_excel_row']}:F{bet['_excel_row']};BetUnlock!A{chosen['_excel_row']}:C{chosen['_excel_row']}",
                   f"PriceCheatSheet!E{price['_excel_row']}; trunk r7502"])
    # Current server explicitly moves the historical L70 unlock to L75.
    bet_anchors = {r[0]: r[1] for r in old['cf_unlocks'] if r[0] <= 1500}
    bet_anchors.pop(70)
    bet_anchors[75] = next(r[1] for r in old['cf_unlocks'] if r[0] == 70)
    for r in cf['cf'][5:50]:
        if r[0] == 6 or r[1] != cf['cf'][r[0]-2][1]:
            bet_anchors[r[0]] = r[1]
    # Avoid obsolete historical change levels inside the current covered interval.
    bet_anchors.pop(9, None)
    cf_rows = []
    for level in range(1, 1501):
        h = old['cf'][level-1] if level <= 300 else None
        recent = cf['cf'][level-1] if level <= 124 else None
        stage = max(k for k in bet_anchors if k <= level)
        bet = bet_anchors[stage]
        if h is not None:
            bet = min(bet, old['calculations'][level-1]['official_bet'])
        if 5 <= level <= 50:
            bet = cf['cf'][5][1] if level == 5 else recent[1]
        # At 51-74 the current L50 interval takes precedence over old L70.
        if 51 <= level < 75:
            bet = cf['cf'][49][1]
        observed_delta = cf['cf'][level][3] if 6 <= level <= 49 else None
        multiplier = recent[2] if 2 <= level <= 124 else (h[3] if h else None)
        status = ('9/22实测区间＋标准EXP模型' if observed_delta is not None
                  else '旧正式表参考' if level <= 300 else '尾段拟合')
        bet_status = ('9/22实测金额' if 6 <= level <= 50 else
                      '9/22 L5–9区间推定' if level == 5 else
                      '9/22档位区间延续' if 51 <= level < 75 else
                      '旧表金额＋9/22解锁等级' if 75 <= level < 100 else '旧正式表解锁档')
        mult_status = ('9/22服务器倍率' if 2 <= level <= 124 else
                       '旧正式表倍率' if level <= 300 else '拟合，非解锁配置')
        cf_rows.append([level, bet, h[2] if h else None, observed_delta,
                        multiplier, status, bet_status, mult_status,
                        f'cashFrenzy等级!A{level+1}:I{level+1}' if h else '历史L251–300门槛趋势',
                        f'9/22实测到达L{level+1}' if observed_delta else ''])
    # Preserve known points. Fit ONLY the absent tail, in EXP (not CR points).
    historical_need = {r[0]: r[1]*r[2]/3 for r in cf_rows[250:300]}
    anchor = historical_need[300]
    numerator = sum((l-300)*(v-anchor) for l, v in historical_need.items())
    denominator = sum((l-300)**2 for l in historical_need)
    slope = numerator/denominator
    assert slope > 0
    # Multiplier tail: retain all old values through300, then last two changes.
    changes = [(r[0], r[3]) for i, r in enumerate(old['cf']) if i == 0 or r[3] != old['cf'][i-1][3]]
    previous, last = changes[-2:]
    mult_slope = (last[1]-previous[1])/(last[0]-previous[0])
    assert last[0] == 300 and mult_slope > 0
    # Known max-Bet change levels only; always retain the requested endpoint.
    overview = {1, 1500}
    for i in range(1, 1500):
        if cr[i][3] != cr[i-1][3] or cf_rows[i][1] != cf_rows[i-1][1]:
            overview.add(i+1)
    data = {'revision': lock['revision'], 'read_time': lock['read_time_utc'], 'cr': cr,
            'cf': cf_rows, 'vip': [[r['vipLevel'], r['needExp']] for r in tables['VipCfg']['records']],
            'cr_packages': [[i, vip_coin[f'vip_16_{i}'], vip_coin['vip_16_0']] for i in range(16)],
            'cr_vip_points_usd': vip_price['vip_16_0'], 'cf_vip': cf['cf_vip'],
            'cf_packages': cf['cf_packages'], 'shops': cf['shops'],
            'overview': sorted(overview), 'fit': {'window':[251,300], 'anchor_level':300,
                'exp_anchor':anchor, 'exp_slope':slope, 'mult_previous':previous,
                'mult_last':last, 'mult_slope':mult_slope},
            'source_files':[history.name,'cf-confirmed-reference.controlled.json','trunk r7502 7表'],
            'boundary': '到达L7–50为实测区间；当前L50开始升级需求改用历史参考。混合来源不代表当前CF服务器表。'}
    expected = []
    for c, f in zip(cr, cf_rows):
        level = c[0]
        need = f[3] if f[3] is not None else f[1]*f[2]/3 if level <= 300 else anchor+slope*(level-300)
        mult = f[4] if f[4] is not None else math.floor(last[1]+mult_slope*(level-300)+0.5)
        cspin = c[2] if c[1] == 1 else c[2]/c[4]
        fspin = need/(f[1]/3)
        expected.append([level,c[3],f[1],cspin,fspin,cspin*c[3]/c[5],fspin*f[1]/(500000*mult),c[5]/c[6],mult,need])
    assert all(all(v > 0 for v in r[1:]) for r in expected)
    assert all(b[2]>=a[2] for a,b in zip(expected,expected[1:]))
    summary = {'levels':1500,'current_measured_upgrade_intervals':44,'historical_until':300,
               'fitted_tail_levels':1200,'max_bet_fitted':False,'overview_rows':len(overview),
               'tail_exp_slope_positive':slope>0,'source_write':False,'configuration_write':False,
               'model_boundary_levels':[6,49,50,51,74,75,124,125,299,300,301,1500],
               'cr_vip_multiplier_current_max': max(r[1]/r[2] for r in data['cr_packages'])}
    save(out/'inputs.controlled.json',data)
    save(out/'expected.controlled.json',expected)
    save(out/'preparation-validation.json',summary)
    return summary


def verify(out: Path) -> dict:
    data=read(out/'inputs.controlled.json')
    book=data.get('book',BOOK)
    pop='pop' in data
    core='CALC_CR_CF' if pop else '等级明细'
    sanitize(out,book)
    f = openpyxl.load_workbook(out/book, read_only=False, data_only=False)
    v = openpyxl.load_workbook(out/book, read_only=False, data_only=True)
    expected = read(out/'expected.controlled.json')
    for row in expected:
        level = row[0]
        got = [v[core].cell(level+5,c).value for c in range(1,11)]
        for a,b in zip(got,row):
            assert isinstance(a,(int,float)) and math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-7),(level,a,b)
    if pop:
        for row in read(out/'pop-expected.controlled.json'):
            level=row[0]
            got=[v['POP模型'].cell(level+5,c).value for c in range(1,11)]
            assert all(isinstance(a,(int,float)) and math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-6) for a,b in zip(got,row)),(level,got,row)
            base=expected[level-1]
            front=[v['等级明细'].cell(level+5,c).value for c in range(1,14)]
            want=[level,base[1],base[2],row[1],base[3],base[4],row[3],base[5],base[6],row[4],base[7],base[8],'N/A']
            assert all(a==b if isinstance(b,str) else math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-6) for a,b in zip(front,want)),level
        for i,r in enumerate(data['pop']['vip']):
            assert v['VIP门槛'].cell(i+6,7).value==r[1]
            assert math.isclose(v['VIP门槛'].cell(i+6,8).value,r[1]/80)
            bonus=r[2] if r[2] is not None else data['pop']['vip'][3][2]+(i-3)*(data['pop']['vip'][3][2]-data['pop']['vip'][2][2])
            assert math.isclose(v['VIP倍率'].cell(i+7,5).value,1+bonus)
    errors = []
    for s in v:
        for row in s:
            for cell in row:
                if cell.data_type == 'e': errors.append((s.title,cell.coordinate,cell.value))
    assert not errors,errors[:10]
    assert all(s.freeze_panes is None for s in f)
    charts = sum(len(s._charts) for s in f)
    assert charts == (7 if pop else 6),charts
    with ZipFile(out/book) as z:
        assert not any(n.startswith('xl/externalLinks/') for n in z.namelist())
        ns={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
        pts=[]
        for name in z.namelist():
            if '/charts/' in name and name.endswith('.xml'):
                root=ET.fromstring(z.read(name))
                for ser in root.findall('.//c:ser',ns):
                    assert ser.find('.//c:f',ns) is not None
                    for ref in ser.findall('.//c:numRef',ns):
                        formula=ref.find('c:f',ns).text
                        sn,area=formula.rsplit('!',1)
                        sn=sn.strip("'").replace("''", "'")
                        a,b,c,e=openpyxl.utils.range_boundaries(area)
                        source=[v[sn].cell(r,k).value for r in range(b,e+1) for k in range(a,c+1)]
                        points=ref.findall('c:numCache/c:pt',ns)
                        assert len(points)==len(source),(formula,len(points),len(source))
                        assert all(math.isclose(float(p.find('c:v',ns).text),source[int(p.attrib['idx'])],rel_tol=1e-12,abs_tol=1e-9) for p in points)
                pts.append([int(p.attrib['val']) for p in root.findall('.//c:val//c:ptCount',ns)])
        assert len(pts) == charts and sum(p == [1500]*len(p) for p in pts if p) == (5 if pop else 4),pts
    summary={'levels_checked':1500,'formula_errors':0,'charts':charts,
             'chart_point_counts':pts,'external_links':0,'frozen_panes':0,
             'native_WPS_open':'not performed','model_is_current_CF_configuration':False,
             'pop_model_verified':pop,'pop_high_level_is_observed':False}
    f.close();v.close();save(out/'validation-summary.json',summary)
    return summary


def cache_charts(out: Path) -> dict:
    """Artifact export omits native chart caches. Fill only those missing caches.

    Cell/formula authoring stays in Artifact. The source-linked chart formulas,
    style and worksheet parts are preserved; cached points come from the actual
    recalculated XLSX cells, never from a parallel business calculation.
    """
    book=out/read(out/'inputs.controlled.json').get('book',BOOK)
    values=openpyxl.load_workbook(book,read_only=False,data_only=True)
    namespace='http://schemas.openxmlformats.org/drawingml/2006/chart'
    ns={'c':namespace}
    tag=lambda n:f'{{{namespace}}}{n}'
    temp=out/'chart-cache.tmp'
    count=0
    with ZipFile(book) as old, ZipFile(temp,'w') as new:
        for item in old.infolist():
            raw=old.read(item.filename)
            if '/charts/' in item.filename and item.filename.endswith('.xml'):
                root=ET.fromstring(raw)
                for kind,cache_kind in [('numRef','numCache'),('strRef','strCache')]:
                    for ref in root.findall('.//c:'+kind,ns):
                        formula=ref.find('c:f',ns).text
                        sheet_name,area=formula.rsplit('!',1)
                        sheet_name=sheet_name.strip("'").replace("''", "'")
                        a,b,c,e=openpyxl.utils.range_boundaries(area)
                        cells=[values[sheet_name].cell(r,k).value for r in range(b,e+1) for k in range(a,c+1)]
                        cache=ref.find('c:'+cache_kind,ns)
                        if cache is None: cache=ET.SubElement(ref,tag(cache_kind))
                        for child in list(cache):
                            if child.tag!=tag('formatCode'): cache.remove(child)
                        ET.SubElement(cache,tag('ptCount'),{'val':str(len(cells))})
                        for i,value in enumerate(cells):
                            assert value is not None,(formula,i)
                            if kind=='numRef': assert isinstance(value,(int,float)),(formula,i,value)
                            p=ET.SubElement(cache,tag('pt'),{'idx':str(i)})
                            ET.SubElement(p,tag('v')).text=str(value)
                        count+=1
                raw=ET.tostring(root,encoding='utf-8',xml_declaration=True)
            new.writestr(item,raw)
    values.close();temp.replace(book)
    result={'native_chart_reference_caches_filled':count,'worksheet_parts_changed':0}
    save(out/'chart-cache-receipt.json',result)
    return result


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','prepare-pop','cache-charts','verify'])
    parser.add_argument('--baseline',type=Path)
    parser.add_argument('--pop-source',type=Path)
    parser.add_argument('--current',type=Path)
    parser.add_argument('--history',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    result=(prepare_pop(args.baseline,args.pop_source,args.history,args.out) if args.action=='prepare-pop'
            else prepare(args.current,args.history,args.out) if args.action=='prepare'
            else cache_charts(args.out) if args.action=='cache-charts' else verify(args.out))
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':
    main()
