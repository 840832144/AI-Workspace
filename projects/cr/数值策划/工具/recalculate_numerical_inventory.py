#!/usr/bin/env python3
"""固定 trunk 配置的分系统复算，完整输出仅允许保存在 Git 工作树之外。

先运行 inventory_all_numerics.py；本工具不访问 SVN，不改配置、不做调参。
python recalculate_numerical_inventory.py --input <受控输出目录> --extra <固定版本JSON根>
CSV 保留全条件，Excel 的阅读视图由 workbook-model.json 生成。未明条件不补零。
"""
from __future__ import annotations
import argparse
import csv
import gzip
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

QUEST = {4: '薯片', 5: '777', 8: '拳击', 9: '挖矿'}

def num(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)

def divide(a: Any, b: Any) -> float | None:
    return a / b if num(a) and num(b) and b > 0 else None

def stage_spins(required: Any, gain: Any, probability: Any) -> float | None:
    """固定每次命中积分、独立固定概率、起始0、升级清零条件下的阶段期望。"""
    if not all(num(x) for x in (required, gain, probability)) or required < 0 or gain <= 0 or not 0 < probability <= 1:
        return None
    return math.ceil(required / gain) / probability

def group(rows: list[dict], keys: tuple[str, ...]) -> dict[tuple, list[dict]]:
    out: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        out[tuple(r.get(k) for k in keys)].append(r)
    return out

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--extra', type=Path)
    a = parser.parse_args()
    root = a.input.resolve()
    gitroot = Path(__file__).resolve().parents[4]
    if root == gitroot or gitroot in root.parents:
        raise ValueError('完整数值产物不得写入 public Git 工作树')
    stats = json.loads((root / '盘点结果.json').read_text(encoding='utf-8'))
    revision = stats['revision']
    datasets: dict[str, dict] = {}
    sheets: list[dict] = []
    counts: dict[str, int] = {}
    diagnostics: dict[str, Any] = {}

    def table(name: str) -> dict:
        if name not in datasets:
            d = json.loads((root / 'normalized' / (name + '.json')).read_text(encoding='utf-8'))
            if d['revision'] != revision:
                raise ValueError('拒绝混用 revision: ' + name)
            datasets[name] = d
        return datasets[name]

    def sheet(name: str) -> dict:
        candidates = table(name)['sheets']
        matching = [s for s in candidates if s['name'] == 'Sheet1']
        if matching:
            return matching[0]
        if len(candidates) != 1:
            raise ValueError('多页表必须明确主表: ' + name)
        return candidates[0]

    def rows(name: str) -> list[dict]:
        return sheet(name)['records']

    def ref(name: str, r: dict, fields: str = '') -> str:
        return f'{name}.xlsx/{sheet(name)["name"]}/行{r["_excel_row"]};{r["_row_id"]};{fields};r{revision}'

    def save(name: str, rs: list[dict], title: str | None = None, note: str = '', limit: int | None = None,
             formulas: dict[str, str] | None = None) -> None:
        if not rs:
            counts[name] = 0
            return
        headers = list(dict.fromkeys(k for r in rs for k in r))
        with (root / (name + '.csv')).open('w', encoding='utf-8-sig', newline='') as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
            w.writerows(rs)
        counts[name] = len(rs)
        if title:
            chosen = rs if limit is None else rs[:limit]
            sheets.append({'name': title, 'note': note, 'headers': headers,
                           'rows': [[r.get(k) for k in headers] for r in chosen],
                           'totalRows': len(rs), 'csv': name + '.csv', 'formulas': formulas or {}})

    # Explicit value tiers. Only exact existing rows; never interpolate or use old GetValue logic.
    money_rows = [r for r in rows('PriceCheatSheet') if r['priceType'] == 17 and r['vipType'] == 1 and r['money'] == 100]
    rates = {(r['level'], vip): (r.get('vip_16_' + str(vip)), r) for r in money_rows for vip in range(16)}
    bet = []
    for (level, vip), (coins, rate_row) in rates.items():
        for b in rows('SlotsCasinoBetList'):
            for field in ('bet2', 'bet3', 'bet33', 'bet9', 'bet35'):
                usd = divide(b.get(field), coins)
                bet.append({'等级档': level, 'VIP': vip, 'BetIndex': b['levelId'], 'Bet列': field,
                            '金币下注': b.get(field), '一配置美元金币': coins, '参考美金Bet': usd,
                            'User规则RTP': 0.85 if usd is not None and usd > 1 else 0.95 if usd is not None and usd < 1 else '等于1待确认' if usd == 1 else '换算缺失',
                            '条件': '精确level/VIP；机器Bet列绑定及查档规则待确认；配置折算非实付',
                            '来源': ref('SlotsCasinoBetList', b, field) + ' | ' + ref('PriceCheatSheet', rate_row, 'vip_16_' + str(vip))})
    save('复算_Bet全条件', bet)
    first_context = (min(rates)[0], min(rates)[1])
    save('复算_Bet阅读示例', [r for r in bet if (r['等级档'], r['VIP']) == first_context], 'Bet换算',
         '仅配置首个等级/VIP档的五种Bet列；全档见复算_Bet全条件.csv。不是机器绑定结论。',
         formulas={'G': '=IF(F{r}>0,E{r}/F{r},"缺口")', 'H': '=IF(ISNUMBER(G{r}),IF(G{r}>1,0.85,IF(G{r}<1,0.95,"等于1待确认")),"缺口")'})
    switches = rows('SlotsCasinoResultSwitchStrategy')
    diagnostics['rtp_raw_distribution'] = dict(Counter(str(r.get('rtp')) for r in switches))
    diagnostics['usd_reference_exact_one_rows'] = sum(r['参考美金Bet'] == 1 for r in bet)
    save('RTP门槛配置', [{'机台':r['machineId'],'等级档':r['level'],'VIP':r['vip'],'betIndex门槛':r['betIndex'],
         'spinNum':r['spinNum'],'rtp原值':r['rtp'],'说明':r.get('name'),'来源':ref('SlotsCasinoResultSwitchStrategy',r)} for r in switches])

    # Acquisition matrices factorize level/VIP/Bet and stage to avoid inventing a player distribution.
    picks = {(r['questType'], r['Id']):r for r in rows('QuestPickGet') if r['Type'] == 2 and r['questType'] in QUEST}
    acquisition = []
    for p in rows('QuestPointsCheatSheet'):
        key = (p['questType'], p['Id'])
        if key not in picks:
            continue
        src = picks[key]
        prob = divide(src['Probability'], 1000)
        for vip in range(16):
            gain = p.get('vip_16_' + str(vip))
            acquisition.append({'活动':QUEST[key[0]],'questType':key[0],'Id':key[1],'等级档':p['level'],'VIP':vip,
                                'BetIndex':src['BetId'],'毛下注金币每Spin':src['bet'],'概率千分值':src['Probability'],
                                '条件命中积分':gain,'条件积分期望每Spin':prob * gain if num(prob) and num(gain) else None,
                                '来源':ref('QuestPickGet',src,'Probability,bet,BetId')+' | '+ref('QuestPointsCheatSheet',p,'vip_16_'+str(vip)),
                                '限制':'须确认积分是命中后数值且单次独立；不把积分期望误当奖品期望'})
    save('复算_四活动获取矩阵', acquisition)
    stages=[]; cumulative=defaultdict(float)
    for r in sorted((r for r in rows('QuestGetLevel') if r['questType'] in QUEST), key=lambda r:(r['questType'],r['Id'])):
        cumulative[r['questType']] += r['LevelUpPoints']
        stages.append({'活动':QUEST[r['questType']], 'questType':r['questType'], '阶段ID':r['Id'],
                       '阶段积分成本':r['LevelUpPoints'], '从0逐阶段积分总成本':cumulative[r['questType']],
                       '奖励活动物品数':r['num'], '来源':ref('QuestGetLevel',r),'口径':'每级清零，阶段成本相加；活动物品映射见QuestInitItem，关联待系统策划确认'})
    save('复算_四活动全阶段',stages)
    examples=[]
    for q, name in QUEST.items():
        candidates=[r for r in acquisition if r['questType']==q and num(r['条件命中积分']) and r['条件命中积分']>0 and num(r['概率千分值']) and r['概率千分值']>0]
        if not candidates:
            continue
        src=min(candidates,key=lambda r:(r['等级档'],r['VIP'],r['BetIndex']))
        for st in [r for r in stages if r['questType']==q]:
            prob=src['概率千分值']/1000
            spins=stage_spins(st['阶段积分成本'],src['条件命中积分'],prob)
            wager=spins*src['毛下注金币每Spin'] if spins is not None else None
            examples.append({'活动':name,'阶段':st['阶段ID'],'等级档':src['等级档'],'VIP':src['VIP'],'BetIndex':src['BetIndex'],
                             '阶段积分':st['阶段积分成本'],'命中积分':src['条件命中积分'],'命中概率':prob,
                             '期望Spin':spins,'金币Bet':src['毛下注金币每Spin'],'期望毛下注金币':wager,
                             '奖励物品数':st['奖励活动物品数'],'毛下注金币每个物品':divide(wager,st['奖励活动物品数']),
                             '来源':st['来源']+' | '+src['来源']})
    save('复算_四活动阶段成本示例',examples,'获取与阶段成本',
         '每活动选首个有效配置档示例；全部阶段。假设独立固定概率、命中积分固定、阶段从0开始且清零；无机器净耗或实付含义。',
         formulas={'I':'=IF(AND(G{r}>0,H{r}>0,H{r}<=1),ROUNDUP(F{r}/G{r},0)/H{r},"缺口")',
                   'K':'=IF(ISNUMBER(I{r}),I{r}*J{r},"缺口")','M':'=IF(AND(ISNUMBER(K{r}),L{r}>0),K{r}/L{r},"缺口")'})
    save('四活动初始与结束兑换',[{'活动':QUEST.get(r['questType'],str(r['questType'])),'资源ID':r[f'itemId_3_{i}'],
         '初始数量':r[f'initItemCount_3_{i}'],'结束兑换金币每个':r[f'itemExchChip_3_{i}'],'来源':ref('QuestInitItem',r)}
         for r in rows('QuestInitItem') if r['questType'] in QUEST for i in range(3) if r.get(f'itemId_3_{i}')])

    # 777: first draw within an untouched ring. Forced turns and repeated collection are separate.
    lucky=[]; round_map={r['round']:r for r in rows('StrikeLuckyRound')}
    for (rnd, ring), pool in group(rows('StrikeLucky'),('round','inout')).items():
        cost=round_map[rnd]; i=int(ring)-1; total=sum(r['hitWeight'] for r in pool)
        for r in pool:
            lucky.append({'轮':rnd,'环':ring,'格ID':r['gridId'],'权重':r['hitWeight'],'同轮同环总权重':total,
                          '首抽概率':divide(r['hitWeight'],total),'奖励类型':r['itemType'],'奖励ID':r['itemId'],
                          '奖励数量':r['itemCount'],'该奖励首抽期望数量':divide(r['hitWeight']*r['itemCount'],total),
                          '消耗资源ID':cost[f'costItemId_3_{i}'],'每抽消耗数':cost[f'costCount_3_{i}'],
                          '强制命中轮':r['forceTurn'],'来源':ref('StrikeLucky',r)+' | '+ref('StrikeLuckyRound',cost)})
    save('复算_777首抽',lucky,'777', '仅未触发保底、全部格子可选时首抽；不同资源期望不可直接相加。整轮需补充移除/保底/收集规则。',
         formulas={'F':'=IF(E{r}>0,D{r}/E{r},"缺口")','J':'=IF(ISNUMBER(F{r}),F{r}*I{r},"缺口")'})

    boxing=[]; bcost={(r['Turn'],r['Orbit']):r for r in rows('QuestBoxingJcakpot')}
    for key,pool in group(rows('QuestBoxingStageReward'),('Turn','orbit')).items():
        total=sum(r['Weight'] for r in pool); cost=bcost.get(key)
        for r in pool:
            boxing.append({'轮':key[0],'轨道':key[1],'权重':r['Weight'],'有效池总权重':total,
                           '初始池单抽概率':divide(r['Weight'],total),
                           '单组数量上限':r['MaxNum'],'奖励类型':r['RewardItemType'],'资源ID':r['RewardItemId'],
                           '奖励数量':r['RewardItemCount'],'初始池期望数量':divide(r['Weight']*r['RewardItemCount'],total),
                           '按配额取满的奖励量':r['MaxNum']*r['RewardItemCount'] if num(r['MaxNum']) else None,
                           '消耗ID':cost['CostItemId'] if cost else None,'单抽成本':cost['CostItemCount'] if cost else None,
                           '来源':ref('QuestBoxingStageReward',r)+((' | '+ref('QuestBoxingJcakpot',cost)) if cost else '')})
    save('复算_拳击奖励池',boxing,'拳击','条件：初始池全行可选，Weight按行归一；6行MaxNum为空，配额/是否无限待确认。配额取满量不是通关期望；Jackpot及Pass单列。',
         formulas={'E':'=IF(D{r}>0,C{r}/D{r},"缺口")','J':'=IF(ISNUMBER(E{r}),E{r}*I{r},"缺口")','K':'=IF(ISNUMBER(F{r}),F{r}*I{r},"缺口")'})
    save('拳击Jackpot固定奖励',[{k:v for k,v in r.items() if not k.startswith('_')}|{'来源':ref('QuestBoxingJcakpot',r)} for r in rows('QuestBoxingJcakpot')])

    miner=[]
    for r in rows('QuestMinerDropItem'):
        keys=['EmptyProb','BombProb','CashNum','ChipProb','CardPageProb']
        total=sum(r[k] for k in keys)
        miner.append({'地图组ID':r['id'],'剩余箱数':r['BoxNum'],'空概率值':r['EmptyProb'],'炸弹概率值':r['BombProb'],
                      'CashNum概率值':r['CashNum'],'金币概率值':r['ChipProb'],'卡包概率值':r['CardPageProb'],
                      '概率值合计':total,'金币奖励价值分':r['chipNum'],'分母':10000,
                      '金币分支价值分每次抽取':r['ChipProb']*r['chipNum']/10000,'卡包ID':r['CardPageItemId'],
                      '卡包期望每次抽取':r['CardPageProb']/10000,
                      '状态':'条件复算；总和不等于10000，缺失/顺序规则待确认' if total!=10000 else '条件复算；万分比与互斥抽取口径待确认',
                      '来源':ref('QuestMinerDropItem',r)})
    save('复算_挖矿掉落',miner,'挖矿','仅按万分比边际概率解读的条件量；CashNum列是概率名义，不能读作数量。不是每镐返还；炸弹连锁/特殊砖成本缺失。',
         formulas={'H':'=SUM(C{r}:G{r})','K':'=F{r}*I{r}/J{r}','M':'=G{r}/J{r}'})
    diagnostics['miner_probability_totals']=dict(Counter(str(r['概率值合计']) for r in miner))
    map_rows=[]
    for (mid,), rs in group(rows('QuestMinerMap'),('id',)).items():
        c=Counter(r[f'col_10_{i}'] for r in rs for i in range(10))
        map_rows.append({'地图ID':mid,'客户端地图':rs[0]['cliMapNumber'],'行数':len(rs),'格数':sum(c.values()),
                         '普通砖1':c[1],'特殊砖2':c[2],'红钻9':c[9],'绿钻10':c[10],'蓝钻11':c[11],
                         '其他格':sum(n for k,n in c.items() if k not in (1,2,9,10,11)),
                         '来源':' | '.join(ref('QuestMinerMap',r) for r in rs)})
    save('挖矿地图阶段',map_rows)
    save('挖矿固定通关奖励',[{k:v for k,v in r.items() if not k.startswith('_')}|{'来源':ref('QuestMinerStageReward',r)} for r in rows('QuestMinerStageReward')])

    snack=[]
    for r in rows('SnackDropItemCfg'):
        snack.append({'箱数':r['boxNum'],'luck下界':r['luck'],'reset万分值':r['resetItemProb'],
                      'Pass万分值':r['passItemProb'],'单次Pass数量':r['passNum'],'金币万分值':r['chipItemProb'],
                      '单次金币价值分':r['chipNum'],'概率分母':10000,
                      'Pass边际数量期望':r['passItemProb']*r['passNum']/10000,
                      '金币边际价值分期望':r['chipItemProb']*r['chipNum']/10000,
                      '来源':ref('SnackDropItemCfg',r),
                      '条件':'仅该状态边际复算；reset/Jackpot不同拥有数量分支不能合并归一，整轮缺状态规则'})
    save('复算_薯片状态边际',snack,'薯片','保留箱数和luck门槛；这里只算已明示万分比的边际量，不计算重置后的整局返还。',
         formulas={'I':'=D{r}*E{r}/H{r}','J':'=F{r}*G{r}/H{r}'})
    save('薯片Luck阶段',[{k:v for k,v in r.items() if not k.startswith('_')}|{'来源':ref('SnackAddLuck',r)} for r in rows('SnackAddLuck')])

    # Level and VIP costs are different units and threshold semantics.
    level=[]; running=defaultdict(float)
    for r in rows('LevelCfg'):
        t=r['levelUpType'];running[t]+=r['levelUpExp']
        level.append({'等级':r['level'],'类型':t,'到下级成本':r['levelUpExp'],'单位':'Spin次数' if t==1 else '等级经验' if t==0 else '类型待确认',
                      '仅同单位累计成本':running[t],'升级VIP条件':r.get('levelUpVip'),'来源':ref('LevelCfg',r)})
    save('复算_等级阶段成本',level)
    vip=[]; previous=0
    for r in sorted(rows('VipCfg'),key=lambda r:r['vipLevel']):
        vip.append({'VIP等级':r['vipLevel'],'累计经验门槛':r['needExp'],'前级累计门槛':previous,
                    '增量VIP经验':r['needExp']-previous,'来源':ref('VipCfg',r)})
        previous=r['needExp']
    save('复算_VIP成本',vip,'VIP与成长','VIP升级不清0，使用门槛差，不能把累计门槛相加；5000等级逐级成本见CSV，Spin与经验分开累计。',formulas={'D':'=B{r}-C{r}'})
    hourly=[]
    for key,pool in group(rows('FreeBonusHourly'),('id','weightType')).items():
        total=sum(r['weight'] for r in pool)
        for r in pool:
            hourly.append({'类型':key[0],'领取次数条件':key[1],'奖励档':r['level'],'权重':r['weight'],'组内总权重':total,
                           '奖励美元千分值':r['coins'],'缩放分母':1000,
                           '该档期望配置美元每次领取':divide(r['weight']*r['coins'],total*1000),
                           '间隔秒':r['interval'],'来源':ref('FreeBonusHourly',r)})
    save('复算_小时福利',hourly,'免费福利','同类型/领取次数分组，概率×美元千分值；组内H列相加为每次领取期望，不等于日实际产出。',formulas={'H':'=IF(E{r}>0,D{r}*F{r}/E{r}/G{r},"缺口")'})
    wheel=[]
    for key,pool in group(rows('FreeBonusWheel'),('payType','weightType','group')).items():
        total=sum(r['weight'] for r in pool)
        for r in pool:
            wheel.append({'付费类型':key[0],'周次数档':key[1],'group':key[2],'奖励档':r['level'],
                          '权重':r['weight'],'总权重':total,'倍数百分值':r['multi'],
                          '该档期望倍数':divide(r['weight']*r['multi'],100*total),'来源':ref('FreeBonusWheel',r)})
    save('复算_福利轮盘',wheel)

    pass_rows=[]
    for name in ['SnackPassReward','QuestBoxingPass']:
        for (category,), pool in group(rows(name),('category',)).items():
            cumulative=0
            for r in sorted(pool,key=lambda r:r['levelId']):
                cumulative=cumulative+r['LevelExp'] if num(cumulative) and num(r['LevelExp']) else None
                for i in range(2):
                    if r.get(f'rewardType_2_{i}') is None:
                        continue
                    pass_rows.append({'表':name,'分组':category,'阶段':r['levelId'],'阶段成本':r['LevelExp'],
                                      '累计成本':cumulative,'单位':'Pass奖券；升级不累计',
                                      '奖励类型':r[f'rewardType_2_{i}'],'奖励ID':r[f'rewardId_2_{i}'],'数量':r[f'rewardNum_2_{i}'],
                                      '类型语义':'本表17→PriceCheatSheet.priceType17，9→priceType9；其他保留本表枚举','来源':ref(name,r)})
    for key,pool in group(rows('BPReward'),('passType','chapter')).items():
        previous=0
        for r in sorted(pool,key=lambda r:r['level']):
            for track in ['free','pay']:
                pass_rows.append({'表':'BPReward','分组':str(key)+'/'+track,'阶段':r['level'],
                                  '阶段成本':r['pointRequirement']-previous,'累计成本':r['pointRequirement'],'单位':'Pass经验；本章累计，跨章规则待确认',
                                  '奖励类型':r[track+'AwardType'],'奖励ID':r[track+'ItemId'],'数量':r[track+'ItemCount'],
                                  '类型语义':'本表9注释存在金币/美金及除900/除100冲突，金额不可换算','来源':ref('BPReward',r)})
            previous=r['pointRequirement']
    save('复算_Pass阶段奖励',pass_rows,'Pass','免费/付费轨独立；四活动组合未定。不同表枚举不能通用。BattlePassAward旧表9=卡包，已在字段总表保留。')

    cards=[]
    for key,pool in group(rows('CardPack'),('pack','itemId','season')).items():
        total=sum(r['weight'] for r in pool)
        for r in pool:
            cards.append({'卡包':key[0],'ItemID':key[1],'赛季':key[2],'行ID':r['id'],'权重':r['weight'],'包组权重和':total,
                          '变体概率':divide(r['weight'],total),'声明卡数':r['cardNum'],
                          '变体卡数期望贡献':divide(r['weight']*r['cardNum'],total),
                          '分槽num之和':sum(r.get('num'+str(i)) or 0 for i in range(1,6)),
                          '来源':ref('CardPack',r),'限制':'仅变体组成；金卡/稀有卡/完成册增量价值需当前状态与抽卡规则，不能用卡数平均'})
    save('复算_卡包声明组成',cards,'卡包卡册','仅按同pack/item/season有效变体组归一；不是新卡率或玩家价值。未导入历史附件抽卡规则。',
         formulas={'G':'=IF(F{r}>0,E{r}/F{r},"缺口")','I':'=IF(ISNUMBER(G{r}),G{r}*H{r},"缺口")'})
    for n in ['CardAlbumCfg','CardChapter','LevelAward','Item','BuildLevelCfg','BuildingProductChip','ItemExchange','PayKey','PriceSetting','BPPurchase','SnackItemPack']:
        save('现行_'+n,[{k:v for k,v in r.items() if not k.startswith('_')}|{'来源':ref(n,r)} for r in rows(n)])

    # Commerce uses explicit field comments for currency and precision, never SKU suffix guessing.
    products=[]; permanent=[]
    for p in sorted((root/'normalized').glob('*.json')):
        d=table(p.stem)
        if d['system'] not in ['商城礼包','任务建造与常驻系统','免费福利','其他活动','Pass']:
            continue
        # Preserve these directory entries but do not interpret lifecycle/old-user mechanisms.
        if p.stem in ['BagReturn','BagRestoreCoins','PayLoseControl']:
            continue
        s=sheet(p.stem)
        metas={m['key']:m for m in s['fields']}
        if d['system']=='商城礼包':
            price_fields=[m for m in s['fields'] if ('价格' in m['comment'] or '参考价格' in m['comment']) and not any(x in m['comment'] for x in ['原始','展示','原价'])]
            for r in s['records']:
                for m in price_fields:
                    value=r.get(m['key'])
                    if value is None:
                        continue
                    comment=m['comment'];scale=100 if '除以100' in comment else None
                    currency='USD配置标价' if '美元' in comment else '里拉配置标价' if '里拉' in comment else '币种未声明'
                    products.append({'表':p.stem,'行ID':r['_row_id'],'价格字段':m['field'],'原值':value,
                                     '除数':scale,'换算标价':divide(value,scale),'币种':currency,
                                     '适用条件':';'.join(f'{k}={v}' for k,v in r.items() if v is not None and re.search(r'vip|level|group|limit|type',k,re.I) and not k.startswith('_')),
                                     '价格说明':comment,'来源':ref(p.stem,r,m['field'])})
        for r in s['records']:
            for m in s['fields']:
                v=r.get(m['key'])
                if v is None or not re.search(r'奖励|消耗|兑换|所需|概率|权重|积分|经验|产出|生产',m['comment']):
                    continue
                if re.search(r'广告|埋点|日志|机器人|支付回调',m['comment']):
                    continue
                permanent.append({'系统':d['system'],'表':p.stem,'行ID':r['_row_id'],'字段':m['field'],'现行值':v,
                                  '字段解释':m['comment'],'单位口径':'按本表枚举和注释；未明单位不自动换算','来源':ref(p.stem,r,m['field'])})
    save('商城礼包现行标价',products,'商城标价','只换算字段明示除以100的币种；参考价、展示折扣、SKU后缀不能证明实付或折扣。礼包奖励保留资源种类见字段明细。',
         formulas={'F':'=IF(AND(ISNUMBER(D{r}),ISNUMBER(E{r}),E{r}>0),D{r}/E{r},"缺口")'})
    save('任务福利活动奖励消耗字段',permanent)

    # A rate is allowed only when its denominator is explicit. This is a fresh-pool quantity rate.
    returns=[]
    for q, data, keys, costkey, typekey, itemkey, valuekey, pkey, costid in [
        (5,lucky,('轮','环'),'每抽消耗数','奖励类型','奖励ID','奖励数量','首抽概率','消耗资源ID'),
        (8,boxing,('轮','轨道'),'单抽成本','奖励类型','资源ID','奖励数量','初始池单抽概率','消耗ID')]:
        for key,pool in group(data,keys).items():
            first=pool[0];cost=first[costkey];resource=first[costid]
            same=[r for r in pool if r[typekey]==3 and r[itemkey]==resource]
            expectation=sum(r[pkey]*r[valuekey] for r in same) if all(num(r[pkey]) for r in pool) else None
            returns.append({'活动':QUEST[q],'轮与环轨':str(key),'消耗资源ID':resource,'期望返同ID物品数':expectation,
                            '每抽消耗物品数':cost,'首抽同资源返还率':divide(expectation,cost),
                            '分母与限制':'分母为本次抽奖活动物品数；只含type3且ID相同的直接返奖，未含其他价值/后续回流',
                            '来源':' | '.join(r['来源'] for r in pool)})
    save('复算_同资源返还率',returns,'返还率口径','777/拳击初始池条件量。薯片与挖矿缺单次消耗或状态转移定义，整轮返还留空；金币毛下注/净耗分母见说明。',
         formulas={'F':'=IF(AND(ISNUMBER(D{r}),ISNUMBER(E{r}),E{r}>0),D{r}/E{r},"缺口")'})

    # Machine event pools: preserve hierarchy; no global weight normalization and no inferred outcome EV.
    machine=[]
    for path in sorted((root/'normalized').glob('SlotsCasinoCommResultStrategy*.json')):
        name=path.stem
        for key,pool in group(rows(name),('machineId','eventGroup','parentId')).items():
            total=sum(r.get('eventWeight') or 0 for r in pool)
            machine.append({'表':name,'machineId原值':key[0],'eventGroup':key[1],'parentId':key[2],
                            '子项数':len(pool),'权重和':total,'条件':'仅同层/父节点权重小计，层级路由/结果集未归一为全机RTP',
                            '来源':f'{name}.xlsx/{sheet(name)["name"]}/行'+','.join(str(r['_excel_row']) for r in pool)+f';r{revision}'})
    save('机台奖励层级目录',machine)

    # Read supplementary numeric JSON only, excluding binary result sets and code/protocol.
    json_count=0; json_cells=0; json_errors=[]
    if a.extra:
        def leaves(obj: Any, pointer: str=''):
            if isinstance(obj,dict):
                for k,v in obj.items():
                    yield from leaves(v,pointer+'/'+str(k).replace('~','~0').replace('/','~1'))
            elif isinstance(obj,list):
                for i,v in enumerate(obj):
                    yield from leaves(v,pointer+'/'+str(i))
            else:
                yield pointer,obj
        with gzip.open(root/'机台地图JSON数值明细.csv.gz','wt',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f);w.writerow(['来源相对路径','JSONPointer','现行值','单位','revision'])
            for p in sorted(a.extra.rglob('*.json')):
                if p.relative_to(a.extra).parts[0] not in ['slots','QuestMap']:
                    continue
                try:
                    obj=json.loads(p.read_text(encoding='utf-8-sig'))
                except (json.JSONDecodeError, UnicodeError) as exc:
                    json_errors.append({'path':p.relative_to(a.extra).as_posix(),'error':type(exc).__name__,
                                        'line':getattr(exc,'lineno',None),'status':'保留原文件，未修补；本工具严格JSON无法提取'})
                    continue
                json_count+=1
                for pointer,value in leaves(obj):
                    w.writerow([p.relative_to(a.extra).as_posix(),pointer,value,'由模板/字段定义决定；不把展示值当概率',revision]);json_cells+=1

    # Formula cache gaps and external workbook references are preserved, not silently recalculated.
    cache_gaps=[]; external=[]
    for p in sorted((root/'normalized').glob('*.json')):
        d=table(p.stem)
        for s in d['sheets']:
            for r in s['records']:
                for field,formula in r.get('_formulas',{}).items():
                    if r.get(field) is None:
                        cache_gaps.append({'表':p.stem,'Sheet':s['name'],'Excel行':r['_excel_row'],'字段':field,'公式':formula})
                    if '[' in formula and ']' in formula:
                        external.append({'表':p.stem,'Sheet':s['name'],'Excel行':r['_excel_row'],'字段':field,'公式':formula,'缓存现行值':r.get(field)})
    save('缺失公式缓存',cache_gaps)
    save('外部公式引用清单',external)
    diagnostics.update({'revision':revision,'output_rows':counts,'extra_json_files':json_count,'extra_json_cells':json_cells,'json_read_gaps':json_errors,
                        'missing_formula_cache':len(cache_gaps),'external_formula_references':len(external),
                        'subagents':'none','source_writes':False,'source_hash_checks':False})
    (root/'复算结果.json').write_text(json.dumps(diagnostics,ensure_ascii=False,indent=2),encoding='utf-8')
    (root/'workbook-model.json').write_text(json.dumps({'revision':revision,'sheets':sheets},ensure_ascii=False),encoding='utf-8')
    print(json.dumps(diagnostics,ensure_ascii=False))

if __name__ == '__main__':
    main()
