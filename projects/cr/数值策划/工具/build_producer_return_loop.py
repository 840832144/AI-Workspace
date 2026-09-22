"""TASK-0036 Dashboard R1定向修订；只读9/20候选与固定r7013源，输出修改计划。

python build_producer_return_loop.py --baseline <Dashboard受控目录> --output <返还闭环受控目录>
只重跑卡册完成模型和777奖励归属；薯片原随机路径与其余Accepted底稿复用。
"""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
import shutil
from build_producer_workbook import Book, col, cell
from producer_dashboard_models import card_simulation, lucky_simulation
from build_producer_dashboard import USD, PCT, MULT


def revise(plan: dict, evidence: dict) -> tuple[dict, list[str]]:
    b=Book.__new__(Book);b.sheets={s['name']:s for s in plan['sheets']}
    b.raw={}; changed=set()
    for table in plan['source_specs']:
        s=b.sheets['SRC_'+table]
        b.raw[table]=[dict(zip(s['rows'][0],r)) for r in s['rows'][1:]]
    def ref(table: str, record: dict, field: str) -> str:
        s=b.sheets['SRC_'+table]
        i=next(i for i,r in enumerate(s['rows'][1:],2) if r[0]==record['原Excel行'])
        return cell(s['name'],i,s['rows'][0].index(field)+1)
    def touch(name: str) -> dict:
        changed.add(name);return b.sheets[name]
    def append_columns(name: str, headers: list, rows: list, formats: dict) -> None:
        s=touch(name);sec=s['sections'][0] if s['sections'] else {'row':1,'end':len(s['rows']),'columns':len(s['rows'][0])}
        start=sec['columns'];s['rows'][sec['row']-1]+=headers
        assert len(rows)==sec['end']-sec['row']
        for i,r in enumerate(rows,sec['row']):s['rows'][i]+=r
        sec['columns']+=len(headers)
        for offset,fmt in formats.items():s['formats'].append([f'{col(start+offset)}{sec["row"]+1}:{col(start+offset)}{sec["end"]}',fmt])
    def section(name: str, title: str, headers: list, rows: list, formats: dict | None=None) -> int:
        touch(name);return b.section(name,title,headers,rows,formats)
    def replace_first(name: str, headers: list, rows: list, formats: dict) -> None:
        s=touch(name);assert len(s['sections'])==1
        s['rows']=s['rows'][:28];s['sections']=[];s['formats']=[x for x in s['formats'] if int(__import__('re').search(r'\d+',x[0])[0])<30]
        b.section(name,'成本与返还闭环',headers,rows,formats)
        for chart in s['charts']:chart['end']=s['sections'][0]['end']
    def avg(sheet: str, field: str, rows: list[int]) -> str:
        return '('+'+'.join(f"'{sheet}'!{field}{i}" for i in rows)+')/'+str(len(rows))
    # 等级终点行不是一次升级；N/A与真实零分开。
    append_columns('CALC_PRO_LEVEL',['本级返还率','累计返还率','累计净成本USD'],[
        [f'=IF(ISNUMBER(K{i}),L{i}/K{i},"N/A：等级上限")',f'=P{i}/N{i}',f'=N{i}-P{i}'] for i in range(2,5002)],{1:PCT,2:PCT,3:USD})
    s=touch('等级_阶段概览');sec=s['sections'][0]
    rows=[]
    for i in range(31,sec['end']+1):
        end=int(s['rows'][i-1][0].split('–')[1]);rr=min(end+1,5000)
        rows.append([f'=IF(E{i}>0,F{i}/E{i},"N/A：等级上限")',f'=CALC_PRO_LEVEL!T{rr}',f'=CALC_PRO_LEVEL!U{rr}'])
    append_columns(s['name'],['阶段返还率','累计返还率','累计净成本 $'],rows,{1:PCT,2:PCT,3:USD})
    s['charts'][1].update(title='阶段与累计返还率',columns=[1,11,12],format=PCT)
    det=touch('等级_明细');det['sections'][0]['columns']=21;det['rows'][5]+=b.sheets['CALC_PRO_LEVEL']['rows'][0][18:]
    for i in range(5000):det['rows'][6+i]+=[f'=CALC_PRO_LEVEL!{c}{i+2}' for c in 'STU']
    det['formats'] += [['S7:T5006',PCT],['U7:U5006',USD]]
    # VIP支付分母与机器净耗严格分开。
    append_columns('CALC_PRO_VIP',['礼包返还率','累计礼包USD','累计礼包返还率','累计净成本USD'],[
        [f'=G{i}/E{i}',f'=SUM(G$2:G{i})',f'=P{i}/D{i}',f'=D{i}-P{i}'] for i in range(2,17)],{1:PCT,2:USD,3:PCT,4:USD})
    append_columns('VIP_概览',['本级礼包返还率','累计礼包返还率'],[[f'=CALC_PRO_VIP!O{i}',f'=CALC_PRO_VIP!Q{i}'] for i in range(2,17)],{1:PCT,2:PCT})
    section('VIP_概览','累计充值闭环（分母为充值；权益不美元化）',['VIP','累计充值 $','累计礼包 $','累计礼包返还率','累计净成本 $'],[[f'=CALC_PRO_VIP!{c}{i}' for c in 'ADPQR'] for i in range(2,17)],{2:USD,3:USD,4:PCT,5:USD})
    section('VIP_明细','礼包返还闭环',['VIP','本级礼包返还率','累计礼包 $','累计礼包返还率','累计净成本 $'],[[f'=CALC_PRO_VIP!{c}{i}' for c in 'AOPQR'] for i in range(2,17)],{2:PCT,3:USD,4:PCT,5:USD})
    vip=touch('VIP_概览');vip['charts'][1].update(title='本级与累计礼包返还率',columns=[1,12,13],format=PCT)
    section('VIP_概览','有效Buff属于权益，无独立消费分母',b.sheets['Buff_概览']['rows'][29],copy.deepcopy(b.sheets['Buff_概览']['rows'][30:46]),{2:MULT,3:PCT,6:PCT})
    touch('Buff_概览')['rows'][2]=['权益索引：有效福利/Slots任务Buff已并入VIP。无独立消费闭环，返还率N/A；历史/关闭项仍保留索引。']
    touch('BET_RTP_概览')['rows'][29][3]='机器返还率'
    bet=touch('BET_RTP_概览')
    for index,label in ((1,'≤$1机器返还率'),(2,'>$1机器返还率')):
        bet['rows'][5][index*3]=label;bet['kpis'][index][0]=label
    append_columns('BET_RTP_概览',['机器净耗率'],[[f'=1-D{i}'] for i in range(31,b.sheets['BET_RTP_概览']['sections'][0]['end']+1)],{1:PCT})
    append_columns('CALC_PRO_BET',['机器净耗率'],[[f'=1-H{i}'] for i in range(2,len(b.sheets['CALC_PRO_BET']['rows'])+1)],{1:PCT})
    for name in ('货币_概览','美金金币档位_概览'):
        s=touch(name);s['rows'][2]=['价值基准，无消费分母；返还率N/A。金币/$、钻石/$及相邻倍率不属于消费返还。']
        append_columns(name,['返还率','钻石/$（最低价档）'],[['N/A：价值基准','=1/CALC_DIAMOND!E2'] for _ in range(s['sections'][0]['end']-30)],{2:'0.00'})
    w=touch('福利_概览');w['rows'][2]=['免费投放，无统一消费分母，返还率N/A。单项任务成本未闭合时不虚构回补率；美元值表示同额机器净耗回补能力。']
    append_columns(w['name'],['返还率'],[['N/A：免费投放/未给任务成本'] for _ in range(w['sections'][0]['end']-30)],{})
    # 商品购买与Pass玩法两张子表；不能把不同分母压成同一返还率。
    shopcalc=touch('CALC_PRO_SHOP')
    append_columns('CALC_PRO_SHOP',['支付净成本USD'],[[f'=IF(ISNUMBER(E{i}),B{i}-E{i},"成本未闭合")'] for i in range(2,len(shopcalc['rows'])+1)],{1:USD})
    shop=[];passrow=None
    for i,r in enumerate(shopcalc['rows'][1:],2):
        if 'snackpass' in r[0].lower():passrow=i;continue
        shop.append([f'=CALC_PRO_SHOP!{c}{i}' for c in 'ABEFJF']+[f'=CALC_PRO_SHOP!{c}{i}' for c in 'GHI'])
    replace_first('商城_Pass_概览',['商品','支付成本 $','可计价返还 $','支付返还率','支付净成本 $','回报倍数（辅助）','VIP点','点数差额','分账/条件'],shop,{2:USD,3:USD,4:PCT,5:USD,6:MULT})
    touch('商城_Pass_概览')['charts'][1].update(title='商品支付返还率',columns=[1,4],format=PCT)
    assert passrow
    section('商城_Pass_概览','薯片Pass购买：完成后的潜在权益；不是购买即返还',['商品','购买价 $','全完成黄金奖励 $','支付返还率','支付净成本 $','条件'],[[f'=CALC_PRO_SHOP!A{passrow}',f'=CALC_PRO_SHOP!B{passrow}',f'=CALC_PRO_SHOP!E{passrow}',f'=CALC_PRO_SHOP!F{passrow}',f'=CALC_PRO_SHOP!J{passrow}','购买、完成共享门槛后可追领；玩法成本另表']],{2:USD,3:USD,4:PCT,5:USD})
    # 卡册：同版状态模型跑至全部完成，整册直接取同路径最后一章完成时刻。
    cards=evidence['simulation_rows']['cards'];assert evidence['theoretical_until_complete']
    cs=touch('CALC_SIM_ALBUM');cs['rows'][0]=['档','样本','UID权重档','章','理论首次完成Spin','季末Spin上限','季内完成','理论已开包','最终唯一卡']
    cs['rows'][1:]=[[r['profile'],r['sample'],r['uid_class'],r['chapter'],r['spins'],r['horizon'],r['within_season'],r['opened'],r['unique']] for r in cards]
    ca=touch('卡包_概览');ca['rows'][2]=['空册/季首；理论模型继续同版卡池至完成（不换赛季、不外推day配置），与季内完成率分开。低/中/高情景和UID等配为Estimate；章节成本不能相加。']
    ca['rows'][29][3]='理论完成Spin';ca['rows'][29][10]='赛季内完成率'
    for i,r in enumerate(ca['rows'][30:90],31):
        idx=[j+2 for j,x in enumerate(cards) if x['profile']==r[0] and x['chapter']==r[1]]
        r[3]='='+avg('CALC_SIM_ALBUM','E',idx);r[10]='='+avg('CALC_SIM_ALBUM','G',idx)
        r[11]='理论持续同版卡池至完成；整册为同路径终点，非章成本相加'
    ca['charts'][0].update(title='理论完成成本与返还',columns=[2,6,7],format=USD)
    append_columns('卡包_概览',['玩家档/章节'],[[f'=A{i}&"·"&B{i}'] for i in range(31,91)],{})
    for chart in ca['charts']:chart['columns'][0]=13
    touch('卡包_明细')['rows'][2]=['新增理论完成样本与赛季内完成标记分开；无删失均值替代。旧Accepted静态获取效率保留历史位置。']
    sec=b.sheets['卡包_明细']['sections'][-1];b.sheets['卡包_明细']['rows'][sec['row']-1]=cs['rows'][0]
    # 777圈层按实际获得时的付费圈归属，特殊内圈奖励归触发它的当前圈。
    lucky=evidence['simulation_rows']['lucky'];grid={r['gridId']:r for r in b.raw['StrikeLucky']};rounds={r['round']:r for r in b.raw['StrikeLuckyRound']}
    circ=touch('CALC_777_CIRCLE');circ['rows'][0]+= ['本圈净耗USD','本圈基础USD','本圈樱桃USD','本圈7USD','本圈总返还USD','本圈返还率','本圈净成本USD']
    for j,rec in enumerate(lucky):
        rd=rounds[rec['round']]
        for c in (1,2,3):
            i=j*3+c+1;r=circ['rows'][i-1]
            counts=rec['earned_by_paid_ring'][str(c)]
            base='+'.join(f'{n}*{ref("StrikeLucky",grid[int(g)],"itemCount")}/100' for g,n in counts.items() if grid[int(g)]['itemType']==17) or '0'
            extra=[f'={ref("StrikeLuckyRound",rd,k+"ItemCount")}/100' if rec['collection_ring'][k]==c else '=0' for k in ('cherry','seven')]
            r += [f'=G{i}-G{i-1}' if rec['round']>1 or c>1 else f'=G{i}','='+base]+extra+[f'=SUM(I{i}:K{i})',f'=IF(H{i}>0,L{i}/H{i},"N/A：新增净耗为0")',f'=H{i}-L{i}']
    s=touch('777_概览');sec=s['sections'][1];s['rows']=s['rows'][:sec['row']-2];s['sections']=s['sections'][:1]
    crows=[]
    for rd in rounds:
        for c in (1,2,3):
            idx=[j*3+c+1 for j,r in enumerate(lucky) if r['round']==rd];row=len(s['rows'])+3+len(crows)
            crows.append([rd,['外圈','中圈','内圈'][c-1],'='+avg('CALC_777_CIRCLE','D',idx),'='+avg('CALC_777_CIRCLE','E',idx),'='+avg('CALC_777_CIRCLE','H',idx),'='+avg('CALC_777_CIRCLE','I',idx),'='+avg('CALC_777_CIRCLE','J',idx),'='+avg('CALC_777_CIRCLE','K',idx),'='+avg('CALC_777_CIRCLE','L',idx),f'=IF(E{row}>0,I{row}/E{row},"N/A：本圈新增净耗为0")',f'=E{row}-I{row}','='+avg('CALC_777_CIRCLE','G',idx)])
    section('777_概览','圈层闭环（中档；按奖励实际取得的付费圈归属）',['轮','圈','普通付费次数','特殊付费次数','本圈净耗 $','基础返还 $','樱桃返还 $','7返还 $','总返还 $','返还率','净成本 $','累计净耗 $'],crows,{3:'0.0',4:'0.0',5:USD,6:USD,7:USD,8:USD,9:USD,10:PCT,11:USD,12:USD})
    totalrows=[]
    for k,prof in enumerate(evidence['profiles']):
        start=31+k*3;end=start+2;row=len(s['rows'])+3+len(totalrows)
        totalrows.append([prof['name'],'三轮总通关',f'=SUM(C{start}:C{end})',f'=SUM(D{start}:D{end})',f'=SUM(H{start}:H{end})',f'=E{row}/D{row}',f'=D{row}-E{row}',f'=D{row}',f'=G{row}'])
    totalfirst=section('777_概览','三轮总通关（积分连续；最终完成总成本与净成本分开）',['玩家档','终点','总骰子','总机器净耗 $','总返还 $','总返还率','总净成本 $','最终完成成本 $','最终完成净成本 $'],totalrows,{3:'0.0',4:USD,5:USD,6:PCT,7:USD,8:USD,9:USD})
    section('777_明细','逐样本圈层返还（新补列）',circ['rows'][0],[[f'=CALC_777_CIRCLE!{col(c)}{i}' for c in range(1,15)] for i in range(2,len(circ['rows'])+1)],{7:USD,8:USD,9:USD,10:USD,11:USD,12:USD,13:PCT,14:USD})
    # 薯片原400条路径复用。只添加有限自然渠道+具体补包支付的预算闭环。
    snack=evidence['simulation_rows']['snack'];sn=b.sheets['CALC_SIM_SNACK'];lookup={(x['sample'],x['stage']):i+2 for i,x in enumerate(snack)}
    acq=b.sheets['CALC_PRO_ACQUIRE']['rows'];mid=[i for i,r in enumerate(acq[1:],2) if r[0]=='中档' and r[1]==4]
    stages=sorted([r for r in b.raw['QuestGetLevel'] if r['questType']==4],key=lambda r:r['Id']);cum=0;route=[]
    for i,st in zip(mid,stages):cum+=st['num'];route.append((cum,i))
    assert cum==160
    def natural_ref(qty: int) -> str:return 'CALC_PRO_ACQUIRE!M'+str(next(i for n,i in route if n>=qty))
    packs=[r for r in b.raw['SnackItemPack'] if r['type']==1];assert len(packs)==2
    assert all(r['addLuckVip_16_5']==0 for r in packs),'补包改变幸运值时必须重新模拟，不能复用路径'
    prices=[next(x for x in b.raw['PayDiamond'] if x['itemID']==r['itemId_gp']) for r in packs]
    for pack in packs:assert pack['rewardType_2_0']==17 and pack['rewardId_2_1']==215001
    name='CALC_SNACK_RETURN';b.new(name,['样本','目标','所需薯片','缺口薯片','自然净耗USD','自然实际返还USD','自然返还率','补包1次数','补包1支付USD','补包1赠币USD','路径1总返还USD','路径1总成本USD','路径1返还率','路径1净成本USD','补包2次数','补包2支付USD','补包2赠币USD','路径2总返还USD','路径2总成本USD','路径2返还率','路径2净成本USD'],True);touch(name)
    for i,rec in enumerate(snack,2):
        oldi=i;cap=lookup[rec['sample'],'160次开盒'];achieved=oldi if rec['draws']<=160 else cap
        row=[rec['sample'],rec['stage'],f'=CALC_SIM_SNACK!C{oldi}',f'=MAX(0,C{i}-160)','='+natural_ref(min(rec['draws'],160)),f'=CALC_SIM_SNACK!I{achieved}',f'=F{i}/E{i}']
        for k,(pack,price) in enumerate(zip(packs,prices)):
            countcol,paycol,giftcol,retcol,costcol,ratecol,netcol=('H','I','J','K','L','M','N') if k==0 else ('O','P','Q','R','S','T','U')
            row += [f'=ROUNDUP(D{i}/{ref("SnackItemPack",pack,"rewardNum_2_1")},0)',f'={countcol}{i}*{ref("PayDiamond",price,"money_dollar")}/100',f'={countcol}{i}*{ref("SnackItemPack",pack,"rewardNum_2_0")}/100',f'=CALC_SIM_SNACK!I{oldi}+{giftcol}{i}',f'=E{i}+{paycol}{i}',f'={retcol}{i}/{costcol}{i}',f'={costcol}{i}-{retcol}{i}']
        b.append(name,row)
    ss=touch('薯片_概览');ss['rows'][2]=['自然160上限；超出明确自然渠道不可达。自然实际返还与补包完成闭环分账；补包支付按当前SKU整包数，赠币只计一次，剩余道具不提前计奖励。']
    ss['rows'][29]=['目标/截面','预计薯片','纯自然完成成本 $','自然实际返还 $','自然返还率','自然净成本 $','自然内完成率','缺口薯片','最终免费奖励 $','黄金Pass另计 $','自然可达性','预计Spin','说明']
    targets=[r[0] for r in ss['rows'][30:51]]
    for i,label in enumerate(targets,31):
        ids=[j+2 for j,r in enumerate(snack) if r['stage']==label];allreachable=all(snack[j-2]['draws']<=160 for j in ids)
        ss['rows'][i-1]=[label,'='+avg(name,'C',ids),'='+avg(name,'E',ids) if allreachable else '自然渠道不可达','='+avg(name,'F',ids),'='+avg(name,'F',ids)+'/('+avg(name,'E',ids)+')','='+avg(name,'E',ids)+'-'+avg(name,'F',ids),f'={sum(snack[j-2]["draws"]<=160 for j in ids)}/{len(ids)}','='+avg(name,'D',ids),'='+avg('CALC_SIM_SNACK','I',ids),'='+avg('CALC_SIM_SNACK','H',ids),'可达' if allreachable else '自然渠道不可达（部分/全部路径）','='+avg('CALC_SIM_SNACK','K',ids) if allreachable else '自然渠道不可达','自然实际=目标完成或160停止时返还；补包完成见下表']
    ss['formats']=[f for f in ss['formats'] if int(__import__('re').search(r'\d+',f[0])[0])<30]+[[f'{c}31:{c}51',fmt] for c,fmt in [('B','0.0'),('C',USD),('D',USD),('E',PCT),('F',USD),('G',PCT),('H','0.0'),('I',USD),('J',USD),('L','#,##0')]]
    ss['charts'][0].update(title='自然实际成本与返还（至目标或160上限）',columns=[1,4,6],format=USD)
    ss['charts'][1].update(title='自然渠道返还率与目标完成率',columns=[1,5,7],format=PCT)
    supplement=[]
    for label in targets:
        ids=[j+2 for j,r in enumerate(snack) if r['stage']==label]
        for k,pack in enumerate(packs):
            cols=('H','I','J','K','L','N') if k==0 else ('O','P','Q','R','S','U');rr=len(ss['rows'])+3+len(supplement)
            supplement.append([label,pack['itemId_gp'],'='+avg(name,'E',ids),'='+avg(name,cols[1],ids),'='+avg(name,cols[3],ids),'='+avg(name,cols[4],ids),f'=E{rr}/F{rr}',f'=F{rr}-E{rr}','='+avg(name,'D',ids),'='+avg(name,cols[0],ids),'自然机器净耗+支付；奖励含补包赠币，不含黄金Pass'])
    suppfirst=section('薯片_概览','补充渠道完成：两种SKU各自重复购买的情景，不代选购买方案',['目标','补包SKU','自然机器净耗 $','补包支付 $','完成总返还 $','最终完成总成本 $','综合返还率','最终净成本 $','缺口薯片','整包数','分母/条件'],supplement,{3:USD,4:USD,5:USD,6:USD,7:PCT,8:USD,9:'0.0',10:'0.0'})
    section('薯片_明细','补包情景逐样本闭环（两方案不叠加）',b.sheets[name]['rows'][0],[[f'={name}!{col(c)}{i}' for c in range(1,22)] for i in range(2,len(snack)+2)],{5:USD,6:USD,7:PCT,9:USD,10:USD,11:USD,12:USD,13:PCT,14:USD,16:USD,17:USD,18:USD,19:USD,20:PCT,21:USD})
    pass15=targets.index('Pass 15');passsupp=suppfirst+pass15*2+1
    section('商城_Pass_概览','薯片Pass玩法完成（26个SKU补包情景；购买价另计）',['完成目标','自然净耗 $','补包支付 $','黄金Pass支付 $','玩法+赠币+黄金奖励 $','最终总成本 $','综合返还率','最终净成本 $','自然可达性'],[[
        'Pass 15',f"='薯片_概览'!C{passsupp}",f"='薯片_概览'!D{passsupp}",f'=CALC_PRO_SHOP!B{passrow}',f"='薯片_概览'!E{passsupp}+'薯片_概览'!J{31+pass15}",f"='薯片_概览'!F{passsupp}+CALC_PRO_SHOP!B{passrow}",
        f"=('薯片_概览'!E{passsupp}+'薯片_概览'!J{31+pass15})/('薯片_概览'!F{passsupp}+CALC_PRO_SHOP!B{passrow})",f"='薯片_概览'!F{passsupp}+CALC_PRO_SHOP!B{passrow}-'薯片_概览'!E{passsupp}-'薯片_概览'!J{31+pass15}",'自然渠道不可达；补包须在活动结束前10小时之前可购买']],{2:USD,3:USD,4:USD,5:USD,6:USD,7:PCT,8:USD})
    # 常驻只将现有证据串成具体缺口，不用配置残留证明启用。
    resident=touch('常驻_概览');resident['rows'][2]=['待启用确认/成本未闭合：航行需关卡收集道具及船容量，宝箱需积分来源与箱内容。固定r7013 Item原格已匹配13项物品身份，未给出成本/启用；不纳入当前经济结论。']
    resident['rows'][5][9]='当前状态';resident['rows'][6][9]='待启用确认';resident['kpis'][3][:2]=['当前状态','待启用确认']
    for r in resident['rows'][30:resident['sections'][0]['end']]:
        if str(r[0]).startswith('航行'):r[4]='成本未闭合：关卡收集道具/船容量';r[6]='待启用确认；获取成本未闭合'
        else:r[3]='奖励未闭合：需箱内容';r[4]='成本未闭合：积分任务组合';r[6]='待启用确认；积分与箱内容待补'
    append_columns('常驻_概览',['返还率','净成本','最终完成成本'],[['N/A：成本未闭合','成本未闭合','待启用确认/成本未闭合'] for _ in range(resident['sections'][0]['end']-30)],{})
    # Dashboard统一语义；支付类有独立支付列，绝不冒充机器净耗。
    dash=touch('总览');headers=['模块','终点/适用条件','机器理论净耗 $','支付 $','可计价返还 $','返还率','净成本 $','最终完成成本 $','分母/状态','下钻']
    cardmid=70;grand=targets.index('首次Grand');grandsupp=suppfirst+grand*2+1;t777=totalfirst+1
    data=[
      ['等级','1→5000','=CALC_PRO_LEVEL!N5000','N/A','=CALC_PRO_LEVEL!P5000','=E31/C31','=C31-E31','=C31','分母=机器理论净耗；95%专项',"=HYPERLINK(\"#'等级_阶段概览'!A1\",\"概览\")"],
      ['VIP','V1→V15','N/A：充值','=CALC_PRO_VIP!D16','=CALC_PRO_VIP!P16','=E32/D32','=D32-E32','=D32','分母=充值；权益不美元化',"=HYPERLINK(\"#'VIP_概览'!A1\",\"概览\")"],
      ['BET/RTP','1000Spin；中档','=CALC_PRO_ACQUIRE!E'+str(mid[0])+'*1000*(1-CALC_PRO_ACQUIRE!F'+str(mid[0])+')','N/A','已在机器净耗中扣除','=CALC_PRO_ACQUIRE!F'+str(mid[0]),'=C33','=C33','机器返还率分母=毛下注；净耗率5%/15%',"=HYPERLINK(\"#'BET_RTP_概览'!A1\",\"概览\")"],
      ['货币','价值基准','N/A','N/A','N/A','N/A','N/A','N/A','价值基准，非消费闭环',"=HYPERLINK(\"#'货币_概览'!A1\",\"概览\")"],
      ['福利','按各自周期','N/A','N/A','逐项免费投放','N/A','N/A','N/A','免费投放；无统一消费分母',"=HYPERLINK(\"#'福利_概览'!A1\",\"概览\")"],
      ['商城/薯片Pass','逐SKU购买/玩法分表','N/A：购买','逐商品','逐商品','支付返还率见分表','逐商品','Pass玩法见分表','支付与机器净耗不混为同一分母',"=HYPERLINK(\"#'商城_Pass_概览'!A1\",\"概览\")"],
      ['卡册','中档普通整册；理论持续同版',f"='卡包_概览'!F{cardmid}",'N/A',f"='卡包_概览'!G{cardmid}",f"='卡包_概览'!H{cardmid}",f"='卡包_概览'!I{cardmid}",'=C37','理论完成期望；赛季完成率另列',"=HYPERLINK(\"#'卡包_概览'!A1\",\"概览\")"],
      ['薯片','首次Grand；26个SKU补包情景',f"='薯片_概览'!C{grandsupp}",f"='薯片_概览'!D{grandsupp}",f"='薯片_概览'!E{grandsupp}",f"='薯片_概览'!G{grandsupp}",f"='薯片_概览'!H{grandsupp}",f"='薯片_概览'!F{grandsupp}",'自然不可达；综合分母=自然净耗+支付',"=HYPERLINK(\"#'薯片_概览'!A1\",\"概览\")"],
      ['777','中档三轮总通关',f"='777_概览'!D{t777}",'N/A',f"='777_概览'!E{t777}",f"='777_概览'!F{t777}",f"='777_概览'!G{t777}",f"='777_概览'!H{t777}",'分母=机器理论净耗；圈层归属已拆',"=HYPERLINK(\"#'777_概览'!A1\",\"概览\")"],
      ['常驻','航行/每日宝箱','成本未闭合','N/A','需确认','N/A：成本未闭合','成本未闭合','待启用确认','未并入当前经济结论',"=HYPERLINK(\"#'常驻_概览'!A1\",\"缺口\")"]]
    replace_first('总览',headers,data,{3:USD,4:USD,5:USD,6:PCT,7:USD,8:USD})
    dash['charts'][0].update(title='代表终点成本与返还（不可跨模块相加）',columns=[1,8,5],format=USD)
    dash['charts'][1].update(title='各模块返还率（按行标注分母）',columns=[1,6],format=PCT)
    u=touch('Unknown')
    u['rows'][11][2:4]=['理论完成模型已跑至章/册完成；赛季完成率独立；日Spin/UID仍是情景，高阶册另算','理论成本/返还已闭合为Estimate；不代表真实玩家或跨赛季运行']
    u['rows'][12][2:4]=['自然160上限明确不可达；补包两条当前SKU路径另算','含自然净耗与整包支付、赠币一次；须满足活动购买时间窗']
    for s in b.sheets.values():
        if s.get('dashboard'):
            headers=s['rows'][s['sections'][0]['row']-1]
            s['cost_columns']=[i+1 for i,h in enumerate(headers) if any(k in h for k in ('成本','净耗','支付'))]
            s['reward_columns']=[i+1 for i,h in enumerate(headers) if any(k in h for k in ('奖励','返还','礼包','回补')) and i+1 not in s['cost_columns']]
    # 每个消费闭环都有相应明细；只增本轮计算列/表，不新增无关配置。
    plan['sheets']=sorted(b.sheets.values(),key=lambda s:3 if s['hidden'] else 0 if s.get('dashboard') else 1 if s['name'].endswith('_明细') else 2)
    plan['manifest_id']='TASK0036-r7013-return-loop-20260920';plan['return_loop']=True
    plan['closure_locations']={'777_total_first':totalfirst,'snack_supplement_first':suppfirst,'snack_grand_sku2':grandsupp,'snack_pass15_sku2':passsupp,'card_mid_album':cardmid}
    return plan,sorted(changed)


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    assert not any((p/'.git').exists() for p in (a.output.resolve(),*a.output.resolve().parents))
    a.output.mkdir(parents=True,exist_ok=True)
    old=json.loads((a.baseline/'dashboard-plan.json').read_text(encoding='utf-8'));plan=copy.deepcopy(old)
    ep=a.output/'simulation-evidence.json'
    if ep.exists():evidence=json.loads(ep.read_text(encoding='utf-8'));assert evidence['theoretical_until_complete']
    else:
        evidence=json.loads((a.baseline/'simulation-evidence.json').read_text(encoding='utf-8'))
        raw={s['name'][4:]:[dict(zip(s['rows'][0],r)) for r in s['rows'][1:]] for s in plan['sheets'] if s['name'][4:] in plan['source_specs']}
        evidence['simulation_rows']['cards'],evidence['simulation_checks']['cards']=card_simulation(raw,evidence['profiles'],until_complete=True)
        evidence['simulation_rows']['lucky'],evidence['simulation_checks']['lucky']=lucky_simulation(raw)
        evidence['theoretical_until_complete']=True;ep.write_text(json.dumps(evidence,ensure_ascii=False),encoding='utf-8')
    plan,changed=revise(plan,evidence)
    before={s['name']:s for s in old['sheets']};patch=[]
    for s in plan['sheets']:
        if s['name'] not in changed:continue
        previous=before.get(s['name'],{'rows':[]})['rows'];edits=[]
        for i in range(max(len(s['rows']),len(previous))):
            row=s['rows'][i] if i<len(s['rows']) else [];prior=previous[i] if i<len(previous) else []
            for j in range(max(len(row),len(prior))):
                value=row[j] if j<len(row) else None;was=prior[j] if j<len(prior) else None
                if value!=was:edits.append([i+1,j+1,value])
        patch.append({'name':s['name'],'edits':edits,'hidden':s['hidden']})
    (a.output/'return-plan.json').write_text(json.dumps(plan,ensure_ascii=False),encoding='utf-8')
    (a.output/'return-patch.json').write_text(json.dumps({'sheets':[s['name'] for s in plan['sheets']],'changed':patch},ensure_ascii=False),encoding='utf-8')
    for spec in plan['source_specs'].values():
        target=a.output/spec['file'];target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():shutil.copy2(a.baseline/spec['file'],target)
    print(json.dumps({'changed_sheets':changed,'edits':sum(len(s['edits']) for s in patch),'sources':len(plan['source_specs'])},ensure_ascii=False))


if __name__=='__main__':main()
