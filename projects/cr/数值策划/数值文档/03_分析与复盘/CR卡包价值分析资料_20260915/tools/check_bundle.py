"""复核配置副本、CSV一致性、当前季引用和卡组状态覆盖。仅使用 Python 3 标准库。

运行：python tools/check_bundle.py
"""
from __future__ import annotations
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any
from extract_xlsx import extract, records

ROOT=Path(__file__).resolve().parents[1]

def read_table(environment: str, name: str) -> list[dict[str, Any]]:
    return records(extract(ROOT/'config'/environment/f'{name}.xlsx'))

def number(value: Any) -> int:
    return int(value or 0)

def audit_environment(env: str) -> dict[str, Any]:
    albums=read_table(env,'CardAlbumCfg')
    album=next(x for x in albums if x['id']==2)
    chapters=read_table(env,'CardChapter')
    cards=read_table(env,'CardList')
    packs=[x for x in read_table(env,'CardPack') if x['season']==2]
    chapter_ids={x['id'] for x in chapters if x['seasonId']==2}
    by_chapter=defaultdict(list)
    for card in cards:
        if card['seasonId']==2: by_chapter[card['cardChapter']].append(card)
    assert len([x for x in cards if x['seasonId']==2])==album['prestigeCardNum']
    assert len([x for x in cards if x['seasonId']==2 and not x['isPrestige']])==album['cardNum']
    assert all(len(by_chapter[x['id']])==x['cardNum'] for x in chapters if x['seasonId']==2)
    groups=[x for x in read_table(env,'CardGroup') if x['chapterId'] in chapter_ids]
    by_group=defaultdict(list)
    for group in groups:
        by_group[group['group']].append(group)
    patterns=defaultdict(list)
    count_mismatch=[]
    for pack in packs:
        total=0
        for slot in range(1,6):
            t,st,g,n=[number(pack[f'{field}{slot}']) for field in ['type','star','group','num']]
            if t>=0 and st>0 and g>0 and n>0:
                patterns[(t,st,g,n)].append({'rule_id':pack['id'],'pack':pack['pack'],'slot':slot})
                total+=n
        total+=sum(number(pack[f'cardId{i}'])>0 for i in range(1,4))
        if total!=number(pack['cardNum']): count_mismatch.append(pack['id'])
    # 筛选器均为闭区间。只在上下边界或下一格改变候选集，遍历等价区间即可覆盖整域。
    days=sorted({0,60}|{number(x[k])+offset for x in groups for k,offset in [('seasonDayMin',0),('seasonDayMax',1)] if 0<=number(x[k])+offset<=60})
    progress=sorted({0,169}|{number(x[k])+offset for x in groups for k,offset in [('progMin',0),('progMax',1)] if 0<=number(x[k])+offset<=169})
    empty=[];short=[];group_empty=[];tested=0
    for (typ,star,group_id,n),rule_slots in patterns.items():
        for prestige in [False,True]:
            for day in days[:-1]:
                for prog in progress[:-1]:
                    tested+=1
                    eligible=[x for x in by_group[group_id] if x['seasonDayMin']<=day<=x['seasonDayMax'] and x['progMin']<=prog<=x['progMax'] and (prestige or not x['isPrestige']) and x['weight']>0]
                    state={'type':typ,'star':star,'group':group_id,'num':n,'day':day,'progress':prog,'prestige':prestige}
                    if not eligible:
                        empty.append(state);continue
                    candidates=set()
                    for g in eligible:
                        cs=[c for c in by_chapter[g['chapterId']] if (typ==0 or c['type']==typ) and c['starLevel']==star]
                        if not cs: group_empty.append({**state,'chapter':g['chapterId']})
                        candidates.update(c['cardId'] for c in cs)
                    if len(candidates)<n:
                        short.append({**state,'candidate_count':len(candidates),'rule_slots':rule_slots})
    return {'season_id':2,'season_day_domain':[0,59],'unique_count_domain':[0,168],
            'method':'闭区间筛选的等价状态区间代表点，含普通/高阶两种状态；不是玩家分布或实机模拟。',
            'tested_pattern_states':tested,'no_positive_group_states':len(empty),'empty_chapter_candidate_states':len(group_empty),
            'candidate_shortage_states':len(short),'shortage_examples':short[:10],
            'affected_rule_slots':sorted({(s['rule_id'],s['pack'],s['slot']) for x in short for s in x['rule_slots']}),
            'declared_card_count_mismatch_rule_ids':count_mismatch,
            'limits':'候选全集不足是确定性容量风险。未统计21次重抽耗尽概率、跨槽位候选重叠或玩家权重导致的实际少发概率。'}

def main() -> None:
    manifest=json.loads((ROOT/'sources.json').read_text(encoding='utf-8'))
    cells=0
    for meta in manifest:
        path=ROOT/meta['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['sha256'],meta['file']
        rows=records(extract(path))
        with (ROOT/meta['text_file']).open(encoding='utf-8',newline='') as stream:
            textrows=list(csv.DictReader(stream))
        assert len(rows)==len(textrows)==meta['rows']
        for row,textrow in zip(rows,textrows):
            for key,value in row.items():
                assert textrow[key]==('' if value is None else str(value)),(meta['file'],row['_excel_row'],key)
                cells+=1
    result={'verified_xlsx_files':len(manifest),'verified_csv_cells':cells,'environments':{e:audit_environment(e) for e in ['trunk','dev']}}
    (ROOT/'checks'/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({**{k:v for k,v in result.items() if k!='environments'},'environments':{e:{k:v for k,v in x.items() if k not in ['shortage_examples','affected_rule_slots']} for e,x in result['environments'].items()}},ensure_ascii=False))

if __name__=='__main__':
    main()
