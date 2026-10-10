"""TASK-0036 master计划：固定r7013原始导出，Accepted结果只作交付比较。

python build_producer_workbook.py --analysis <0036分析目录> --sources <r7013导出包目录> --output <受控目录>
随后用同目录 render_producer_workbook.mjs 渲染。Python负责业务与来源映射；
JS仅为已配置Artifact Tool的导出适配器。不连接SVN，不读旧表数值，不计算hash。
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any
from producer_workbook_sources import read_source


def col(n: int) -> str:
    result = ''
    while n:
        n, r = divmod(n - 1, 26)
        result = chr(65 + r) + result
    return result


def cell(sheet: str, row: int, column: int) -> str:
    return "'" + sheet.replace("'", "''") + "'!" + col(column) + str(row)


class Book:
    def __init__(self, analysis: Path, sources: Path) -> None:
        self.analysis = analysis
        self.sources = sources
        self.receipt = json.loads((sources / 'export-receipt.json').read_text(encoding='utf-8'))
        assert self.receipt['revision'] == 7013
        self.bindings: list[dict] = []
        self.source_specs: dict[str, dict] = {}
        self.sheets: dict[str, dict] = {}
        self.raw: dict[str, list[dict]] = {}
        self.refs: dict[tuple, str] = {}
        self.checks: list[dict] = []
        self.new('SRC_INDEX', ['表', '原Sheet', '字段', 'Excel列', '字段说明', '原证据revision', '适用revision'], True)

    def new(self, name: str, headers: list, hidden: bool = False, note: str = '') -> dict:
        s = {'name': name, 'hidden': hidden, 'rows': [], 'sections': [], 'formats': []}
        self.sheets[name] = s
        if hidden:
            s['rows'].append(headers)
        else:
            s['rows'] = [[name], ['r7013现值体验；尚未冻结或发布'], [note], []]
        return s

    def append(self, name: str, row: list) -> int:
        self.sheets[name]['rows'].append(row)
        return len(self.sheets[name]['rows'])

    def section(self, name: str, title: str, headers: list, rows: list[list], formats: dict | None = None) -> int:
        self.append(name, [title])
        hr = self.append(name, headers)
        for row in rows:
            self.append(name, row)
        self.sheets[name]['sections'].append({'row': hr, 'end': hr + len(rows), 'columns': len(headers)})
        for c, fmt in (formats or {}).items():
            self.sheets[name]['formats'].append([f'{col(c)}{hr+1}:{col(c)}{hr+len(rows)}', fmt])
        self.append(name, [])
        return hr + 1

    def source(self, name: str, fields: list[str] | None = None, select: Any = None) -> list[dict]:
        if name in self.raw:
            return self.raw[name]
        receipt = next(r for r in self.receipt['files'] if r['table'] == name)
        d = read_source(self.sources / 'source/r7013' / receipt['file'])
        # 完整业务原行和字段进入SRC；选择条件只用于本任务适用的活动/物品。
        fields = [f for i, f in d['fields']]
        records = [r for r in d['records'] if select is None or select(r)]
        self.raw[name] = records
        sn = 'SRC_' + name
        assert len(sn) <= 31
        self.new(sn, ['原Excel行', '原行键'] + fields, True)
        self.source_specs[name] = {'file': 'source/r7013/' + receipt['file'], 'sheet': d['sheet'], 'fields': fields, 'errors': d['errors']}
        for i, field in d['fields']:
            self.append('SRC_INDEX', [receipt['file'], d['sheet'], field, col(i+1), d['comments'][i], 7013, 7013])
        for r in records:
            rn = self.append(sn, [r['_excel_row'], r['_row_id']] + [r.get(f) for f in fields])
            for j, (i, f) in enumerate(d['fields'], 3):
                self.refs[name, r['_excel_row'], f] = cell(sn, rn, j)
                self.bindings.append({'sheet': sn, 'cell': col(j)+str(rn), 'table': name,
                    'source_cell': col(i+1)+str(r['_excel_row']), 'value': r[f]})
        return records

    def ref(self, name: str, r: dict, field: str) -> str:
        return self.refs[name, r['_excel_row'], field]

    def link(self, name: str, r: dict, field: str) -> str:
        ref = self.ref(name, r, field)
        return f'=IF(ISBLANK({ref}),"",{ref})'

    def csv(self, name: str) -> list[dict]:
        with (self.analysis / (name + '.csv')).open(encoding='utf-8-sig', newline='') as f:
            return list(csv.DictReader(f))

    def expected(self, ref: str, value: Any, group: str) -> None:
        if value not in (None, ''):
            self.checks.append({'cell': ref, 'expected': float(value), 'group': group})

    def raw_view(self, front: str, title: str, source: str, fields: list[str], headers: list[str] | None = None, records: list[dict] | None = None) -> int:
        rr = records if records is not None else self.source(source, fields)
        return self.section(front, title, headers or fields, [[self.link(source, r, f) for f in fields] for r in rr])


def build(b: Book) -> None:
    notes = {
        '总览': '普通扣金币Spin；固定等级/VIP/Bet且余额足够。配置美元不是实付。9组Unknown保留。',
        '基础金币': '精确价格档位；不推断缺档、向上选档或跨VIP倍率。所有金币价值按同档配置美元比较。',
        'VIP': '累计经验不清零；差值为增量门槛。VIP经验不换算充值美元。',
        'BET_RTP': '常规USD Bet≤1为95%，>1为85%。bet2仅分析参考；特殊RTP独立列示，优先级Unknown。',
        '等级': '源空type保持空。仅显式Spin链可累计；经验门槛不转换为预计Spin或天数。',
        'Buff': '只列当前加成配置与有明示分母的换算；不将旧表Buff倍率或未明加成叠加到RTP。',
        '美金金币档位': 'money单位为美元×100；按priceType/vipType/level精确读取。展示全部现行档位，缺值不补0。',
        '任务福利': '条件期望按每次领取；Spin数不能替代领取次数或在线时长，不输出虚构每日总量。',
        '商城_Pass': '配置标价与原奖励对比；不代表实际支付/最终兑现。共享Pass门槛只累计一次。',
        '卡包卡册': '掉落事件不等于新卡；声明卡数不等于整册完成。日期候选不证明本版线上启用。',
        '薯片': '积分连续跨档，从0积分0档起；初始赠送单列。一次消耗一个道具、一次一奖，Jackpot可重复。',
        '777': 'forceTurn已Closed：当前圈付费抽奖计数；普通格提前命中取消强制，换圈/轮重置，特殊格排除。',
        '常驻': '有配置不等于本版启用；建造已关闭，残留奖励不计可用收入。拳击/挖矿不进入9.22组合。',
        'Unknown': '沿用Accepted的9组解释边界；不是新增冻结Gate，不把Unknown当作0。',
    }
    for n, note in notes.items():
        b.new(n, [], note=note)
    price = b.source('PriceCheatSheet')
    bet = b.source('SlotsCasinoBetList')
    vip = b.source('VipCfg')
    vp_fields = ['vipLevel', 'expRate', 'slotRewardRate', 'slotTaskRewardRate', 'FreechipsRate', 'FreeSpinRate', 'SuperSpinRate', 'passFinalReward', 'passLevelReward', 'questTreasureDifficulty']
    vp = b.source('VipPrivilege', vp_fields)
    b.new('SRC_RULES', ['输入', '值', '出处'], True)
    for row in [['USD Bet分界', 1, 'User正式决定 / TASK-0034'], ['≤分界常规RTP', .95, 'User正式决定'], ['>分界常规RTP', .85, 'User正式决定'], ['百分比单位', 100, '对应源字段注释'], ['千分比单位', 1000, '对应源字段注释'], ['万分比单位', 10000, '对应源字段注释']]:
        b.append('SRC_RULES', row)
    b.new('SRC_SCENARIOS', ['场景', '等级', 'VIP', 'BetIndex', 'Spin', '分析档'], True)
    spins = b.csv('Spin体验')
    calc_heads = ['场景', '等级', 'VIP', 'BetIndex', 'Spin', '金币Bet', '金币/配置USD', 'USD Bet', '常规RTP', '毛下注金币', '机器返还金币', '机器净耗金币', '毛下注USD', '净耗USD', '净耗Bet数']
    b.new('CALC_SPIN', calc_heads, True)
    spin_rows = {}
    for expected in spins:
        inp = b.append('SRC_SCENARIOS', [expected['scenario'], int(expected['level']), int(expected['vip']), int(expected['bet_index']), int(expected['spins']), expected['bet_case']])
        br = next(r for r in bet if r['levelId'] == int(expected['bet_index']))
        matches = [r for r in price if (r['money'], r['priceType'], r['vipType'], r['level']) == (100, 17, 1, int(expected['level']))]
        assert len(matches) == 1
        pr = matches[0]
        rr = len(b.sheets['CALC_SPIN']['rows']) + 1
        r = [f'={cell("SRC_SCENARIOS",inp,j)}' for j in range(1, 6)]
        r += ['=' + b.ref('SlotsCasinoBetList', br, 'bet2'), '=' + b.ref('PriceCheatSheet', pr, 'vip_16_' + expected['vip'])]
        r += [f'=F{rr}/G{rr}', f'=IF(H{rr}<=SRC_RULES!B2,SRC_RULES!B3,SRC_RULES!B4)', f'=E{rr}*F{rr}', f'=J{rr}*I{rr}', f'=J{rr}-K{rr}', f'=J{rr}/G{rr}', f'=L{rr}/G{rr}', f'=L{rr}/F{rr}']
        b.append('CALC_SPIN', r)
        spin_rows[expected['scenario']] = rr
        for j, field in [(6,'coin_bet'),(7,'coins_per_config_usd'),(8,'config_usd_bet'),(9,'regular_rtp'),(10,'gross_coin_wager'),(11,'expected_machine_return_coins'),(12,'expected_machine_net_coin_cost'),(13,'gross_config_usd'),(14,'expected_machine_net_config_usd'),(15,'net_cost_in_bet_units')]:
            b.expected(cell('CALC_SPIN',rr,j), expected[field], 'Accepted Spin')
    b.section('BET_RTP', '36组常规Spin：现值与成本体验', calc_heads, [[f'={cell("CALC_SPIN",r,j)}' for j in range(1,16)] for r in spin_rows.values()], {9:'0.0%'})
    b.raw_view('BET_RTP','完整Bet配置档位（各列绑定Unknown）','SlotsCasinoBetList',['levelId','highroller','levelExp','bet2','bet3','bet33','bet9','bet35','eventOpen'])
    special = b.csv('现行_新手及活动关联RTP-引用')
    sf = ['id','minUnlockLevel','maxUnlockLevel','activityId_5_0','activityId_5_1','activityId_5_2','activityId_5_3','activityId_5_4','rtpTier','本行rtpTier注释解释']
    b.new('SRC_SPECIAL', sf, True)
    newbie=b.source('SlotsCasinoNewbieConfig')
    for r in special:
        original=next(x for x in newbie if x['_excel_row']==int(r['Excel行']))
        b.append('SRC_SPECIAL', [b.link('SlotsCasinoNewbieConfig',original,f) if f!='本行rtpTier注释解释' else r.get(f) for f in sf])
    b.section('BET_RTP','新手及活动关联RTP（与上表独立，优先级Unknown）',sf,[[f'=IF(ISBLANK({cell("SRC_SPECIAL",r,j)}),"",{cell("SRC_SPECIAL",r,j)})' for j in range(1,11)] for r in range(2,11)])

    # 基础金币：同一价格口径的全部等级，不复制旧基础币/膨胀系数。
    base = sorted([r for r in price if (r['money'],r['priceType'],r['vipType']) == (100,17,1)],key=lambda r:r['level'])
    b.new('CALC_COINS',['等级','V0金币/USD','V5金币/USD','V10金币/USD','V15金币/USD','V0相对首档','V5/V0','V10/V0','V15/V0'],True)
    for r in base:
        rn=len(b.sheets['CALC_COINS']['rows'])+1
        b.append('CALC_COINS',[b.link('PriceCheatSheet',r,'level')]+[b.link('PriceCheatSheet',r,'vip_16_'+str(v)) for v in (0,5,10,15)]+[f'=B{rn}/$B$2',f'=C{rn}/B{rn}',f'=D{rn}/B{rn}',f'=E{rn}/B{rn}'])
    b.section('基础金币','等级现值与同档VIP对比',b.sheets['CALC_COINS']['rows'][0],[[f'={cell("CALC_COINS",i,j)}' for j in range(1,10)] for i in range(2,len(base)+2)],{6:'0.00x',7:'0.00x',8:'0.00x',9:'0.00x'})
    exchange=b.source('DiamondChipExchange')
    b.new('CALC_EXCHANGE',['配置行','钻石','金币','金币/钻石'],True)
    for r in exchange:
        rn=len(b.sheets['CALC_EXCHANGE']['rows'])+1
        b.append('CALC_EXCHANGE',[r['_row_id'],b.link('DiamondChipExchange',r,'diamond'),b.link('DiamondChipExchange',r,'chip'),f'=IF(OR(B{rn}="",C{rn}="",B{rn}<=0),"Unknown",C{rn}/B{rn})'])
    b.section('基础金币','钻石兑换报价（不推定钻石美元汇率）',b.sheets['CALC_EXCHANGE']['rows'][0],[[f'={cell("CALC_EXCHANGE",i,j)}' for j in range(1,5)] for i in range(2,len(exchange)+2)])

    b.new('CALC_VIP',['VIP','累计经验','增量经验'],True)
    for i,r in enumerate(vip,2):
        b.append('CALC_VIP',[b.link('VipCfg',r,'vipLevel'),b.link('VipCfg',r,'needExp'),f'=B{i}' if i==2 else f'=B{i}-B{i-1}'])
    b.section('VIP','累计门槛与相邻VIP增量',b.sheets['CALC_VIP']['rows'][0],[[f'={cell("CALC_VIP",i,j)}' for j in range(1,4)] for i in range(2,len(vip)+2)])
    for i,r in enumerate(b.csv('VIP门槛引用'),2):
        b.expected(cell('CALC_VIP',i,2),r['累计经验门槛'],'Accepted VIP')
        b.expected(cell('CALC_VIP',i,3),r['增量VIP经验'],'Accepted VIP')
    b.raw_view('VIP','金币与奖励加成原字段（不二次叠入机器RTP）','VipPrivilege',vp_fields[:5],records=vp)

    levels=b.source('LevelCfg')
    awards=b.source('LevelAward',['level','rewardType','money','diamond','vipExp','ItemId','ItemCount'])
    award_map={r['level']:r for r in awards}
    b.new('CALC_LEVEL',['等级','升级类型原值','下一级门槛','升级VIP字段','显式累计Spin','奖励类型','原奖励金额','钻石','VIP经验','奖励道具','数量'],True)
    for i,r in enumerate(levels,2):
        type_ref=b.ref('LevelCfg',r,'levelUpType')
        chain=f'=IF(AND({type_ref}<>"",{type_ref}=1),C{i},"Unknown")' if i==2 else f'=IF(AND({type_ref}<>"",{type_ref}=1,ISNUMBER(E{i-1})),E{i-1}+C{i},"Unknown")'
        ar=award_map.get(r['level'])
        b.append('CALC_LEVEL',[b.link('LevelCfg',r,f) for f in ('level','levelUpType','levelUpExp','levelUpVip')]+[chain]+([b.link('LevelAward',ar,f) for f in ('rewardType','money','diamond','vipExp','ItemId','ItemCount')] if ar else ['不适用']*6))
    b.section('等级','逐级现值、显式Spin累计与升级奖励',b.sheets['CALC_LEVEL']['rows'][0],[[f'={cell("CALC_LEVEL",i,j)}' for j in range(1,12)] for i in range(2,len(levels)+2)])
    b.expected('CALC_LEVEL!E5',29,'Accepted 显式成长链')

    b.new('CALC_BUFF',['VIP','经验系数原值','经验系数/100','3小时福利原值','福利系数/100'],True)
    for i,r in enumerate(vp,2):
        b.append('CALC_BUFF',[b.link('VipPrivilege',r,'vipLevel'),b.link('VipPrivilege',r,'expRate'),f'=B{i}/SRC_RULES!B5',b.link('VipPrivilege',r,'FreechipsRate'),f'=D{i}/SRC_RULES!B5'])
    b.section('Buff','VIP明示系数；实际经验入账组合仍Unknown',b.sheets['CALC_BUFF']['rows'][0],[[f'={cell("CALC_BUFF",i,j)}' for j in range(1,6)] for i in range(2,len(vp)+2)],{3:'0.00x',5:'0.00x'})
    b.raw_view('Buff','联赛积分加成（百分比原值）','LeagueBuff',['itemID','scoreAddition'])
    items=b.source('Item',['itemID','name_zh','itemType','param1','validTimeSecond'],select=lambda r:isinstance(r.get('itemType'),(int,float)) and r['itemType']>100)
    b.raw_view('Buff','Buff类型物品（参数语义不外推）','Item',['itemID','name_zh','itemType','param1','validTimeSecond'],records=items)
    b.raw_view('Buff','Quest Buff原配置；不自动套用于薯片/777','QuestBuffBag',['Id','QuestType','VIP','BuffType','BlastItemNum','questItemId','questItemNum','CountdownTime'])

    fields=['money','priceType','vipType','level']+['vip_16_'+str(i) for i in range(16)]
    b.raw_view('美金金币档位','全现行价格档位（左侧条件＋右侧VIP0–15金币/资源值）','PriceCheatSheet',fields,records=price)

    # 福利只按同一奖励种类/领取次数/等级的权重归一，不混日频次。
    hourly=b.source('FreeBonusHourly')
    b.new('CALC_WELFARE',['类型','领取次数条件','等级','间隔秒','条件金币配置USD期望'],True)
    groups=sorted(set((r['id'],r['weightType'],r['level']) for r in hourly))
    for key in groups:
        rr=[r for r in hourly if (r['id'],r['weightType'],r['level'])==key]
        weights=[b.ref('FreeBonusHourly',r,'weight') for r in rr]
        products=[b.ref('FreeBonusHourly',r,'coins')+'*'+w for r,w in zip(rr,weights)]
        b.append('CALC_WELFARE',[b.link('FreeBonusHourly',rr[0],f) for f in ('id','weightType','level','interval')]+['=('+ '+'.join(products)+')/('+ '+'.join(weights)+')/SRC_RULES!B6'])
    b.section('任务福利','每次领取的条件期望（分母：一次满足条件的领取）',b.sheets['CALC_WELFARE']['rows'][0],[[f'={cell("CALC_WELFARE",i,j)}' for j in range(1,6)] for i in range(2,len(groups)+2)])
    for r in b.csv('福利领取条件期望'):
        matches=[i+2 for i,k in enumerate(groups) if str(k[0])==r['type'] and str(k[1])==r['claim_count_condition']]
        assert len(matches)==1
        b.expected(cell('CALC_WELFARE',matches[0],5),r['config_usd_expected_per_claim'],'Accepted 福利')
    for n,fields in [('CashRoyalTask',['id','taskName','resetType','type','param1','maxVal','chip']),('SignReward',['day','RewardType1','chip','itemId','itemCount','diamond']),('OnlineReward',['rewardID','chip','onlineTime']),('FrenzyMission',['Chapter','Level','MissionId','MissionType','MachineId','ParmType1','Parm1','RewardType1','RewardId1','RewardNum1'])]:
        b.raw_view('任务福利',n+'：条件与原奖励',n,fields)

    ps=b.source('PriceSetting')
    b.new('CALC_SHOP',['money','货币类型','VIP类型','VIP','标价USD','原奖励','原奖励/配置USD'],True)
    for r in ps:
        for v in (0,5,10,15):
            rn=len(b.sheets['CALC_SHOP']['rows'])+1
            b.append('CALC_SHOP',[b.link('PriceSetting',r,f) for f in ('money','currencyType','vipType')]+[v,f'=A{rn}/SRC_RULES!B5',b.link('PriceSetting',r,'vip'+str(v)),f'=IF(OR(E{rn}<=0,F{rn}=""),"Unknown",F{rn}/E{rn})'])
    b.section('商城_Pass','商店与礼包配置报价（V0/5/10/15对比）',b.sheets['CALC_SHOP']['rows'][0],[[f'={cell("CALC_SHOP",i,j)}' for j in range(1,8)] for i in range(2,len(b.sheets['CALC_SHOP']['rows'])+1)])
    b.raw_view('商城_Pass','薯片礼包原奖励；参考价单位Unknown','SnackItemPack',['id','type','group','_money','displayDiscount','rewardType_2_0','rewardId_2_0','rewardNum_2_0','rewardType_2_1','rewardId_2_1','rewardNum_2_1'])
    passes=b.source('SnackPassReward')
    b.new('CALC_PASS',['等级','共享本级门槛','共享累计门槛','付费原门槛','免费类型','免费数量','付费类型','付费数量'],True)
    for fr in sorted([r for r in passes if r['category']==0],key=lambda r:r['levelId']):
        paid=next(r for r in passes if r['category']==1 and r['levelId']==fr['levelId'])
        rn=len(b.sheets['CALC_PASS']['rows'])+1
        b.append('CALC_PASS',[b.link('SnackPassReward',fr,'levelId'),b.link('SnackPassReward',fr,'LevelExp'),f'=SUM(B$2:B{rn})',b.link('SnackPassReward',paid,'LevelExp'),b.link('SnackPassReward',fr,'rewardType_2_0'),b.link('SnackPassReward',fr,'rewardNum_2_0'),b.link('SnackPassReward',paid,'rewardType_2_0'),b.link('SnackPassReward',paid,'rewardNum_2_0')])
    b.section('商城_Pass','薯片Pass：共享门槛、累计与两轨主奖励',b.sheets['CALC_PASS']['rows'][0],[[f'={cell("CALC_PASS",i,j)}' for j in range(1,9)] for i in range(2,17)])
    b.raw_view('商城_Pass','薯片Pass完整奖励槽；追领只计未领取奖励','SnackPassReward',['id','category','levelId','rewardType_2_0','rewardId_2_0','rewardNum_2_0','rewardType_2_1','rewardId_2_1','rewardNum_2_1'],records=passes)
    b.raw_view('商城_Pass','其他Pass独立规则；不得套用薯片门槛','BPRate',['level','pointTotal','coinsRate'])
    b.raw_view('商城_Pass','其他Pass购买经验条件','BPCfg',['ExpGet','ExpAddtion','TimesMax','DownMax','DownTime'])
    b.raw_view('商城_Pass','其他Pass关卡条件','CommonBPLevelCondition',['Id','Type','Group','LevelId','LevelExp','LevelDiamond'])

    drop=b.source('SlotsCasinoDropCards')
    b.new('CALC_CARDS',['场景','Spin','原掉率万分值','掉率','掉落事件期望','至少一次概率','卡包1','权重1','卡包2','权重2','卡包3','权重3'],True)
    card_rows={}
    for expected in spins:
        lev,v,betid=map(int,(expected['level'],expected['vip'],expected['bet_index']))
        rr=[r for r in drop if r['level']==lev and r['betIndex']==betid and r['needVipMinCard']<=v<=r['needVipMaxCard']]
        assert len(rr)==1
        r=rr[0]; rn=len(b.sheets['CALC_CARDS']['rows'])+1; si=spin_rows[expected['scenario']]
        b.append('CALC_CARDS',[f'=CALC_SPIN!A{si}',f'=CALC_SPIN!E{si}',b.link('SlotsCasinoDropCards',r,'dropPro'),f'=C{rn}/SRC_RULES!B7',f'=B{rn}*D{rn}',f'=1-(1-D{rn})^B{rn}']+[b.link('SlotsCasinoDropCards',r,f) for f in ('cardId1','cardWeight1','cardId2','cardWeight2','cardId3','cardWeight3')])
        card_rows[expected['scenario']]=rn
    b.section('卡包卡册','36组精确档位掉落事件（不是新卡数）',b.sheets['CALC_CARDS']['rows'][0],[[f'={cell("CALC_CARDS",i,j)}' for j in range(1,13)] for i in range(2,38)],{4:'0.00%',6:'0.00%'})
    for r in b.csv('Spin掉卡条件'):
        rn=card_rows[r['scenario']]
        b.expected(cell('CALC_CARDS',rn,5),r['conditional_expected_drop_events'],'Accepted 掉卡')
        b.expected(cell('CALC_CARDS',rn,6),r['conditional_p_at_least_one_drop'],'Accepted 掉卡')
    b.raw_view('卡包卡册','赛季现值（9.22仅日历候选，不证明启用）','CardAlbumCfg',['id','startTime','endTime','seasonName','passageNum','cardNum','prestigePassageNum','prestigeCardNum','rewardType','albumCoins'])
    b.raw_view('卡包卡册','章节配置；原金额须按rewardType解释','CardChapter',['id','seasonId','isPrestige','cardNum','rewardType','chapterCoins','chapterItem','chapterItemCount'])
    packs=b.source('CardPack')
    b.new('CALC_PACK',['卡包','ItemID','赛季','变体行ID','权重','同包总权重','变体概率','声明卡数','卡数期望贡献','分槽数量合计'],True)
    for r in packs:
        rn=len(b.sheets['CALC_PACK']['rows'])+1
        same=[x for x in packs if x['pack']==r['pack']]
        weights=','.join(b.ref('CardPack',x,'weight') for x in same)
        nums=','.join(b.ref('CardPack',r,'num'+str(i)) for i in range(1,6))
        b.append('CALC_PACK',[b.link('CardPack',r,f) for f in ('pack','itemId','season','id','weight')]+[f'=SUM({weights})',f'=E{rn}/F{rn}',b.link('CardPack',r,'cardNum'),f'=G{rn}*H{rn}',f'=SUM({nums})'])
    b.section('卡包卡册','声明组成；不等于当前状态下的新卡价值',b.sheets['CALC_PACK']['rows'][0],[[f'={cell("CALC_PACK",i,j)}' for j in range(1,11)] for i in range(2,len(packs)+2)],{7:'0.00%'})

    stages=b.source('QuestGetLevel',select=lambda r:r['questType'] in (4,5))
    pick=b.source('QuestPickGet',select=lambda r:r['questType'] in (4,5))
    points=b.source('QuestPointsCheatSheet',select=lambda r:r['questType'] in (4,5))
    initial=b.source('QuestInitItem',select=lambda r:r['questType'] in (4,5))
    unlock=b.source('SysUnlock')
    stage_rows={}; act_rows={}
    b.new('CALC_STAGE',['活动','阶段ID','阶段积分','奖励数量','累计积分','累计道具'],True)
    for q in (4,5):
        rows=[]
        for r in sorted([r for r in stages if r['questType']==q],key=lambda r:r['Id']):
            rn=len(b.sheets['CALC_STAGE']['rows'])+1
            prev=rows[-1] if rows else None
            b.append('CALC_STAGE',[b.link('QuestGetLevel',r,'questType'),b.link('QuestGetLevel',r,'Id'),b.link('QuestGetLevel',r,'LevelUpPoints'),b.link('QuestGetLevel',r,'num'),f'=C{rn}'+(f'+E{prev}' if prev else ''),f'=D{rn}'+(f'+F{prev}' if prev else '')])
            rows.append(rn)
        assert [r for r in stages if r['questType']==q][-1]['num']==0
        stage_rows[q]=rows
    b.new('CALC_ACTIVITY',['场景','活动','Spin','等级达标','源概率','有效概率','每次命中积分','期望积分','期望道具','至少首份概率','初始物品','初始赠送','首阶段所需命中'],True)
    b.new('CALC_TAIL',['场景','活动','累计阶段积分','阶段奖','最少命中','达到概率','期望贡献'],True)
    for e in b.csv('双活动体验'):
        q=int(e['quest_type']); si=spin_rows[e['scenario']]; sr=spins[si-2]
        eligible=next(r for r in unlock if r['desc']==('薯片活动' if q==4 else 777))
        pck=[r for r in pick if r['questType']==q and r['BetId']==int(sr['bet_index']) and r['Type']==2]
        assert len(pck)==1
        pck=pck[0]
        pts=[r for r in points if r['questType']==q and r['Id']==pck['Id'] and r['level']==int(sr['level'])]
        assert len(pts)==1
        init=next(r for r in initial if r['questType']==q)
        rn=len(b.sheets['CALC_ACTIVITY']['rows'])+1
        start=len(b.sheets['CALC_TAIL']['rows'])+1
        for st in stage_rows[q][:-1]:
            tr=len(b.sheets['CALC_TAIL']['rows'])+1
            b.append('CALC_TAIL',[f'=CALC_ACTIVITY!A{rn}',f'=CALC_ACTIVITY!B{rn}',f'=CALC_STAGE!E{st}',f'=CALC_STAGE!D{st}',f'=ROUNDUP(C{tr}/CALC_ACTIVITY!G{rn},0)',f'=IF(E{tr}>CALC_ACTIVITY!C{rn},0,MAX(0,1-BINOMDIST(E{tr}-1,CALC_ACTIVITY!C{rn},CALC_ACTIVITY!F{rn},TRUE)))',f'=D{tr}*F{tr}'])
        end=len(b.sheets['CALC_TAIL']['rows'])
        b.append('CALC_ACTIVITY',[f'=CALC_SPIN!A{si}',q,f'=CALC_SPIN!E{si}',f'=CALC_SPIN!B{si}>={b.ref("SysUnlock",eligible,"param_4_0")}',f'={b.ref("QuestPickGet",pck,"Probability")}/SRC_RULES!B6',f'=IF(D{rn},E{rn},0)',b.link('QuestPointsCheatSheet',pts[0],'vip_16_'+sr['vip']),f'=C{rn}*F{rn}*G{rn}',f'=SUM(CALC_TAIL!G{start}:G{end})',f'=CALC_TAIL!F{start}',b.link('QuestInitItem',init,'itemId_3_0'),b.link('QuestInitItem',init,'initItemCount_3_0'),f'=CALC_TAIL!E{start}'])
        act_rows[e['scenario'],q]=rn
        for c,f in [(5,'p_hit'),(7,'gain_on_hit'),(8,'expected_points'),(9,'expected_items'),(10,'p_any_earned_item'),(12,'configured_initial_count'),(13,'first_threshold_required_hits')]:
            b.expected(cell('CALC_ACTIVITY',rn,c),e[f],'Accepted 活动')
    for q,front in ((4,'薯片'),(5,'777')):
        rr=[r for (s,quest),r in act_rows.items() if quest==q]
        cols=[1,3,4,5,7,8,9,10,12,13]
        b.section(front,'36组获取体验；初始赠送不混入Spin产物',[b.sheets['CALC_ACTIVITY']['rows'][0][j-1] for j in cols],[[f'={cell("CALC_ACTIVITY",r,j)}' for j in cols] for r in rr],{4:'0.0%',8:'0.00%'})
        b.section(front,'阶段成本、阶段奖励与累计（末行零产物为封顶）',b.sheets['CALC_STAGE']['rows'][0][1:],[[f'={cell("CALC_STAGE",r,j)}' for j in range(2,7)] for r in stage_rows[q]])
    b.raw_view('薯片','幸运值档位与获得增量','SnackAddLuck',['id','usedItemCountMin','usedItemCountMax','addLuck'])
    sd=b.source('SnackDropItemCfg')
    b.raw_view('薯片','状态奖池原权重及奖励；不据此输出完整活动EV','SnackDropItemCfg',['boxNum','luck','resetItemProb','passItemProb','passNum','chipItemProb','chipNum'],records=sd)
    b.raw_view('薯片','Jackpot槽位原权重；非独立额外发奖','SnackDropItemCfg',['boxNum','luck']+[f'jackpot{i}Prob_3_{j}' for i in (1,2,3,4) for j in (0,1,2)],records=sd)
    b.raw_view('777','轮/圈消耗与收集奖励（不等于清盘成本）','StrikeLuckyRound',['round','costItemId_3_0','costCount_3_0','costItemId_3_1','costCount_3_1','costItemId_3_2','costCount_3_2','cherryCollect','cherryItemCount','sevenCollect','sevenItemCount'])
    b.raw_view('777','格子当前奖励与forceTurn原配置','StrikeLucky',['gridId','round','inout','hitWeight','itemType','itemId','itemCount','forceTurn'])

    b.new('CALC_OVERVIEW',['场景','等级','VIP','Spin','USD Bet','常规RTP','机器净耗USD','薯片期望道具','777期望道具','卡包掉落期望','同得首份概率下界','同得首份概率上界'],True)
    for e in spins:
        s=e['scenario']; r=spin_rows[s]; sn=act_rows[s,4]; lu=act_rows[s,5]; ca=card_rows[s]
        b.append('CALC_OVERVIEW',[f'=CALC_SPIN!{col(j)}{r}' for j in (1,2,3,5,8,9,14)]+[f'=CALC_ACTIVITY!I{sn}',f'=CALC_ACTIVITY!I{lu}',f'=CALC_CARDS!E{ca}',f'=MAX(0,CALC_ACTIVITY!J{sn}+CALC_ACTIVITY!J{lu}-1)',f'=MIN(CALC_ACTIVITY!J{sn},CALC_ACTIVITY!J{lu})'])
    b.section('总览','36组Spin体验：同一次毛下注只计一次',b.sheets['CALC_OVERVIEW']['rows'][0],[[f'={cell("CALC_OVERVIEW",i,j)}' for j in range(1,13)] for i in range(2,38)],{6:'0.0%',11:'0.00%',12:'0.00%'})
    coverage=b.csv('范围覆盖与资源关系')
    b.new('SRC_SCOPE',list(coverage[0]),True)
    for r in coverage: b.append('SRC_SCOPE',list(r.values()))
    b.section('总览','八类系统的阅读入口与解释边界',list(coverage[0]),[[f'={cell("SRC_SCOPE",i,j)}' for j in range(1,5)] for i in range(2,10)])
    section=b.sheets['总览']['sections'][-1]
    for rn in range(section['row']-1,section['end']):
        b.sheets['总览']['rows'][rn]=[v for value in b.sheets['总览']['rows'][rn] for v in (value,None,None)]
    section['columns']=12;section['span']=3
    b.raw_view('常驻','解锁条件现值；空类型不补默认','SysUnlock',['id','desc','unlockType_4_0','param_4_0','unlockType_4_1','param_4_1','unlockType_4_2','param_4_2','unlockType_4_3','param_4_3'],headers=['ID','系统','条件类型1','参数1','条件类型2','参数2','条件类型3','参数3','条件类型4','参数4'],records=unlock)
    b.raw_view('常驻','日常宝箱积分档','DailyTreasurePoint',['Id','Point','ItemId'])
    b.raw_view('常驻','航海关卡与资源需求','VoyageChapter',['chapterId','stageId','capacity','unlockLevel','requireItems','stageReward_4_0','stageRewardNum_4_0','travelReward_4_0','travelRewardNum_4_0'])
    unk=b.csv('制作人Unknown');b.new('SRC_UNKNOWN',list(unk[0]),True)
    for r in unk: b.append('SRC_UNKNOWN',list(r.values()))
    b.section('Unknown','9组现有Unknown及需要补充的策划定义',list(unk[0]),[[f'={cell("SRC_UNKNOWN",i,j)}' for j in range(1,6)] for i in range(2,11)])
    b.append('SRC_INDEX',['TASK-0036 Accepted','报告/场景CSV','SRC_SCENARIOS / SRC_SPECIAL / SRC_UNKNOWN / SRC_SCOPE','','场景定义、9条特殊RTP阅读层与9组Unknown；非旧CashRoyal数值',6961,7013])
    wiki = [
        ('数值推导','15 Sheet旧总表','横向现值＋体验/累计/对比','旧数值不导入'),
        ('免费奖励','每次领取、权重、Buff','任务福利/Buff','每日领取频次Unknown'),
        ('等级+buff','22 Sheet多版本推导','基础金币/VIP/等级/Buff/商城','历史经验/倍数不套用'),
        ('卡包','8 Sheet新旧版对比','卡包卡册','不从旧版反推现行掉落'),
        ('老虎机','父目录','BET_RTP','不开展新机台模拟'),
        ('老虎机/CR机台建模规范','建模及统计说明','采用单位/条件/分母分层','程序/协议审计不纳入本任务'),
        ('老虎机/调控','空页面','特殊RTP独立','未补充优先级证据'),
        ('疯狂探险','2份配置＋体验附件','任务福利/FrenzyMission','旧推荐Bet与返还不沿用'),
        ('竞品调研','父目录','仅资料分类','竞品数值不导入'),
        ('竞品调研/弹球公园数值体验','游玩记录/图片/脚本/视频','仅参考表格结构','原始样本/媒体不进入新包'),
        ('竞品调研/tycoon翻地块','3 Sheet记录','仅参考资源列组织','竞品值不导入'),
        ('小游戏','父目录','薯片/777优先','不替User增加活动组合'),
        ('小游戏/薯片','3份同名/版本附件','薯片/商城_Pass','旧outPut单价不替代当前Unknown'),
        ('小游戏/挖宝','配置/累计/体验/备份','常驻资料参照','不新增活动体验模型'),
        ('小游戏/矿工','阶段/累计/奖励','结构已读','不加入9.22组合'),
        ('小游戏/幸运7','轮圈/消耗/奖励/Bet','777','旧每格一次清盘不替代forceTurn规则'),
        ('小游戏/新cr弹球数值','2份体验及进度附件','常驻资料参照','不新增活动体验模型'),
        ('未命名','空页面','无可提取内容','不补造功能'),
        ('建造','9 Sheet结构及报表说明','常驻：关闭与残留说明','旧周期目标/建设币收入不导入'),
    ]
    b.new('SRC_WIKI_REFERENCE',['模块','阅读到的结构','本表对应','版本/范围边界'],True)
    for r in wiki:b.append('SRC_WIKI_REFERENCE',list(r))
    b.section('常驻','系统功能全子模块阅读映射（结构参考，不是当前数值源）',['模块','结构','对应模块','边界'],[[f'={cell("SRC_WIKI_REFERENCE",i,j)}' for j in range(1,5)] for i in range(2,21)])
    section=b.sheets['常驻']['sections'][-1]
    for rn in range(section['row']-1,section['end']):
        b.sheets['常驻']['rows'][rn]=[v for value in b.sheets['常驻']['rows'][rn] for v in (value,None,None)]
    section['columns']=12;section['span']=3


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('analysis','sources','output'):p.add_argument('--'+n,required=True,type=Path)
    a=p.parse_args();out=a.output.resolve()
    if any((x/'.git').exists() for x in (out,*out.parents)):raise ValueError('完整内容只允许输出至Git以外受控目录')
    summary=json.loads((a.analysis/'summary.json').read_text(encoding='utf-8'))
    assert summary['applicability_revision']==7013
    b=Book(a.analysis,a.sources);build(b)
    from producer_workbook_layout import dual_layer
    dual_layer(b)
    fronts=[s for s in b.sheets.values() if not s['hidden']]
    hidden=[s for s in b.sheets.values() if s['hidden']]
    out.mkdir(parents=True,exist_ok=True)
    data={'title':'CR_9.22_数值体验表_r7013_MASTER','revision':7013,'evidence_revision':7013,
          'manifest_id':'TASK-0036-r7013-master-display-20260918','sheets':fronts+hidden,'checks':b.checks,
          'bindings':b.bindings,'source_specs':b.source_specs,'export_receipt':b.receipt}
    (out/'workbook-plan.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    public={'visible_sheets':[s['name'] for s in fronts],'source_tables':list(b.raw),'hidden_sheets':len(hidden),'accepted_comparisons':len(b.checks),'no_old_values':True,'svn_operation':'read-only export -r7013','no_hash':True}
    (out/'structure-summary.json').write_text(json.dumps(public,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'sheets':len(b.sheets),'visible':len(fronts),'checks':len(b.checks),'source_tables':len(b.raw)},ensure_ascii=False))


if __name__=='__main__':
    main()
