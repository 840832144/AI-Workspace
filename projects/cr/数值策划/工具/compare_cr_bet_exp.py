"""TASK-0036：只读dev固定导出，比较Bet与反推经验；不写源配置或提交SVN。

prepare --base <受控根> --out <本轮输出>
verify --base <受控根> --out <本轮输出>
XLSX及原生图表由配套ArtifactJS生成，原生Excel回算并导出预览。
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import openpyxl
from producer_workbook_sources import read_source
from producer_dashboard_models import max_unlocked

BOOK = 'CR_vs_CF_Bet解锁与经验对照_r7252.xlsx'


def prepare(base: Path, out: Path) -> dict:
    assert not any((p/'.git').exists() for p in (out.resolve(), *out.resolve().parents))
    receipt = json.loads((out/'source.local.json').read_text(encoding='utf-8-sig'))
    assert receipt['environment'] == 'CR dev' and receipt['revision'] == 7252
    source = out/'source'
    levels = read_source(source/'LevelCfg.xlsx')['records']
    bets = read_source(source/'SlotsCasinoBetList.xlsx')['records']
    by_id = {r['levelId']: r for r in bets}
    unlocks = read_source(source/'SlotsCasinoBetUnlock.xlsx')['records']
    prices = [r for r in read_source(source/'PriceCheatSheet.xlsx')['records']
              if (r['money'], r['priceType'], r['vipType']) == (100, 17, 1)]
    assert next(r['val'] for r in read_source(source/'CommCfg.xlsx')['records'] if r['id'] == 161) == 1
    w = openpyxl.load_workbook(base/'CashRoyal数值.xlsx', read_only=True, data_only=True)
    rows = list(w['cashFrenzy等级'].values)
    cf_base, cf_loss = rows[1][24], rows[1][23]
    cf_unlocks = [[r[36], r[35], f'cashFrenzy等级!AJ{i}:AK{i}']
                  for i, r in enumerate(rows[1:], 2) if isinstance(r[35], (int, float))]
    cf = [[r[0],r[1],r[2],r[8],r[6],f'cashFrenzy等级!A{i}:I{i}'] for i,r in enumerate(rows[1:],2)]
    assert [r[0] for r in cf] == list(range(1,301))
    # 沿用已Accepted的CF缓存，不重新验收其他系统/模型。
    w.close()
    cr, calculations = [], []
    for r in levels:
        lv = r['level']
        unlock = max_unlocked(unlocks,lv)
        bet = by_id[unlock['betlevel']]
        price = max((p for p in prices if p['level'] <= lv), key=lambda p:p['level'])
        mode, threshold, exp, coin, rate = r['levelUpType'] or 0, r['levelUpExp'], bet['levelExp'], bet['bet2'], price['vip_16_0']
        cf_bet = max(b for l,b,_ in cf_unlocks if l <= lv)
        official_bet = min(cf_bet,cf[lv-1][1]) if lv<=300 else cf_bet
        ref_bet=next(b for b in bets if b['bet2']==official_bet)
        exp=ref_bet['levelExp']
        cr.append([lv,mode,threshold,ref_bet['levelId'],coin,exp,rate,
                   f'LevelCfg!C{r["_excel_row"]}',f'SlotsCasinoBetList!E{ref_bet["_excel_row"]}:F{ref_bet["_excel_row"]}',
                   f'SlotsCasinoBetUnlock!A{unlock["_excel_row"]}:C{unlock["_excel_row"]}',
                   f'PriceCheatSheet!row{price["_excel_row"]}',cf_bet,official_bet])
        spins = threshold if mode == 1 else math.ceil(threshold/exp)
        calculations.append({'level':lv,'dev_bet':coin,'dev_exp':exp,'dev_cost':spins*official_bet/rate*.05 if lv<5000 else None,
                             'cf_main_bet':cf[lv-1][1] if lv<=300 else None,'cf_unlock_bet':cf_bet,
                             'official_bet':official_bet,
                             'cf_cost':official_bet*cf[lv-1][2]*cf_loss/cf_base/cf[lv-1][3] if lv<=300 else None,
                             'inferred_exp':threshold/cf[lv-1][2] if mode==0 and lv<=300 else None})
    assert [r[0] for r in cr] == list(range(1,5001))
    tiers=[]
    tier_sources={coin:(lv,coord) for lv,coin,coord in cf_unlocks}
    for r in cr[:300]:
        if r[12] not in tier_sources:
            tier_sources[r[12]]=(r[0],f'cashFrenzy等级!B{r[0]+1}（User保守选择）')
    for coin,(lv,coord) in sorted(tier_sources.items()):
        bet = next(r for r in bets if r['bet2']==coin)
        first = min(r['level'] for r in unlocks if r['highroller']==0 and r['betlevel']==bet['levelId'])
        target_first = 0 if lv==0 else next(r[0] for r in cr if r[0]>=lv and r[12]>=coin)
        tiers.append([lv,coin,bet['levelId'],first,bet['levelExp'],coord,target_first])
    groups=[]
    for method in ('official',):
        key='official_bet'
        for coin in sorted({r[key] for r in calculations[:300] if r['inferred_exp'] is not None}):
            members=[r for r in calculations[:300] if r[key]==coin and r['inferred_exp'] is not None]
            values=[r['inferred_exp'] for r in members]
            groups.append({'method':method,'bet':coin,'levels':[r['level'] for r in members],
                           'min':min(values),'max':max(values),'conflict':not math.isclose(min(values),max(values),rel_tol=1e-10)})
    # 游戏只能执行整次Spin：另列ceil(CF期望Spin)的配置模拟，不冒称CF实测次数。
    candidates=[]
    for b in bets:
        group=next((g for g in groups if g['bet']==b['bet2']),None)
        if group:
            bounds=[]
            for lv in group['levels']:
                need=cr[lv-1][2]; turns=math.ceil(cf[lv-1][2])
                bounds.append((math.ceil(need/turns),math.ceil(need/(turns-1))-1 if turns>1 else None))
            lower=max(x[0] for x in bounds)
            finite=[x[1] for x in bounds if x[1] is not None]
            upper=min(finite) if finite else None
            assert upper is None or lower<=upper,'不能默默拟合无法实现的整Spin目标'
            proposed=max(b['levelExp'],lower)
            if upper is not None:proposed=min(proposed,upper)
            levels_for_bet=group['levels']
        else:
            lower=upper=None; proposed=b['levelExp'];levels_for_bet=[]
        candidates.append({'id':b['levelId'],'bet':b['bet2'],'current_exp':b['levelExp'],'lower':lower,'upper':upper,
                           'proposed_exp':proposed,'levels':levels_for_bet,'source_cell':f'SlotsCasinoBetList!E{b["_excel_row"]}',
                           'status':'整Spin模型候选' if group else '缺同级对标点，保留现值'})
    by_coin={r['bet']:r for r in candidates}
    for r in calculations:
        lv=r['level'];v=cr[lv-1];candidate=by_coin[r['official_bet']]['proposed_exp']
        r['candidate_exp']=candidate
        r['candidate_spins']=(v[2] if v[1]==1 else math.ceil(v[2]/candidate)) if lv<5000 else None
        r['cf_ceil_spins']=math.ceil(cf[lv-1][2]) if lv<=300 else None
        r['candidate_cost']=r['candidate_spins']*r['official_bet']/v[6]*.05 if lv<5000 else None
    conflicts=[r['level'] for r in calculations[:300] if r['cf_main_bet']!=r['cf_unlock_bet']]
    data={'revision':7252,'read_at_utc':receipt['read_at_utc'],'cr':cr,'cf':cf,'cf_unlocks':cf_unlocks,
          'tiers':tiers,'groups':groups,'candidates':candidates,'cf_base':cf_base,'cf_loss':cf_loss,'cr_loss':.05,
          'source_conflicts':conflicts,'calculations':calculations,
          'authority':{'bet_unit':'literal coins, same level; User confirmed',
                       'cf_bet_source':'User: conflicting sources use lower coin Bet; originals retained',
                       'experience':'User authorized inference: dev threshold / CF historical Spin; not CF raw EXP',
                       'level_cfg':'dev r7252 read-only, preserve all cells','svn_submission':'not authorized'}}
    (out/'comparison-inputs.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'levels':len(cr),'cf_levels':len(cf),'CF_unlocks':len(tiers),'source_conflict_levels':len(conflicts),
            'EXP_conflicting_groups':sum(g['conflict'] for g in groups),
            'mode1_levels':[r[0] for r in cr[:300] if r[1]==1],
            'integer_spin_matches':sum(r['candidate_spins']==r['cf_ceil_spins'] for r in calculations[:300]),
            'candidate_EXP_cells':sum(r['proposed_exp']!=r['current_exp'] for r in candidates),'source_writes':0}


def verify(out: Path) -> dict:
    d=json.loads((out/'comparison-inputs.json').read_text(encoding='utf-8'))
    w=openpyxl.load_workbook(out/BOOK,data_only=False)
    c=openpyxl.load_workbook(out/BOOK,data_only=True)
    formulas=0
    for s in w:
        for row in s:
            for cell in row:
                if cell.data_type=='f':
                    formulas+=1
                    cached=c[s.title][cell.coordinate]
                    assert cached.value is not None and cached.data_type!='e',(s.title,cell.coordinate,cached.value)
        assert s.freeze_panes is None
    detail=c['逐级_明细']
    for i,r in enumerate(d['calculations'],5):
        def same(col,expected):
            actual=detail[f'{col}{i}'].value
            if expected is None:assert actual=='N/A',(i,col,actual)
            else:assert math.isclose(actual,expected,rel_tol=1e-10,abs_tol=1e-9),(i,col,actual,expected)
        for col,key in [('A','level'),('E','dev_bet'),('F','dev_exp'),('K','dev_cost'),('M','cf_main_bet'),('O','cf_cost'),('Q','cf_unlock_bet'),('R','official_bet'),('S','inferred_exp'),('Y','cf_ceil_spins'),('Z','candidate_exp'),('AA','candidate_spins'),('AC','candidate_cost')]:
            same(col,r[key])
    candidate_sheet=c['Bet经验_候选']
    for i,r in enumerate(d['candidates'],5):
        assert candidate_sheet[f'G{i}'].value==r['proposed_exp']
        if i>5:
            decreasing=r['proposed_exp']<d['candidates'][i-6]['proposed_exp']
            assert candidate_sheet[f'K{i}'].value==('经验倒挂：不可落表' if decreasing else '未下降')
    tier_sheet=c['Bet档位_明细']
    for i,r in enumerate(d['tiers'],5):assert tier_sheet[f'C{i}'].value==r[6]
    groups=c['经验约束_明细']
    for row,g in enumerate(d['groups'],5):
        for col,key in [('E','min'),('F','max')]:
            assert math.isclose(groups[f'{col}{row}'].value,g[key],rel_tol=1e-10)
        assert groups[f'G{row}'].value==('冲突' if g['conflict'] else '唯一')
    with ZipFile(out/BOOK) as z:
        assert not any(n.startswith('xl/externalLinks/') for n in z.namelist())
        core=ET.fromstring(z.read('docProps/core.xml'))
        assert not any(e.text for e in core if e.tag.rsplit('}',1)[-1] in ('creator','lastModifiedBy'))
        ns={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
        charts=[ET.fromstring(z.read(n)) for n in z.namelist() if n.startswith('xl/charts/chart') and n.endswith('.xml')]
        assert len(charts)==5 and all(x.find('.//c:lineChart',ns) is not None for x in charts)
        point_counts=[]
        for chart in charts:
            point_counts.append([int(s.find('c:val/c:numRef/c:numCache/c:ptCount',ns).attrib['val']) for s in chart.findall('.//c:ser',ns)])
        assert sorted(point_counts)==sorted([[300,300],[5000,5000],[300,300,300],[300,300,300],[296,296,296]]),point_counts
    for s in ('SRC_DEV','SRC_CF','SRC_BET'):assert w[s].sheet_state=='hidden'
    result={'revision':7252,'formula_cells':formulas,'formula_errors':0,'missing_caches':0,'external_links':0,
            'visible_sheets':[s.title for s in w if s.sheet_state=='visible'],'charts':5,
            'levels_compared':5000,'CF_original_levels':300,'inferred_EXP_groups':len(d['groups']),
            'integer_spin_matches':sum(r['candidate_spins']==r['cf_ceil_spins'] for r in d['calculations'][:300]),
            'unchanged_Spin_mode_mismatches':[r['level'] for r in d['calculations'][:300] if r['candidate_spins']!=r['cf_ceil_spins']],
            'proposed_EXP_changes':sum(r['proposed_exp']!=r['current_exp'] for r in d['candidates']),
            'candidate_EXP_decreases':sum(a['proposed_exp']>b['proposed_exp'] for a,b in zip(d['candidates'],d['candidates'][1:])),
            'chart_points':point_counts,'source_writes':0,'configuration_candidate_written':False,
            'full_alignment':'NOT achieved: early Spin-mode / fractional expectation / USD gaps; candidate pending acceptance'}
    w.close();c.close()
    (out/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['prepare','verify']);p.add_argument('--base',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(prepare(a.base,a.out) if a.action=='prepare' else verify(a.out),ensure_ascii=False))
