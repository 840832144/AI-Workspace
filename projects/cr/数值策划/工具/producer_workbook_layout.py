"""模块概览与完整明细；业务阶段分组，不抽样删行。"""
from __future__ import annotations
from collections import defaultdict
from typing import Any

MILESTONES = [1,10,20,30,40,50,75,100,125,150,300,400,500,600,700,800,900,1000,1100,1200,1400,1600,1800,2000,3000,4000,5000]
MODULES = {
    '基础金币': ('货币', ['DiamondChipExchange']),
    'VIP': ('VIP', ['VipCfg','VipPrivilege']),
    'BET_RTP': ('BET_RTP', ['SlotsCasinoBetList','SlotsCasinoNewbieConfig']),
    '等级': ('等级', ['LevelAward']),
    'Buff': ('Buff', ['LeagueBuff','Item','QuestBuffBag']),
    '美金金币档位': ('美金金币档位', ['PriceCheatSheet']),
    '任务福利': ('福利', ['FreeBonusHourly','CashRoyalTask','SignReward','OnlineReward','FrenzyMission']),
    '商城_Pass': ('商城_Pass', ['PriceSetting','SnackItemPack','SnackPassReward','BPRate','BPCfg','CommonBPLevelCondition']),
    '卡包卡册': ('卡包', ['SlotsCasinoDropCards','CardAlbumCfg','CardChapter','CardPack']),
    '薯片': ('薯片', ['SnackAddLuck','SnackDropItemCfg']),
    '777': ('777', ['StrikeLuckyRound','StrikeLucky']),
    '常驻': ('常驻', ['DailyTreasurePoint','VoyageChapter','SysUnlock']),
}


def jump(name: str, row: int, label: str = '打开明细') -> str:
    return f'=HYPERLINK("#\'{name}\'!A{row}","{label}")'


def dual_layer(b: Any) -> None:
    ordered: dict[str, dict] = {'总览': b.sheets['总览']}
    for old, (module, sources) in MODULES.items():
        detail = b.sheets.pop(old)
        dn = module + '_明细'
        on = module + ('_阶段概览' if module == '等级' else '_概览')
        detail['name'] = dn
        detail['style_key'] = old
        detail['rows'][0] = [dn]
        detail['rows'][3] = [jump(on, 1, '返回模块概览')]
        b.sheets[dn] = detail
        overview = b.new(on, [], note=detail['rows'][2][0])
        overview['style_key'] = old
        overview['rows'][3] = [jump(dn, 1, '完整明细：筛选 / 分组 / 逐行来源')]
        if old == '等级':
            levels = b.raw['LevelCfg']
            reasons: dict[int, set[str]] = defaultdict(set)
            for level in MILESTONES: reasons[level].add('旧表阅读节点（仅沿用等级标签）')
            for prev, current in zip(levels, levels[1:]):
                if (prev['levelUpType'],prev['levelUpVip']) != (current['levelUpType'],current['levelUpVip']):
                    reasons[current['level']].add('升级方式/VIP入账配置改变')
            award_map = {r['level']: r for r in b.raw['LevelAward']}
            for prev, current in zip(levels, levels[1:]):
                aa,bb = award_map.get(prev['level'],{}),award_map.get(current['level'],{})
                if tuple(aa.get(f) for f in ('rewardType','ItemId')) != tuple(bb.get(f) for f in ('rewardType','ItemId')):
                    reasons[current['level']].add('升级奖励类型/道具改变')
            for r in b.raw['PriceCheatSheet']:
                if (r['money'],r['priceType'],r['vipType']) == (100,17,1):
                    reasons[r['level']].add('金币美元换算配置档位')
            positions = {r['level']: i+2 for i,r in enumerate(levels)}
            boundaries = sorted(set(reasons) & set(positions))
            rows=[];groups=[]
            for i,start in enumerate(boundaries):
                end=boundaries[i+1]-1 if i+1<len(boundaries) else levels[-1]['level']
                a,c=positions[start],positions[end]
                # 升级类型为空时，即使经验门槛存在，也不解释为Spin或天数。
                rows.append([f'=CALC_LEVEL!A{a}',f'=CALC_LEVEL!A{c}', '；'.join(sorted(reasons[start])),
                    f'=IF(CALC_LEVEL!B{a}="","Unknown",CALC_LEVEL!B{a})',
                    f'=CALC_LEVEL!C{a}',f'=CALC_LEVEL!C{c}',
                    f'=IF(OR(CALC_LEVEL!B{a}="",COUNT(CALC_LEVEL!C{a}:C{c})<>ROWS(CALC_LEVEL!C{a}:C{c})),"Unknown",SUM(CALC_LEVEL!C{a}:C{c}))',
                    f'=IF(CALC_LEVEL!B{a}=1,"Spin（本阶段升级门槛之和）",IF(CALC_LEVEL!B{a}="","Unknown","经验（非Spin）"))',
                    f'=IF(COUNT(CALC_LEVEL!I{a}:I{c})<>ROWS(CALC_LEVEL!I{a}:I{c}),"Unknown/不适用",SUM(CALC_LEVEL!I{a}:I{c}))', jump(dn,a+5)])
                if c>a:groups.append([a+5,c+5])
            b.section(on,'等级阶段：连续门槛变化保留逐级明细，概览按业务边界分段',
                ['起始等级','结束等级','分段依据','升级type','首级门槛','末级门槛','区间门槛合计','合计单位/分母','区间VIP经验奖励','下钻'],rows)
            detail['groups']=groups
        elif old == '美金金币档位':
            groups=defaultdict(list)
            for r in b.raw['PriceCheatSheet']:groups[(r['money'],r['priceType'],r['vipType'])].append(r)
            rows=[]
            for key, rr in groups.items():
                levels=[b.ref('PriceCheatSheet',r,'level') for r in rr]
                values=[b.ref('PriceCheatSheet',r,'vip_16_0') for r in rr]
                rows.append([b.link('PriceCheatSheet',rr[0],f) for f in ('money','priceType','vipType')]+
                    ['=MIN('+','.join(levels)+')','=MAX('+','.join(levels)+')','=ROWS('+f"'{dn}'!A1:A{len(rr)}"+')',
                     '=MIN('+','.join(values)+')','=MAX('+','.join(values)+')',jump(dn,7+b.raw['PriceCheatSheet'].index(rr[0]))])
            b.section(on,'全部配置条件分组（金额/价值类型/VIP类型）；不混合不同计价分母',
                ['money原单位','priceType','vipType','最低等级档','最高等级档','完整档位行数','VIP0最低配置值','VIP0最高配置值','下钻'],rows)
        elif old == '商城_Pass':
            rows=[]
            for r in b.raw['PriceSetting']:
                rr=[b.link('PriceSetting',r,f) for f in ('money','currencyType','vipType')]
                rr += ['='+b.ref('PriceSetting',r,'money')+'/SRC_RULES!B5']
                rr += [b.link('PriceSetting',r,'vip'+str(v)) for v in (0,5,10,15)]
                rows.append(rr)
            b.section(on,'全部报价档：相同配置条件横向对比VIP，不把不同奖励单位相加',
                ['money','货币类型','VIP类型','配置标价USD','V0原奖励','V5原奖励','V10原奖励','V15原奖励'],rows,{4:'0.00'})
            b.section(on,'薯片Pass：免费/付费共享进度，每个等级是一处门槛变化',b.sheets['CALC_PASS']['rows'][0],
                [[f"='CALC_PASS'!{chr(65+j)}{r}" for j in range(8)] for r in range(2,17)])
        else:
            first=detail['sections'][0]
            # 第一段包含完整场景/完整VIP档/完整福利条件，不截前N条。
            rows=[list(r) for r in detail['rows'][first['row']:first['end']]]
            b.section(on, detail['rows'][first['row']-2][0], detail['rows'][first['row']-1],rows)
            for address, fmt in detail['formats']:
                # 第一段行位相同，可沿用该段格式。
                import re
                if max(map(int,re.findall(r'\d+',address))) <= first['end']:
                    overview['formats'].append([address,fmt])
        if old in ('薯片','777'):
            q=4 if old=='薯片' else 5
            stage=b.sheets['CALC_STAGE']['rows']
            config=[r for r in b.raw['QuestGetLevel'] if r['questType']==q]
            chunks=[]
            for r in config:
                key=(r['LevelUpPoints'],r['num'])
                if not chunks or chunks[-1][0]!=key:chunks.append((key,[r]))
                else:chunks[-1][1].append(r)
            rows=[]
            for key,rr in chunks:
                start=next(i for i,x in enumerate(stage,1) if i>1 and x[1]==b.link('QuestGetLevel',rr[0],'Id'))
                end=start+len(rr)-1
                rows.append([f'=CALC_STAGE!B{start}',f'=CALC_STAGE!B{end}',f'=CALC_STAGE!C{start}',f'=CALC_STAGE!D{start}',
                    f'=SUM(CALC_STAGE!C{start}:C{end})',f'=SUM(CALC_STAGE!D{start}:D{end})',f'=CALC_STAGE!E{end}',f'=CALC_STAGE!F{end}'])
            b.section(on,'获取阶段：相邻相同成本/奖励合并，所有变化点均保留',
                ['开始阶段','结束阶段','每阶段积分','每阶段道具','本段积分','本段道具','末端累计积分','末端累计道具'],rows)
            for table in ('QuestGetLevel','QuestPickGet','QuestPointsCheatSheet','QuestInitItem'):
                fields=b.source_specs[table]['fields']
                rows=[r for r in b.raw[table] if r['questType']==q]
                b.raw_view(dn,table+'：适用活动完整原行',table,fields,records=rows)
        for table in sources:
            fields=b.source_specs[table]['fields']
            if any(detail['rows'][sec['row']-1] == fields for sec in detail['sections']):continue
            b.raw_view(dn,table+'：完整配置原行/原字段',table,fields,records=b.raw[table])
        index=[]
        for sec in detail['sections']:
            index.append([detail['rows'][sec['row']-2][0], '=ROWS('+f"'{dn}'!A{sec['row']+1}:A{sec['end']}"+')',jump(dn,sec['row'])])
        b.section(on,'明细导航：保留全部配置行与条件，点击进入后筛选',['内容','记录数','打开'],index)
        ordered[on]=overview;ordered[dn]=detail
    ordered['Unknown']=b.sheets['Unknown']
    b.new('SRC_MANIFEST',['项目','固定值'],True)
    for row in [('任务','TASK-0036'),('版本清单','TASK-0036-r7013-master-display-20260918'),('源版本','trunk r7013 / svn export -r7013'),
                ('master','仅受控本机使用；相对外链 source/r7013/'),('展示版','内嵌相同已验证值；不更新外链'),
                ('来源','原始工作簿；旧Wiki只作结构参考'),('边界','尚未冻结或发布；9组Unknown保留')]:b.append('SRC_MANIFEST',list(row))
    for f in b.receipt['files']:b.append('SRC_MANIFEST',[f['file'],f['exported_at']])
    nav=[[n,jump(n,1,'进入模块')] for n in ordered if n!='总览']
    b.section('总览','模块阅读导航：概览 → 明细 → CALC → SRC → 原始r7013源格',['模块','跳转'],nav)
    b.sheets={**ordered,**{n:s for n,s in b.sheets.items() if s['hidden']}}
