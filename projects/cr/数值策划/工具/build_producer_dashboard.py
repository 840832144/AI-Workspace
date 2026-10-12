"""TASK-0036 9/20重构：复用Accepted外链计划，仅新增制作人计算与展示。

--baseline 旧受控master目录 --output 新受控目录（含固定revision导出）
不连接SVN，不读旧数值附件，不计算hash；随机样本及完整数值只写受控目录。
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import json
from pathlib import Path
from build_producer_workbook import Book,cell,col
from producer_workbook_sources import read_source
from producer_workbook_layout import MILESTONES,jump
from producer_dashboard_models import max_unlocked,lucky_simulation,snack_simulation,card_simulation,SEED

USD='"$"#,##0.00;[Red]("$"#,##0.00);"$"0.00'
PCT='0.0%';MULT='0.00"x"'
U='Unknown'


def restore(b: Book, old: Path) -> dict:
    p=json.loads((old/'workbook-plan.json').read_text(encoding='utf-8'))
    b.sheets={s['name']:s for s in p['sheets']};b.bindings=p['bindings'];b.source_specs=p['source_specs']
    for n,spec in b.source_specs.items():
        d=read_source(b.sources/spec['file']);allowed={r[0] for r in b.sheets['SRC_'+n]['rows'][1:]}
        b.raw[n]=[r for r in d['records'] if r['_excel_row'] in allowed]
        for rownum,r in enumerate(b.sheets['SRC_'+n]['rows'][1:],2):
            for c,f in enumerate(spec['fields'],3):b.refs[n,r[0],f]=cell('SRC_'+n,rownum,c)
    b.checks=[]  # 不重跑历史969项，只验证本轮新增制作人指标
    return p


def overview(b: Book,name: str,note: str,headers: list,rows: list,kpis: list,chartcols: list,formats: dict | None=None) -> int:
    s=b.new(name,[],note=note);s['dashboard']=True
    dn=name.replace('_阶段概览','_明细').replace('_概览','_明细')
    s['rows'][3]=[jump(dn,1,'查看完整明细') if dn!=name else jump('Unknown',1,'具体解释边界')]
    # 统一四个KPI；图表位于空白区，阶段表从第30行开始。
    s['kpis']=kpis
    for i,(label,formula,fmt) in enumerate(kpis):
        while len(s['rows'])<9:s['rows'].append([])
        c=i*3
        for r in (5,6):
            while len(s['rows'][r])<c+3:s['rows'][r].append(None)
        s['rows'][5][c]=label;s['rows'][6][c]=formula
        s['formats'].append([f'{col(c+1)}7:{col(c+3)}8',fmt])
    while len(s['rows'])<28:s['rows'].append([])
    first=b.section(name,'阶段与价值',headers,rows,formats)
    s['charts']=[{'title':title,'columns':cs,'start':first-1,'end':first+len(rows)-1,'position':pos,'type':kind,'format':fmt} for title,cs,pos,kind,fmt in chartcols]
    s['preview_range']='A1:M43'
    s['cost_columns']=[i+1 for i,h in enumerate(headers) if any(k in h for k in ['成本','净耗','标价','净成本'])]
    s['reward_columns']=[i+1 for i,h in enumerate(headers) if any(k in h for k in ['奖励','返还','回补'])]
    return first


def build(b: Book,cached: dict | None=None) -> dict:
    for n in ['SlotsCasinoBetUnlock','SlotsCasinoBetShow','CardList','CardGroup','PayDiamond','QuestJackpotCfg']:
        b.source(n)
    b.source('CommCfg',select=lambda r:r['id'] in (161,189,190,191,192,193))
    b.new('SRC_DECISIONS',['分析口径','值','依据'],True)
    decisions=[['等级成本RTP',.95,'TASK-0036 2026-09-20'],['VIP点/美元',100,'User已闭合'],['基础机型列',1,'旧正式BET二倍数制；另列全部五种机型敏感性，绑定仍Unknown'],['静态换算等级',500,'明确分析情景，不是玩家分布'],['静态VIP',0,'明确分析情景'],['初始盒子',20,'User覆盖配置随机缺盒'],['随机seed',SEED,'可复算模拟'],['777内圈成本',0,'User临时取奖返回；与r7013自动抽扣费不同'],['自然渠道初始道具',0,'User / 不混赠送']]
    for r in decisions:b.append('SRC_DECISIONS',r)
    b.new('CALC_PRO_RULES',['含义','值'],True)
    for k,v in [('等级RTP','=SRC_DECISIONS!B2'),('VIP点每美元','=SRC_DECISIONS!B3')]:b.append('CALC_PRO_RULES',[k,v])
    price=b.raw['PriceCheatSheet'];bets={r['levelId']:r for r in b.raw['SlotsCasinoBetList']}
    rates=[r for r in price if (r['money'],r['priceType'],r['vipType'])==(100,17,1)]
    def pr(level: int) -> dict:return max((r for r in rates if r['level']<=level),key=lambda r:r['level'])
    def rate(level: int, vip: int) -> str:return b.ref('PriceCheatSheet',pr(level),f'vip_16_{vip}')
    def rf(t: str, r: dict, f: str) -> str:return b.ref(t,r,f)
    def reward(t: str, r: dict, typ: str, amount: str, level: int = 500, vip: int = 0) -> str:
        kind=r.get(typ);q=rf(t,r,amount)
        if r.get(amount) is None:return '"Unknown"'
        if kind in (9,17):return q+'/100'
        if kind==1:return q+'/'+rate(level,vip)
        if kind==2:return q+'*CALC_DIAMOND!E2'
        return '"Unknown"'
    # 商店钻石档位全部保留。主估值采用可见商店最低标价档，额外列最大/最小兑换价值。
    dia=[r for r in b.raw['PayDiamond'] if r['payType']==1 and r['itemShow']==1 and r['currencyType']==2 and (r['diamond'] or 0)>0]
    dia.sort(key=lambda r:r['money_dollar'])
    b.new('CALC_DIAMOND',['SKU','标价USD','钻石','VIP点','USD/钻石','VIP点差额'],True)
    for r in dia:
        i=len(b.sheets['CALC_DIAMOND']['rows'])+1
        b.append('CALC_DIAMOND',[r['itemID'],'='+rf('PayDiamond',r,'money_dollar')+'/100','='+rf('PayDiamond',r,'diamond'),'='+rf('PayDiamond',r,'giveVipExp'),f'=B{i}/C{i}',f'=D{i}-B{i}*SRC_DECISIONS!B3'])
    # 完整5000逐级模型。r7013 CommCfg161=1，LevelUtils达到单次升级上限丢弃溢出。
    limit=next(r for r in b.raw['CommCfg'] if r['id']==161)
    assert limit['val']==1,'升级溢出策略变化，需重新解释'
    levels=b.raw['LevelCfg'];awards={r['level']:r for r in b.raw['LevelAward']}
    b.new('CALC_PRO_LEVEL',['等级','解锁档','推荐金币Bet','金币/USD','推荐Bet USD','EXP/Spin','门槛','模式','预计Spin','毛下注USD','净耗USD','奖励USD','净成本USD','累计净耗USD','累计Spin','累计奖励USD','前级净耗倍数','配置门槛原值'],True)
    for lev in levels:
        lv=int(lev['level']);i=lv+1;un=max_unlocked(b.raw['SlotsCasinoBetUnlock'],lv);br=bets[un['betlevel']]
        if lev['levelUpExp'] is None:raise ValueError('LevelCfg空门槛；不补0')
        ar=awards.get(lv+1)
        rew=reward('LevelAward',ar,'rewardType','money',lv+1,0) if ar else '"不适用"'
        if ar and (ar['diamond'] or 0):rew+='+'+rf('LevelAward',ar,'diamond')+'*CALC_DIAMOND!E2'
        b.append('CALC_PRO_LEVEL',['='+rf('LevelCfg',lev,'level'),'='+rf('SlotsCasinoBetUnlock',un,'betlevel'),
          '=CHOOSE(SRC_DECISIONS!B4,'+','.join(rf('SlotsCasinoBetList',br,f) for f in ('bet2','bet3','bet33','bet9','bet35'))+')',
          '='+rate(lv,0),f'=C{i}/D{i}','='+rf('SlotsCasinoBetList',br,'levelExp'),
          '=ROUND('+rf('LevelCfg',lev,'levelUpExp')+',0)','Spin' if lev['levelUpType']==1 else '经验',
          f'=IF(A{i}=5000,"不适用",IF(H{i}="Spin",G{i},ROUNDUP(G{i}/F{i},0)))',f'=IF(ISNUMBER(I{i}),I{i}*E{i},"不适用")',
          f'=IF(ISNUMBER(J{i}),J{i}*(1-SRC_DECISIONS!B2),"不适用")','='+rew,
          f'=IF(AND(ISNUMBER(K{i}),ISNUMBER(L{i})),K{i}-L{i},"Unknown")',f'=SUM(N{i-1},K{i})' if i>2 else f'=K{i}',f'=SUM(O{i-1},I{i})' if i>2 else f'=I{i}',f'=SUM(P{i-1},L{i})' if i>2 else f'=L{i}',
          f'=IF(ISNUMBER(K{i}),K{i}/K{i-1},"不适用")' if lv>1 else '不适用','='+rf('LevelCfg',lev,'levelUpExp')])
        if lv in (1,4,5,50,500,2000,4999):
            spins=lev['levelUpExp'] if lev['levelUpType']==1 else __import__('math').ceil(round(lev['levelUpExp'])/br['levelExp'])
            b.expected(cell('CALC_PRO_LEVEL',i,9),spins,'level_expected_spin')
            b.expected(cell('CALC_PRO_LEVEL',i,11),spins*br['bet2']/pr(lv)['vip_16_0']*.05,'level_cost_95')
            b.expected(cell('CALC_PRO_LEVEL',i,2),un['betlevel'],'max_unlocked_bet')
    detail=b.new('等级_明细',[],note='全5000级；最后一行是等级上限，不虚构5000→5001。模式空值按经验；单次升级上限1使溢出丢弃。')
    b.section('等级_明细','逐级完整成本与奖励',b.sheets['CALC_PRO_LEVEL']['rows'][0],[[f'=CALC_PRO_LEVEL!{col(c)}{r}' for c in range(1,19)] for r in range(2,5002)],{5:USD,10:USD,11:USD,12:USD,13:USD,14:USD,16:USD,17:MULT})
    b.raw_view('等级_明细','完整升级奖励原行','LevelAward',b.source_specs['LevelAward']['fields'])
    boundaries=set(MILESTONES)|{r['level'] for r in rates if r['level']>=1}
    prev=None
    for r in levels:
        sig=(max_unlocked(b.raw['SlotsCasinoBetUnlock'],r['level'])['betlevel'],r['levelUpType']==1)
        if sig!=prev:boundaries.add(r['level'])
        prev=sig
    boundaries=sorted(x for x in boundaries if 1<=x<=5000)
    stage=[]
    for k,start in enumerate(boundaries):
        end=min(boundaries[k+1]-1,4999) if k+1<len(boundaries) else 5000
        sr,er=start+1,end+1
        stage.append([f'{start}–{end}',f'=CALC_PRO_LEVEL!E{sr}',f'=SUM(CALC_PRO_LEVEL!I{sr}:I{er})',f'=SUM(CALC_PRO_LEVEL!J{sr}:J{er})',f'=SUM(CALC_PRO_LEVEL!K{sr}:K{er})',f'=SUM(CALC_PRO_LEVEL!L{sr}:L{er})',f'=E{31+k}-F{31+k}',f'=CALC_PRO_LEVEL!N{er}',f'=E{31+k}/E{30+k}' if k else '不适用',jump('等级_明细',start+6,'逐级下钻')])
    # section第一数据行31
    overview(b,'等级_阶段概览','V0；最大解锁Bet的二倍数制参考。五种机型列在BET明细；实际机台绑定仍Unknown。成本RTP固定95%。',
      ['等级段','推荐Bet $','预计Spin','毛下注 $','机器净耗 $','升级奖励 $','净成本 $','累计净耗 $','阶段膨胀','下钻'],stage,
      [('满级机器净耗','=CALC_PRO_LEVEL!N5000',USD),('累计升级奖励','=CALC_PRO_LEVEL!P5000',USD),('累计Spin','=CALC_PRO_LEVEL!O5000','#,##0'),('升级成本RTP','=SRC_DECISIONS!B2',PCT)],
      [('阶段净耗与返还',[1,5,6],['A10','G27'],'bar',USD),('累计升级成本',[1,8],['G10','M27'],'line',USD)],{2:USD,4:USD,5:USD,6:USD,7:USD,8:USD,9:MULT})
    # BET：按全部解锁变化点 × 4VIP × 5列显示，不将bet2冒充全部机台。
    b.new('CALC_PRO_BET',['等级','VIP','机型列','解锁档','金币Bet','金币/USD','Bet USD','常规RTP','100Spin净耗','500Spin净耗','1000Spin净耗','1000Spin毛下注'],True)
    for lv in boundaries:
        br=bets[max_unlocked(b.raw['SlotsCasinoBetUnlock'],lv)['betlevel']]
        for vip in (0,5,10,15):
            for f in ('bet2','bet3','bet33','bet9','bet35'):
                i=len(b.sheets['CALC_PRO_BET']['rows'])+1
                b.append('CALC_PRO_BET',[lv,vip,f,'='+rf('SlotsCasinoBetList',br,'levelId'),'='+rf('SlotsCasinoBetList',br,f),'='+rate(lv,vip),f'=E{i}/F{i}',f'=IF(G{i}<=1,0.95,0.85)',f'=100*G{i}*(1-H{i})',f'=500*G{i}*(1-H{i})',f'=1000*G{i}*(1-H{i})',f'=1000*G{i}'])
    b.section('BET_RTP_明细','最大解锁Bet：所有五种列与VIP',b.sheets['CALC_PRO_BET']['rows'][0],[[f'=CALC_PRO_BET!{col(c)}{r}' for c in range(1,13)] for r in range(2,len(b.sheets['CALC_PRO_BET']['rows'])+1)],{7:USD,8:PCT,9:USD,10:USD,11:USD,12:USD})
    brows=[[f'=CALC_PRO_BET!{col(c)}{2+k*20}' for c in (1,4,7,8,9,10,11,12)] for k in range(len(boundaries))]
    overview(b,'BET_RTP_概览','最大已解锁档。图示V0二倍数制参考；明细并列所有5列×4VIP，机台绑定不明不隐去。特殊RTP不与常规叠加。',
      ['等级','解锁档','推荐Bet $','常规RTP','100Spin净耗 $','500Spin净耗 $','1000Spin净耗 $','1000Spin毛下注 $'],brows,
      [('最高推荐Bet','=MAX(CALC_PRO_BET!G2:G'+str(len(b.sheets['CALC_PRO_BET']['rows']))+')',USD),('低档RTP','=SRC_RULES!B3',PCT),('高档RTP','=SRC_RULES!B4',PCT),('机型敏感性列',5,'0')],
      [('各阶段1000Spin净耗',[1,7],['A10','G27'],'line',USD),('Bet与RTP分界',[1,3],['G10','M27'],'line',USD)],{3:USD,4:PCT,5:USD,6:USD,7:USD,8:USD})
    # VIP：充值门槛与金币礼包，固定Level500估值；无等级EXP加成。
    b.new('CALC_PRO_VIP',['VIP','累计点','增量点','累计充值USD','增量充值USD','升级金币','礼包USD','净成本USD','任务加成','成就加成','等级EXP加成','兑换加成','成本膨胀','任务权益膨胀'],True)
    for r in b.raw['VipCfg']:
        v=r['vipLevel'];i=v+1;vr=next(x for x in b.raw['VipPrivilege'] if x['vipLevel']==v)
        b.append('CALC_PRO_VIP',['='+rf('VipCfg',r,'vipLevel'),'='+rf('VipCfg',r,'needExp'),f'=B{i}'+(f'-B{i-1}' if v>1 else ''),f'=B{i}/SRC_DECISIONS!B3',f'=C{i}/SRC_DECISIONS!B3','='+rf('VipPrivilege',vr,'GiftCoin'),f'=F{i}/'+rate(500,v),f'=E{i}-G{i}','='+rf('VipPrivilege',vr,'taskAddition')+'/100','='+rf('VipPrivilege',vr,'achievementAddition')+'/100',0,'='+rf('VipPrivilege',vr,'buyAddtion')+'/100',f'=E{i}/E{i-1}' if v>1 else '不适用',f'=(1+I{i})/(1+I{i-1})' if v>1 else '不适用'])
        b.expected(cell('CALC_PRO_VIP',i,4),r['needExp']/100,'vip_payment')
    b.sheets['VIP_明细']['rows'][2]=['VIP点只按充值100点/$；旧经验系数为关闭/历史字段，不用于等级成长。礼物按Level500本VIP档折USD。']
    b.section('VIP_明细','支付门槛与权益',b.sheets['CALC_PRO_VIP']['rows'][0],[[f'=CALC_PRO_VIP!{col(c)}{r}' for c in range(1,15)] for r in range(2,17)],{4:USD,5:USD,7:USD,8:USD,9:PCT,10:PCT,11:PCT,12:PCT,13:MULT,14:MULT})
    vrows=[[f'=CALC_PRO_VIP!{col(c)}{r}' for c in (1,3,2,5,4,7,8,9,10,13,14)] for r in range(2,17)]
    overview(b,'VIP_概览','每$1=100VIP点；礼包金币估值固定Level500、本VIP。权益物品另列，未强行美元化。等级经验加成=0。',
      ['VIP','增量点','累计点','本级成本 $','累计充值 $','金币礼包 $','净成本 $','任务加成','成就加成','成本膨胀','权益膨胀'],vrows,
      [('最高VIP累计充值','=CALC_PRO_VIP!D16',USD),('累计金币礼包','=SUM(CALC_PRO_VIP!G2:G16)',USD),('VIP点/美元','=SRC_DECISIONS!B3','0'),('等级经验加成',0,PCT)],
      [('升级支付与礼包',[1,4,6],['A10','G27'],'bar',USD),('任务与成就权益',[1,8,9],['G10','M27'],'line',PCT)],{4:USD,5:USD,6:USD,7:USD,8:PCT,9:PCT,10:MULT,11:MULT})
    # 货币与完整美元档位，沿用现有21档换算公式。
    cr=[]
    for i in range(2,len(b.sheets['CALC_COINS']['rows'])+1):
        cr.append([f'=CALC_COINS!{c}{i}' for c in 'ABCDE']+[f'=CALC_COINS!B{i}/CALC_COINS!B{i-1}' if i>2 else '不适用'])
    for name in ('货币_概览','美金金币档位_概览'):
        overview(b,name,'普通金币按当前等级/VIP档折算；9/17按配置美元分÷100。钻石采用可见商店最低价档，全部价档和差异见明细。',
          ['等级','V0金币/$','V5金币/$','V10金币/$','V15金币/$','相邻膨胀'],cr,
          [('基准金币/$','=CALC_COINS!B2','#,##0'),('末档金币/$','=CALC_COINS!B22','#,##0'),('钻石最低单位价','=MIN(CALC_DIAMOND!E2:E'+str(len(dia)+1)+')',USD),('钻石最高单位价','=MAX(CALC_DIAMOND!E2:E'+str(len(dia)+1)+')',USD)],
          [('等级/VIP的金币购买力',[1,2,3,4],['A10','G27'],'line','0.0,,"M"'),('相邻等级档膨胀',[1,6],['G10','M27'],'bar',MULT)],{2:'0.0,,"M"',3:'0.0,,"M"',4:'0.0,,"M"',5:'0.0,,"M"',6:MULT})
    b.section('货币_明细','当前商店钻石档位',b.sheets['CALC_DIAMOND']['rows'][0],[[f'=CALC_DIAMOND!{col(c)}{r}' for c in range(1,7)] for r in range(2,len(dia)+2)],{2:USD,5:'$0.0000'})
    # Buff仅保留有效模块；历史/关闭项集中索引，不作为当前收益。
    buffs=[]
    for r in b.raw['VipPrivilege']:
        buffs.append([r['vipLevel'],'='+rf('VipPrivilege',r,'FreechipsRate')+'/100','='+rf('VipPrivilege',r,'slotTaskRewardRate')+'/100','历史Pass不计入',jump('关闭_历史配置',1,'历史字段索引'),0])
    b.new('Buff_明细',[],note='完整VIP原字段留SRC；League、轮盘、经验与牌桌权益归关闭/历史。')
    b.section('Buff_明细','有效模块的加成映射',['VIP','小时福利倍率','Slots任务加成','已迁出字段','来源','等级EXP加成'],buffs,{2:MULT,3:PCT,6:PCT})
    overview(b,'Buff_概览','仅列小时福利、Slots任务。通用Pass加成未证实适用于薯片，已移关闭/历史索引；不加入薯片奖励。等级EXP不吃VIP加成。',
      ['VIP','福利倍率','Slots任务加成','已迁出字段','来源','等级EXP加成'],buffs,
      [('有效映射模块',2,'0'),('最高福利倍率','=MAX(\'Buff_明细\'!B7:B22)',MULT),('最高任务加成','=MAX(\'Buff_明细\'!C7:C22)',PCT),('等级EXP加成',0,PCT)],
      [('当前有效福利与任务权益',[1,2,3],['A10','M27'],'line',MULT)],{2:MULT,3:PCT,6:PCT})
    # 福利按原周期逐项列，不相加互斥领取方案。
    welfare=[]
    for i in (2,3):welfare.append(['小时福利方案'+str(i-1),f'=CALC_WELFARE!D{i}/60',f'=CALC_WELFARE!E{i}',f'=CALC_WELFARE!C{i}','分钟/每次；两方案互斥','金币；配置分÷100'])
    for r in b.raw['CashRoyalTask']:
        welfare.append([r['taskName'],'重置类型'+str(r['resetType']),'='+rf('CashRoyalTask',r,'chip')+'/'+rate(500,0),'逐任务条件','不与关闭牌桌/比赛任务叠加','普通金币 / Level500 V0'])
    for r in b.raw['SignReward']:
        welfare.append(['签到第'+str(r['day'])+'天','每日一次','='+reward('SignReward',r,'RewardType1','chip'),r['day'],'连续签到；物品另列','9/17配置分÷100'])
    for r in b.raw['OnlineReward']:
        welfare.append(['在线档'+str(r['rewardID']),'='+rf('OnlineReward',r,'onlineTime')+'/60','='+rf('OnlineReward',r,'chip')+'/'+rate(500,0),'在线分钟','周期重置未明，不能推日总量','普通金币 / Level500 V0'])
    for r in b.raw['FrenzyMission']:
        if r['RewardType1'] is not None:welfare.append(['探险任务'+str(r['MissionId']),'一次性','='+reward('FrenzyMission',r,'RewardType1','RewardNum1'),r['Level'],'任务类型/机台/参数见明细','非钱资源不计'])
    overview(b,'福利_概览','各自领取/刷新周期；表中美元等于同额机器净耗的回补能力，不能据此推每日总收入。',
      ['领取项','周期/分钟','回补净耗 $','解锁/阶段','适用条件','估值口径'],welfare,
      [('签到周期',7,'0"天"'),('在线奖励档',len(b.raw['OnlineReward']),'0'),('小时福利方案',2,'0'),('静态估值等级','=SRC_DECISIONS!B5','0')],
      [('分领取项的可计价回补',[1,3],['A10','M27'],'bar',USD)],{3:USD})
    # 商店：显式基础投放，礼包混合资源和VIP点差异单独显示。
    shop=[]
    skus=[r for r in b.raw['PayDiamond'] if r['payType']==1 and (r['itemShow']==1 or 'snack' in r['itemID'].lower())]
    b.new('CALC_PRO_SHOP',['SKU','标价USD','钻石','固定金币','可计价基础USD','回报倍数','VIP点','点数差额','其他资源/口径'],True)
    for r in skus:
        i=len(b.sheets['CALC_PRO_SHOP']['rows'])+1
        rr='='+rf('PayDiamond',r,'diamond')+'*CALC_DIAMOND!E2+'+rf('PayDiamond',r,'chip')+'/'+rate(500,0)
        if r['currencyType']==1 and not r['chip']:rr='="Unknown"'
        other='道具/卡包分账；价格表换算型金币尚需商品调用口径' if r['currencyType']==1 else '钻石按最低标价档；其他道具未计价'
        pack=next((x for x in b.raw['SnackItemPack'] if x['itemId_gp']==r['itemID']),None)
        if pack and pack['type']==1:
            amounts=[reward('SnackItemPack',pack,f'rewardType_2_{j}',f'rewardNum_2_{j}') for j in (0,1) if pack.get(f'rewardType_2_{j}') in (1,2,9,17)]
            rr='='+('+'.join(amounts) if amounts else '"Unknown"')
            other='当前SnackItemPack可计价奖励；薯片/幸运值另列原明细，不改变自然单位价值'
        elif pack and pack['type']==2:
            amounts=[reward('SnackPassReward',x,f'rewardType_2_{j}',f'rewardNum_2_{j}') for x in b.raw['SnackPassReward'] if x['category']==1 for j in (0,1) if x.get(f'rewardType_2_{j}') in (1,2,9,17)]
            rr='='+('+'.join(amounts) if amounts else '"Unknown"')
            other='黄金Pass全完成潜在奖励；需购买并达共享门槛，可追领；完成成本/缺口见薯片，不是即时回报'
        b.append('CALC_PRO_SHOP',[r['itemID'],'='+rf('PayDiamond',r,'money_dollar')+'/100','='+rf('PayDiamond',r,'diamond'),'='+rf('PayDiamond',r,'chip'),rr,f'=IF(ISNUMBER(E{i}),E{i}/B{i},"Unknown")','='+rf('PayDiamond',r,'giveVipExp'),f'=G{i}-B{i}*SRC_DECISIONS!B3',other])
        shop.append([f'=CALC_PRO_SHOP!{col(c)}{i}' for c in (1,2,5,6,7,8,9)])
    overview(b,'商城_Pass_概览','有效Pass仅薯片。商店给出可确认基础奖励，不把缺少换算调用口径的SKU补零。点数差额只作一致性提示。',
      ['SKU','标价 $','基础奖励 $','回报倍数','VIP点','点数差额','分账/缺口'],shop,
      [('有效Pass',1,'0'),('商店/Snack SKU',len(skus),'0'),('薯片Pass价格',next(('='+rf('PayDiamond',r,'money_dollar')+'/100' for r in skus if 'snackpass' in r['itemID'].lower()),'Unknown'),USD),('VIP点/美元','=SRC_DECISIONS!B3','0')],
      [('商店价格与可计价基础奖励',[1,2,3],['A10','G27'],'bar',USD),('商品VIP点差额',[1,6],['G10','M27'],'bar','0')],{2:USD,3:USD,4:MULT})
    # 自然活动获取：当前等级/VIP/最大解锁档，连续积分累计；每个道具使用精确首达命中次数。
    profiles=[]
    for label,lv,vip,daily in [('低档',50,0,100),('中档',500,5,500),('高档',2000,10,1000)]:
        profiles.append({'name':label,'level':lv,'vip':vip,'bet_index':max_unlocked(b.raw['SlotsCasinoBetUnlock'],lv)['betlevel'],'daily_spin':daily})
    b.new('CALC_PRO_ACQUIRE',['玩家档','活动','等级','VIP','推荐Bet USD','RTP','命中概率','每次命中积分','累计所需道具','累计积分门槛','所需命中','期望Spin','机器净耗USD','自然单位USD'],True)
    acquisition={};acquisition_rows={}
    for prof in profiles:
        for qt in (4,5):
            pick=next(r for r in b.raw['QuestPickGet'] if r['questType']==qt and r['Type']==2 and r['BetId']==prof['bet_index'])
            prs=[r for r in b.raw['QuestPointsCheatSheet'] if r['questType']==qt and r['Id']==pick['Id'] and r['level']<=prof['level']];points=max(prs,key=lambda r:r['level'])
            stages=sorted([r for r in b.raw['QuestGetLevel'] if r['questType']==qt],key=lambda r:r['Id'])
            br=bets[prof['bet_index']];first=None;cnt=0
            resolved=[]
            for st in stages:
                i=len(b.sheets['CALC_PRO_ACQUIRE']['rows'])+1;first=first or i;cnt+=st['num']
                b.append('CALC_PRO_ACQUIRE',[prof['name'],qt,prof['level'],prof['vip'],'='+rf('SlotsCasinoBetList',br,'bet2')+'/'+rate(prof['level'],prof['vip']),f'=IF(E{i}<=1,.95,.85)','='+rf('QuestPickGet',pick,'Probability')+'/1000','='+rf('QuestPointsCheatSheet',points,'vip_16_'+str(prof['vip'])),
                  '='+rf('QuestGetLevel',st,'num')+(f'+I{i-1}' if i>first else ''),'='+rf('QuestGetLevel',st,'LevelUpPoints')+(f'+J{i-1}' if i>first else ''),f'=IF(H{i}>0,ROUNDUP(J{i}/H{i},0),"Unknown")',f'=IF(ISNUMBER(K{i}),K{i}/G{i},"Unknown")',f'=IF(ISNUMBER(L{i}),L{i}*E{i}*(1-F{i}),"Unknown")',f'=IF(ISNUMBER(M{i}),M{i}/I{i},"Unknown")'])
                resolved.append((cnt,i))
            acquisition[prof['name'],qt]=(first,i)
            acquisition_rows[prof['name'],qt]=resolved
    def acquire_formula(profile: str, qt: int, count: str | int) -> str:
        # 固定r7013离散样本的阶段路由由生成器解析，金额仍由源格公式计算。
        # 随机状态/发放数量变更需要重跑本模块生成器，不伪称Excel能重跑Monte Carlo。
        target=next((i for n,i in acquisition_rows[profile,qt] if n>=int(count)),None)
        return f'CALC_PRO_ACQUIRE!M{target}' if target is not None else '"Unknown"'
    # 777样本的付费圈计数与奖励格计数分开，Excel按源成本/奖励复算。
    lucky,lc=(cached['simulation_rows']['lucky'],cached['simulation_checks']['lucky']) if cached else lucky_simulation(b.raw)
    if 'paid_special' not in lucky[0]:lucky,lc=lucky_simulation(b.raw)
    b.new('CALC_SIM_777',['样本','轮','外圈付费次数','中圈付费次数','内圈付费次数','外圈特殊次数','中圈特殊次数','总骰子','基础奖励USD','樱桃阶段USD','7终局USD','总返还USD','卡包数'],True)
    for rec in lucky:
        rd=next(r for r in b.raw['StrikeLuckyRound'] if r['round']==rec['round']);i=len(b.sheets['CALC_SIM_777']['rows'])+1
        gr=[r for r in b.raw['StrikeLucky'] if r['round']==rec['round'] and r['itemId']!=215006]
        base='+'.join(reward('StrikeLucky',r,'itemType','itemCount') for r in gr if r['itemType'] in (1,2,9,17)) or '0'
        packs='+'.join(rf('StrikeLucky',r,'itemCount') for r in gr if r['itemType']==4) or '0'
        b.append('CALC_SIM_777',[rec['sample'],rec['round']]+rec['paid']+rec['special'][:2]+[
          '='+ '+'.join(f'{col(c+3)}{i}*'+rf('StrikeLuckyRound',rd,'costCount_3_'+str(c)) for c in range(3)),
          '='+base,'='+reward('StrikeLuckyRound',rd,'cherryItemType','cherryItemCount'),'='+reward('StrikeLuckyRound',rd,'sevenItemType','sevenItemCount'),f'=SUM(I{i}:K{i})','='+packs])
    lrows=[]
    for prof in profiles:
        for rd in b.raw['StrikeLuckyRound']:
            idx=[i+2 for i,x in enumerate(lucky) if x['round']==rd['round']]
            b.new('CALC_777_'+prof['name']+'_'+str(rd['round']),['样本','累计骰子','累计净耗USD'],True)
            sn='CALC_777_'+prof['name']+'_'+str(rd['round'])
            for j,i in enumerate(idx,2):
                records=lucky[i-rd['round']-1:i-1]
                quantity=sum(sum(n*raw_rd[f'costCount_3_{c}'] for c,n in enumerate(rec['paid'])) for rec in records for raw_rd in b.raw['StrikeLuckyRound'] if raw_rd['round']==rec['round'])
                b.append(sn,[j-2,f'=SUM(CALC_SIM_777!H{i-rd["round"]+1}:H{i})','='+acquire_formula(prof['name'],5,quantity)])
            row=len(lrows)+31
            previous='CALC_777_'+prof['name']+'_'+str(rd['round']-1)
            bd=f'-AVERAGE({previous}!B2:B1001)' if rd['round']>1 else ''
            cd=f'-AVERAGE({previous}!C2:C1001)' if rd['round']>1 else ''
            lrows.append([prof['name'],rd['round'],f'=AVERAGE({sn}!B2:B1001)'+bd,f'=IF(COUNT({sn}!C2:C1001)=1000,AVERAGE({sn}!C2:C1001){cd},"Unknown")',f'=CALC_SIM_777!I{idx[0]}',f'=CALC_SIM_777!J{idx[0]}',f'=CALC_SIM_777!K{idx[0]}',f'=SUM(E{row}:G{row})',f'=IF(ISNUMBER(D{row}),H{row}/D{row},"Unknown")',f'=IF(ISNUMBER(D{row}),D{row}-H{row},"Unknown")',f'=CALC_SIM_777!M{idx[0]}','Estimate：三轮连续积分；内圈按User规则'])
    overview(b,'777_概览','每轮从外圈、0自然道具起；1000样本。特殊格临时进入下一内圈免费取奖并消格后返回。源代码自动内圈仍扣费，分析遵User规则，不能声称运行一致。',
      ['玩家档','轮','预计骰子','机器净耗 $','基础返还 $','樱桃返还 $','7终局 $','总返还 $','返还率','净成本 $','卡包数量','结论'],lrows,
      [('模拟样本/轮',1000,'0'),('配置轮数',3,'0'),('内圈额外成本','=SRC_DECISIONS!B9','0'),('初始自然道具',0,'0')],
      [('各档每轮成本与返还',[1,4,8],['A10','G27'],'bar',USD),('每轮预计骰子',[2,3],['G10','M27'],'bar','0.0')],{3:'0.0',4:USD,5:USD,6:USD,7:USD,8:USD,9:PCT,10:USD})
    b.section('777_明细','圈与轮模拟样本；成本公式引用r7013',b.sheets['CALC_SIM_777']['rows'][0],[[f'=CALC_SIM_777!{col(c)}{i}' for c in range(1,14)] for i in range(2,len(lucky)+2)],{9:USD,10:USD,11:USD,12:USD})
    b.new('CALC_777_CIRCLE',['轮','圈','样本','普通付费命中','特殊付费命中','累计骰子','累计机器净耗USD'],True)
    running=defaultdict(int)
    for rec in lucky:
        rd=next(r for r in b.raw['StrikeLuckyRound'] if r['round']==rec['round'])
        for c in range(3):
            i=len(b.sheets['CALC_777_CIRCLE']['rows'])+1
            qty=rec['paid'][c]*rd[f'costCount_3_{c}'];running[rec['sample']]+=qty
            prev=f'F{i-1}' if rec['round']>1 or c>0 else '0'
            b.append('CALC_777_CIRCLE',[rec['round'],c+1,rec['sample'],rec['paid'][c]-rec['paid_special'][c],rec['paid_special'][c],f'={prev}+(D{i}+E{i})*'+rf('StrikeLuckyRound',rd,f'costCount_3_{c}'),'='+acquire_formula('中档',5,running[rec['sample']])])
    circles=[]
    for rd in b.raw['StrikeLuckyRound']:
        for c in range(3):
            row=31+len(circles)
            avg=lambda field: f'AVERAGEIFS(CALC_777_CIRCLE!{field}2:{field}9001,CALC_777_CIRCLE!A2:A9001,{rd["round"]},CALC_777_CIRCLE!B2:B9001,{c+1})'
            gr=[r for r in b.raw['StrikeLucky'] if r['round']==rd['round'] and r['inout']==c+1 and r['itemId']!=215006]
            base='+'.join(reward('StrikeLucky',r,'itemType','itemCount') for r in gr if r['itemType'] in (1,2,9,17)) or '0'
            circles.append([rd['round'],['外圈','中圈','内圈'][c],'='+avg('D'),'='+avg('E'),'='+f'({avg("D")}+{avg("E")})*'+rf('StrikeLuckyRound',rd,f'costCount_3_{c}'),'='+avg('G'),'='+base,'中档；累计净耗含前轮；普通奖励含特殊提前取得'])
    b.section('777_概览','圈层成本：普通与特殊付费命中分开',['轮','圈','普通付费次数','特殊付费次数','本圈骰子','累计机器净耗USD','本圈普通奖励USD','说明'],circles,{3:'0.0',4:'0.0',5:'0.0',6:USD,7:USD})
    # 薯片样本：只保存随机抽取计数，奖励金额仍用源格公式计算。
    snack,sc=(cached['simulation_rows']['snack'],cached['simulation_checks']['snack']) if cached else snack_simulation(b.raw)
    b.new('CALC_SIM_SNACK',['样本','阶段','薯片消耗','奖券','基础USD','JackpotUSD','免费PassUSD','黄金PassUSD','总免费返还USD','自然净耗USD','预计Spin'],True)
    free=sorted([r for r in b.raw['SnackPassReward'] if r['category']==0],key=lambda r:r['levelId'])
    paid=sorted([r for r in b.raw['SnackPassReward'] if r['category']==1],key=lambda r:r['levelId'])
    jp=sorted([r for r in b.raw['QuestJackpotCfg'] if r['Type']==4],key=lambda r:r['Id'])
    for rec in snack:
        i=len(b.sheets['CALC_SIM_SNACK']['rows'])+1
        base='+'.join(str(count)+'*'+rf('SnackDropItemCfg',next(r for r in b.raw['SnackDropItemCfg'] if r['_excel_row']==int(ex)),'chipNum')+'/100' for ex,count in rec['coin_rows'].items()) or '0'
        jackpot='+'.join(str(n)+'*('+reward('QuestJackpotCfg',r,'RewardType','RewardNum')+')' for n,r in zip(rec['jackpots'],jp))
        threshold=0;fr=[];pa=[]
        for a,z in zip(free,paid):
            threshold+=a['LevelExp']
            if rec['tickets']>=threshold:
                for r,arr in ((a,fr),(z,pa)):
                    for slot in (0,1):
                        if r.get(f'rewardType_2_{slot}') in (1,2,9,17):arr.append(reward('SnackPassReward',r,f'rewardType_2_{slot}',f'rewardNum_2_{slot}'))
        midstart=acquisition['中档',4][0]
        b.append('CALC_SIM_SNACK',[rec['sample'],rec['stage'],rec['draws'],rec['tickets'],'='+base,'='+jackpot,'='+('+'.join(fr) or '0'),'='+('+'.join(pa) or '0'),f'=SUM(E{i}:G{i})','='+acquire_formula('中档',4,rec['draws']),f'=IF(ISNUMBER(J{i}),J{i}/(CALC_PRO_ACQUIRE!E{midstart}*(1-CALC_PRO_ACQUIRE!F{midstart})),"Unknown")'])
    srows=[]
    for label in [f'Pass {r["levelId"]}' for r in free]+['首次Grand','20次开盒','50次开盒','100次开盒','160次开盒','200次开盒']:
        ids=[i+2 for i,x in enumerate(snack) if x['stage']==label]
        row=len(srows)+31
        # AVERAGE 参数上限；整列SUMIF/COUNTIF用于可复算分组。
        def avg(c: str) -> str:return f'SUMIF(CALC_SIM_SNACK!B2:B{len(snack)+1},A{row},CALC_SIM_SNACK!{c}2:{c}{len(snack)+1})/COUNTIF(CALC_SIM_SNACK!B2:B{len(snack)+1},A{row})'
        unknown_count=f'COUNTIFS(CALC_SIM_SNACK!B2:B{len(snack)+1},A{row},CALC_SIM_SNACK!J2:J{len(snack)+1},"Unknown")'
        srows.append([label,'='+avg('C'),f'=IF({unknown_count}=0,{avg("J")},"Unknown：自然产出封顶")','='+avg('E'),'='+avg('F'),'='+avg('G'),'='+avg('H'),f'=SUM(D{row}:F{row})',f'=IF(ISNUMBER(C{row}),H{row}/C{row},"Unknown")',f'=IF(ISNUMBER(C{row}),C{row}-H{row},"Unknown")',f'=IF(ISNUMBER(C{row}),C{row}/B{row},"Unknown")',f'=1-{unknown_count}/400',f'=IF({unknown_count}=0,{avg("K")},"Unknown：自然产出封顶")'])
    overview(b,'薯片_概览','初始0道具、20盒；重置满20，JP清零重复。按样本首达成本计算，免费/黄金Pass分账；黄金不计免费总返还。',
      ['阶段/截面','预计薯片','机器净耗 $','基础奖励 $','Jackpot $','免费Pass $','黄金Pass另计 $','潜在免费返还 $','返还率','净成本 $','自然单位 $','自然上限内完成率','预计Spin'],srows,
      [('初始盒子','=SRC_DECISIONS!B7','0'),('每次消耗',1,'0'),('样本数',400,'0'),('初始自然道具',0,'0')],
      [('阶段成本与潜在免费返还',[1,3,8],['A10','G27'],'bar',USD),('自然上限内完成率',[1,12],['G10','M27'],'bar',PCT)],{2:'0.0',3:USD,4:USD,5:USD,6:USD,7:USD,8:USD,9:PCT,10:USD,11:USD,12:PCT})
    b.section('薯片_明细','模拟阶段首达与奖励分层',b.sheets['CALC_SIM_SNACK']['rows'][0],[[f'=CALC_SIM_SNACK!{col(c)}{i}' for c in range(1,12)] for i in range(2,len(snack)+2)],{5:USD,6:USD,7:USD,8:USD,9:USD,10:USD})
    scenarios=[]
    for prof in profiles:
        for draws in (20,50,100,160):
            scenarios.append([prof['name'],draws,'='+acquire_formula(prof['name'],4,str(draws)),
                '='+acquire_formula(prof['name'],4,str(draws))+'/'+str(draws),
                '按获取指定道具数的期望首达成本；不把平均进度代入随机奖励'])
    b.section('薯片_概览','多个机器净耗区间：自然获取同样道具量的成本',['玩家档','薯片数量','期望净耗USD','自然单位USD','分母/说明'],scenarios,{3:USD,4:USD})
    # 卡册：按实际章、卡池和进度模拟。季末未完成保留删失，严禁按卡数均摊。
    cards,cc=(cached['simulation_rows']['cards'],cached['simulation_checks']['cards']) if cached else card_simulation(b.raw,profiles)
    b.new('CALC_SIM_ALBUM',['档','样本','UID权重档','章','首次完成Spin','季末Spin上限','完成','已开包','唯一卡'],True)
    for r in cards:b.append('CALC_SIM_ALBUM',[r['profile'],r['sample'],r['uid_class'],r['chapter'],r['spins'] if r['spins'] is not None else '未完成',r['horizon'],r['complete'],r['opened'],r['unique']])
    album=max(b.raw['CardAlbumCfg'],key=lambda r:r['startTime']);chapters=[r for r in b.raw['CardChapter'] if r['seasonId']==album['id'] and not r['isPrestige']]
    cardrows=[]
    for prof in profiles:
        br=bets[prof['bet_index']]
        for ch in chapters+[None]:
            row=len(cardrows)+31;key=ch['id'] if ch else '整册';subset=[(i+2,r) for i,r in enumerate(cards) if r['profile']==prof['name'] and r['chapter']==key]
            complete=sum(r['complete'] for _,r in subset)
            # 无删失才展示样本完成时间均值；否则精确标Unknown，不报条件均值冒充期望。
            spin='=('+ '+'.join(f'CALC_SIM_ALBUM!E{i}' for i,r in subset)+')/100' if complete==100 else 'Unknown：季末删失'
            rew=reward('CardChapter',ch,'rewardType','chapterCoins',prof['level'],prof['vip']) if ch else '+'.join(reward('CardChapter',r,'rewardType','chapterCoins',prof['level'],prof['vip']) for r in chapters)+'+'+reward('CardAlbumCfg',album,'rewardType','albumCoins',prof['level'],prof['vip'])
            completion='=('+ '+'.join(f'CALC_SIM_ALBUM!G{i}' for i,r in subset)+')/100'
            cardrows.append([prof['name'],key,'='+rf('CardChapter',ch,'cardNum') if ch else '='+rf('CardAlbumCfg',album,'cardNum'),spin,'='+rf('SlotsCasinoBetList',br,'bet2')+'/'+rate(prof['level'],prof['vip']),f'=IF(ISNUMBER(D{row}),D{row}*E{row}*(1-IF(E{row}<=1,.95,.85)),"Unknown")','='+rew,f'=IF(ISNUMBER(F{row}),G{row}/F{row},"Unknown")',f'=IF(ISNUMBER(F{row}),F{row}-G{row},"Unknown")',f'=IF(AND(ISNUMBER(F{row}),ISNUMBER(F{row-1})),F{row}/F{row-1},"Unknown")' if ch and ch!=chapters[0] else '不适用',completion,'Estimate：季内自然渠道；章成本含并行收集，不能逐章相加'])
    overview(b,'卡包_概览','空册/赛季第1天；低中高固定等级/VIP，日Spin100/500/1000仅敏感性；10个UID权重档等配。季末删失不补期望，高阶整册待普通册完成后另算。',
      ['玩家档','章节','需集卡数','预计Spin','推荐Bet $','机器净耗 $','章/册返还 $','返还率','净成本 $','前章成本倍数','季内完成率','边界'],cardrows,
      [('普通册章节','='+rf('CardAlbumCfg',album,'passageNum'),'0'),('普通册卡数','='+rf('CardAlbumCfg',album,'cardNum'),'0'),('每档样本',100,'0'),('代表档',3,'0')],
      [('章节可计价返还',[2,7],['A10','G27'],'bar',USD),('自然渠道季内完成率',[2,11],['G10','M27'],'bar',PCT)],{5:USD,6:USD,7:USD,8:PCT,9:USD,10:MULT,11:PCT})
    b.section('卡包_明细','完整章节模拟样本与删失',b.sheets['CALC_SIM_ALBUM']['rows'][0],[[f'=CALC_SIM_ALBUM!{col(c)}{i}' for c in range(1,10)] for i in range(2,len(cards)+2)])
    # 当前常驻与全部功能路由；User关闭状态优先于源表残留。
    closed=['建造','比赛/牌桌','Spades','联盟','赛马/龙虎','马戏团','轮盘','非薯片BP/Pass']
    b.new('关闭_历史配置',[],note='不计入当前经济。VipPrivilege.passLevelReward/passFinalReward是历史Pass字段，尚未证明适用于薯片，原值保留SRC；不加入薯片奖励。')
    b.section('关闭_历史配置','当前关闭',['模块','现行决定','历史源'],[[x,'关闭 / 不计入当前经济','SRC保留；不改变源配置'] for x in closed])
    b.section('关闭_历史配置','关闭Buff / 历史字段',['来源','字段/用途','说明'],[['LeagueBuff','整表','联盟关闭'],['VipPrivilege','expRate/expAddtion','不提供等级EXP加成'],['VipPrivilege','FreeSpinRate/SuperSpinRate','轮盘关闭'],['VipPrivilege','牌桌/联赛权益','当前不计经济']])
    resident=[]
    for r in b.raw['VoyageChapter']:
        vals=[];other=[]
        for part in ('stage','travel'):
            for i in range(4):
                k=r.get(f'{part}Reward_4_{i}');n=r.get(f'{part}RewardNum_4_{i}')
                if k==1 and n is not None:vals.append(rf('VoyageChapter',r,f'{part}RewardNum_4_{i}')+'/'+rate(500,0))
                elif k and n:other.append(str(k)+':'+str(n))
        resident.append(['航行 '+str(r['chapterId'])+'-'+str(r['stageId']),'='+rf('VoyageChapter',r,'unlockLevel'),'依船/物品容量','='+('+'.join(vals) or '0'),'Unknown：需求物品获取成本',' / '.join(other),'配置路径已还原；本期启用关系待确认'])
    for r in b.raw['DailyTreasurePoint']:resident.append(['每日宝箱 '+str(r['Id']),'='+rf('DailyTreasurePoint',r,'Point'),'按每日积分','Unknown：箱内配置','积分来源组合未唯一指定',str(r['ItemId']),'需按现行子模块确认启用'])
    overview(b,'常驻_概览','列明解锁/参与门槛、核心奖励与终点。存在配置不等于本期开放，未确认模块不汇入有效总返还。',
      ['系统/阶段','门槛','周期/终点','可计价奖励 $','参与成本','非钱资源','当前结论'],resident,
      [('航行阶段',len(b.raw['VoyageChapter']),'0'),('每日宝箱档',len(b.raw['DailyTreasurePoint']),'0'),('明确关闭类别',len(closed),'0'),('未定价值','Unknown','General')],
      [('航行配置奖励',[1,4],['A10','G27'],'bar',USD),('阶段门槛',[1,2],['G10','M27'],'bar','0')],{4:USD})
    # 9组历史Unknown保留来源，加本轮具体闭合/剩余影响，不复制旧已闭合说法。
    unknown=[
      ['U01','Bet/RTP','已闭合解锁最大档、≤$1=95%；机台五列绑定/特殊RTP优先级未定','代表二倍数制结果不能推广到所有机台','机台数值策划'],
      ['U02','体验分布','完整输赢分布和初始余额未给','只给理论净耗，不报破产概率/百分位','机台数值策划'],
      ['U03','等级/VIP','空type经验、每Spin经验、95%成本、VIP点/$已闭合；r7013单次升级上限1丢溢出已核对','商品VIP点不一致单列；不改源值','商品策划'],
      ['U04','福利','部分任务resetType及在线奖励重置、关闭任务映射需确认','各领取项可计价；不汇成虚假日收入','系统策划'],
      ['U05','商城','部分价格表型SKU投放调用、混合资源分摊未唯一还原','基础可计价部分与非钱资源分账','商业化策划'],
      ['U06','卡册','日Spin/UID是显式敏感性；自然渠道样本季末删失；高阶待普通册完成后另算','逐章季内完成率已模拟；未完成章/整册期望保持Unknown','卡册策划确认玩家情景与额外来源'],
      ['U07','薯片','自然获取末档num=0形成有限道具上限；部分样本完成Pass/Grand所需道具超过上限','列自然上限内完成率；无法自然完成的成本Unknown，潜在奖励不当作已实现','策划Review其他渠道供给'],
      ['U08','777','forceTurn及内圈消格已闭合；源代码自动内圈扣费与User免费取奖口径不同','按User规则模拟；不能当作程序运行验收','策划Review既定成本定义'],
      ['U09','常驻/活动叠加','关闭8类别已排除；其余常驻开放组合/非钱资源成本未唯一确定','跨活动机器净耗只记一次；不相加两个通关成本作同步通关成本','系统策划']]
    b.new('Unknown',[],note='9组历史解释边界逐项更新；不是新冻结Gate。已闭合口径不重新悬置。')
    b.section('Unknown','具体影响与需补充',['编号','模块','当前状态/具体缺口','受影响指标','补充方'],unknown)
    # 首页每行一个模块，不把36静态Spin放首页。
    dash=[
      ['等级','升级成本与成长膨胀','1→5000','=CALC_PRO_LEVEL!N5000','=CALC_PRO_LEVEL!P5000','=D31-E31','=E31/D31','见阶段概览','=D31','二倍机型参考；五列敏感性',jump('等级_阶段概览',1)],
      ['VIP','充值门槛与权益','V1→V15','不适用：充值成本','=SUM(CALC_PRO_VIP!G2:G16)','=CALC_PRO_VIP!D16-E32','=E32/CALC_PRO_VIP!D16','见各VIP档','=CALC_PRO_VIP!D16','返还率分母为充值，非机器净耗',jump('VIP_概览',1)],
      ['BET/RTP','下注强度与净耗','100/500/1000Spin','按档位','不另加机器返还','按档位','不适用','95%/85%','无通关终点','机台列绑定、特殊优先级',jump('BET_RTP_概览',1)],
      ['货币','金币与美元购买力','等级/VIP价档','不适用','不适用','不适用','不适用','见价档膨胀','不适用','钻石因购买档位不同',jump('货币_概览',1)],
      ['福利','按各自周期回补','领取/在线/签到','无统一参与成本','逐项见概览','Unknown','Unknown','各周期分开','无统一终点','互斥领取与重置口径',jump('福利_概览',1)],
      ['商城/薯片Pass','支付价值与投放溢价','当前SKU/15关','不适用：标价','分可计价/非钱','逐SKU','逐SKU','见档位','Pass见薯片','点数/商品换算差异',jump('商城_Pass_概览',1)],
      ['卡册','章节与整册收集','空册/季首','Unknown：季末删失','章/册奖励可核算','Unknown','Unknown','逐章模型','Unknown：未完成样本','日Spin、额外渠道、高阶',jump('卡包_概览',1)],
      ['薯片','自然获取、JP与Pass','首次Grand/Pass终点',"='薯片_概览'!C46","='薯片_概览'!H46",'=IF(ISNUMBER(D38),D38-E38,"Unknown")','=IF(ISNUMBER(D38),E38/D38,"Unknown")','见阶段',"='薯片_概览'!C45",'自然道具封顶；潜在奖励非保证实现',jump('薯片_概览',1)],
      ['777','三轮圈层奖励','外→中→内',"=SUM('777_概览'!D34:D36)","=SUM('777_概览'!H34:H36)",'=D39-E39','=E39/D39','见每轮','见三轮成本','三轮自然获取积分连续；内圈按User口径',jump('777_概览',1)],
      ['常驻','参与门槛与阶段终点','航行/每日宝箱','Unknown','可计价部分见概览','Unknown','Unknown','按模块','Unknown','未确认开放者不入有效总返还',jump('常驻_概览',1)],
    ]
    overview(b,'总览','CR 9.22 / r7013。机器净耗=毛下注×(1−RTP)。成本跨活动共用，模块行不可直接相加。尚未冻结或发布。',
      ['模块','一句话作用','关键阶段','机器净耗 $','可计价返还 $','净成本 $','返还率','阶段膨胀','最终成本 $','关键边界','下钻'],dash,
      [('等级成本RTP','=SRC_DECISIONS!B2',PCT),('VIP点/美元','=SRC_DECISIONS!B3','0'),('活动组合','薯片 + 777','General'),('保留解释边界',9,'0')],
      [('等级总成本与奖励',[1,4,5],['A10','G27'],'bar',USD),('各模块返还率（仅有分母项）',[1,7],['G10','M27'],'bar',PCT)],{4:USD,5:USD,6:USD,7:PCT,9:USD})
    # 所有保留明细标清旧静态场景/当前追溯；首层不再引用旧口径。
    for n,s in b.sheets.items():
        if n.endswith('_明细') and n not in ('等级_明细','Buff_明细'):
            s['rows'][2]=['上部为历史Accepted静态场景或原始配置；本轮制作人指标在模块概览及本页新增计算段。旧Unknown不覆盖9/20闭合口径。']
        if n.endswith('_明细'):
            s['groups']=[[sec['row']+1,sec['end']] for sec in s['sections'] if sec['end']-sec['row']>50]
    # 不让旧首页或已关闭BP混在有效概览；保留详细证据不删除配置行。
    order=['总览']
    for module in ['等级','VIP','BET_RTP','货币','Buff','美金金币档位','福利','商城_Pass','卡包','薯片','777','常驻']:
        order.extend([module+('_阶段概览' if module=='等级' else '_概览'),module+'_明细'])
    order+=['关闭_历史配置','Unknown']
    order += [n for n in b.sheets if n not in order]
    b.sheets={n:b.sheets[n] for n in order}
    checks={'lucky':lc,'snack':sc,'cards':cc,'level_overflow':'r7013 CommCfg161=1 / LevelUtils 80-88','samples':{'lucky':1000,'snack':400,'cards_per_profile':100}}
    return {'profiles':profiles,'simulation_checks':checks,'simulation_rows':{'lucky':lucky,'snack':snack,'cards':cards},'unknown':unknown}


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--reuse-simulation',action='store_true',help='仅用于同r7013、同随机模型的公式/布局修正');a=ap.parse_args()
    assert not any((p/'.git').exists() for p in (a.output.resolve(),*a.output.resolve().parents))
    cached=json.loads((a.output/'simulation-evidence.json').read_text(encoding='utf-8')) if a.reuse_simulation else None
    b=Book(a.baseline,a.output);p=restore(b,a.baseline)
    preserved=[s['name'] for s in p['sheets'] if s['hidden'] and s['name'] not in ('SRC_INDEX','SRC_MANIFEST')]
    extra=build(b,cached)
    p.update({'sheets':list(b.sheets.values()),'source_specs':b.source_specs,'bindings':b.bindings,'checks':b.checks,'revision':7013,'manifest_id':'TASK0036-r7013-dashboard-20260920','dashboard':True})
    p['export_receipt']=b.receipt
    b.sheets['SRC_MANIFEST']['rows']=[['项目','当前值'],['Task','TASK-0036'],['revision',7013],['当前版本','2026-09-20制作人Dashboard'],['源工作簿数',len(b.source_specs)]]+[[n,s['file']] for n,s in b.source_specs.items()]
    p['preserved_sheets']=preserved
    (a.output/'dashboard-plan.json').write_text(json.dumps(p,ensure_ascii=False),encoding='utf-8')
    (a.output/'simulation-evidence.json').write_text(json.dumps(extra,ensure_ascii=False),encoding='utf-8')
    summary={'revision':7013,'source_workbooks':len(b.source_specs),'visible_sheets':[s['name'] for s in b.sheets.values() if not s['hidden']],'level_rows':5000,'old_values_used':False,'simulation':extra['simulation_checks'],'checks':len(b.checks),'unknown_groups':9}
    (a.output/'dashboard-structure.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':main()
