"""只读盘点固定 revision 的 CR trunk 工作簿；输出必须位于 Git 仓库外。

python inventory_all_numerics.py --input <锁定trunk目录> --lock <source-lock.json> --output <受控目录>
复用卡包资料的 XLSX 提取器，不读取旧资料中的数值，不重存源 Excel，不计算文件哈希。
"""
from __future__ import annotations
import argparse,csv,gzip,importlib.util,json,re,sys
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

CR_ROOT=Path(__file__).resolve().parents[2]
EXTRACT_PATH=CR_ROOT/'数值策划/数值文档/03_分析与复盘/CR卡包价值分析资料_20260915/tools/extract_xlsx.py'

def extractor()->Callable[[Path],dict[str,Any]]:
    spec=importlib.util.spec_from_file_location('cr_existing_xlsx_reader',EXTRACT_PATH)
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.extract

def category(name:str)->str:
    rules=[(r'^(Snack)','薯片'),(r'^StrikeLucky','777'),(r'^QuestBoxing','拳击'),(r'^QuestMiner','挖矿'),
           (r'^Quest','活动共用及其他Quest'),(r'^(Card|DeskDropCards|SlotsCasinoDropCards)','卡包卡册'),
           (r'^(SlotsCasinoCommResult|SlotsCasinoSpecialResult|SlotsCasinoSafeResult|SlotsRtpIndex|NewSlot|SlotAward)','机台奖励'),
           (r'^(SlotsCasino|SlotsHall|BigWin|SlotsStage|SlotCost|SlotLevel|TrainSlot)','Bet与RTP'),
           (r'^(Level|Vip|vip)','等级与VIP'),(r'^(BP|BattlePass|CommonBP|FunBP|Funpass)','Pass'),
           (r'^(Pay|Bag|DealOffer|ChallengeBag|PiggyBank|WeeklyCard|OnePlusSix|Market)','商城礼包'),
           (r'^(Free|Novice|Online|Sign|FirstFriend|FriendRank|NewInvite|LinkReward|ShareFB|VersionUpdateCompensate|RoomFree)','免费福利'),
           (r'^(Item|GiftItem|PlayerInitItem|Price|Diamond|CommonDiamond|ChipSpin|CommCfg|CommParam|DefaultValue)','资源与价值换算'),
           (r'^(Build|Building|Palace|Voyage|CashRoyalTask|TaskDesc|FrenzyMission|MissionBooster|DailyTreasure|SysUnlock|ModuleNames|RoomUnlock|Role)','任务建造与常驻系统'),
           (r'^(Activity|Raffle|Ring|Treasure|Lottery|Champion|Challenge|WinChallenge|Luck|Lucky|Aladdin|DuoBao|Ramadan|FunStamp|Stampit)','其他活动'),
           (r'^(League|Lounge|NewLeague|Match|NewMatch|Contest|Rank|SuperMatch|Cash|Spades|Horse|Racecourse|Circus|DragonTiger|Roulette|SuperRoulete|Room|Desk|FriendRoom|CatchPrize|Pve|Team|Mvp|TwoHundred)','同trunk其他玩法/归属待确认')]
    return next((v for p,v in rules if re.search(p,name)), '其他配置/归属待确认')

def unit(comment:str,field:str)->str:
    if '万分比' in comment:return '万分比；分母10000'
    if '千分比' in comment:return '千分比；分母1000'
    if '除以100' in comment:
        if '美元' in comment:return '配置美元×100；非实付'
        if '里拉' in comment:return '配置里拉×100；非实付'
        return '缩放值；分母100，具体单位按字段'
    if '百分比' in comment:return '百分数；分母100'
    if '美元*100' in comment or '美金*100' in comment:return '配置美元×100；非实付'
    if '美金' in comment or '美元' in comment:return '配置价值；精度/类型按关联确认'
    if '秒' in comment:return '秒'
    if '小时' in comment:return '小时'
    if '天' in comment:return '天/日期条件（见字段说明）'
    if '权重' in comment:return '相对权重；按有效池归一'
    if '金币' in comment or '筹码' in comment:return '金币（如为枚举/价值转换须结合类型）'
    if '钻石' in comment:return '钻石/枚举（见字段说明）'
    if any(x in comment for x in ['经验','积分']):return '经验/积分（见字段说明）'
    if '数量' in comment or field.lower().endswith(('count','num')):return '数量（资源类型待关联）'
    return '未声明；保留原值'

def dump_csv(path:Path,fields:list[str],rows:list[dict[str,Any]])->None:
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True);p.add_argument('--lock',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();gitroot=CR_ROOT.parents[1]
    if out==gitroot or gitroot in out.parents:raise ValueError('完整数值产物不得写入 public Git 工作树')
    lock=json.loads(a.lock.read_text(encoding='utf-8'))
    if lock.get('environment')!='trunk' or not isinstance(lock.get('revision'),int):raise ValueError('需要锁定的 trunk revision')
    out.mkdir(parents=True,exist_ok=True);normalized=out/'normalized';normalized.mkdir(exist_ok=True)
    extract=extractor();tables=[];fields=[];issues=[];formula_count=0;missing_cache=0;cells_total=0
    # Nonempty named cells and formula cells remain in long-form output; blanks are not zero.
    with gzip.open(out/'全系统数值明细.csv.gz','wt',encoding='utf-8-sig',newline='') as f:
        cols=['系统','表名','Sheet','行ID','Excel行','字段','单元格','现行值','原公式','字段说明','单位','适用条件','revision']
        writer=csv.writer(f);writer.writerow(cols)
        files=sorted(a.input.glob('*.xlsx'))
        for index,path in enumerate(files,1):
            # Never normalize known identity/operational message tables even if present in a read cache.
            if path.stem in {'AwardEmail','InstantSettlementBotRecharge'}:continue
            try:d=extract(path)
            except Exception as e:
                issues.append({'file':path.name,'type':'read_error','detail':type(e).__name__});continue
            payload={'file':path.name,'revision':lock['revision'],'system':category(path.stem),'sheets':[]}
            for sheet in d['sheets']:
                rows={r['row']:r['cells'] for r in sheet['rows']}
                headers=rows.get(1,{})
                mapped=[];counts=Counter()
                for ref,cell in headers.items():
                    value=cell['value'];col=re.sub(r'\d','',ref)
                    if not isinstance(value,str) or not value.strip():continue
                    name=value.strip();counts[name]+=1
                    mapped.append({'column':col,'field':name,'key':name if counts[name]==1 else name+'@'+col,'type':rows.get(2,{}).get(col+'2',{}).get('value'),
                                   'export':rows.get(3,{}).get(col+'3',{}).get('value'),'comment':str(rows.get(4,{}).get(col+'4',{}).get('value') or '')})
                valid=bool(mapped) and any(str(x['type']).lower() in ['int','long','float','double','string','bool','int64','uint','ulong'] for x in mapped)
                if not valid:
                    tables.append({'系统':payload['system'],'表名':path.name,'Sheet':sheet['name'],'行数':max(0,len(sheet['rows'])-4),'字段数':len(mapped),'状态':'辅助页/无标准配置头，不参与现行复算','revision':lock['revision']});continue
                rs=[];filled=Counter();numbers={x['key']:[] for x in mapped}
                for n,cs in rows.items():
                    if n<=4:continue
                    record={'_excel_row':n};formulas={}
                    for meta in mapped:
                        col,key=meta['column'],meta['key'];cell=cs.get(col+str(n),{})
                        value=cell.get('value');record[key]=value
                        if cell.get('formula'):
                            formulas[key]=cell['formula'];formula_count+=1
                            if value is None:missing_cache+=1
                        if value is not None:filled[key]+=1
                        if isinstance(value,(int,float)) and not isinstance(value,bool):numbers[key].append(value)
                    if not any(v is not None for k,v in record.items() if k!='_excel_row'):continue
                    if formulas:record['_formulas']=formulas
                    idkeys=[x['key'] for x in mapped if x['field'].lower().endswith(('id','index')) or x['field'].lower() in ['level','vip','viplevel','turn','round','questtype','money','pricetype','viptype','orbit','stage','key','pack','season','category','boxnum','luck','row','inout','weighttype','paytype','eventgroup','chapter','passtype']]
                    rid=';'.join(f'{k}={record[k]}' for k in idkeys if record.get(k) is not None) or f'Excel行={n}'
                    record['_row_id']=rid
                    cond=';'.join(f'{k}={record[k]}' for k in idkeys if k.lower() not in ['id','itemid','key'] and record.get(k) is not None)
                    for meta in mapped:
                        key=meta['key'];v=record[key]
                        if v is None and key not in formulas:continue
                        writer.writerow([payload['system'],path.name,sheet['name'],rid,n,meta['field'],meta['column']+str(n),v,formulas.get(key,''),meta['comment'],unit(meta['comment'],meta['field']),cond,lock['revision']]);cells_total+=1
                    rs.append(record)
                payload['sheets'].append({'name':sheet['name'],'fields':mapped,'records':rs})
                tables.append({'系统':payload['system'],'表名':path.name,'Sheet':sheet['name'],'行数':len(rs),'字段数':len(mapped),'状态':'已读取；在trunk存在不等于本期启用','revision':lock['revision']})
                for meta in mapped:
                    ns=numbers[meta['key']]
                    fields.append({'系统':payload['system'],'表名':path.name,'Sheet':sheet['name'],'字段':meta['field'],'列':meta['column'],'类型':meta['type'],'端标记':meta['export'],'说明':meta['comment'],'单位':unit(meta['comment'],meta['field']),'非空行数':filled[meta['key']],'数值最小':min(ns) if ns else None,'数值最大':max(ns) if ns else None,'revision':lock['revision']})
            (normalized/(path.stem+'.json')).write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
            if index%150==0:print(f'normalized {index}/{len(files)}',flush=True)
    dump_csv(out/'全系统配置目录.csv',list(tables[0]),tables)
    dump_csv(out/'全系统字段总表.csv',list(fields[0]),fields)
    result={'revision':lock['revision'],'read_at_utc':lock['read_at_utc'],'workbooks':len(list(normalized.glob('*.json'))),'configuration_sheets':sum(x['状态'].startswith('已读取') for x in tables),'reference_sheets':sum(x['状态'].startswith('辅助') for x in tables),'configuration_rows':sum(x['行数'] for x in tables if x['状态'].startswith('已读取')),'fields':len(fields),'populated_cells':cells_total,'formula_cells':formula_count,'missing_formula_cache':missing_cache,'read_errors':issues,'system_counts':dict(Counter(x['系统'] for x in tables if x['状态'].startswith('已读取'))),'privacy':'project-private; local only','old_values_used':False,'source_modified':False}
    (out/'盘点结果.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
