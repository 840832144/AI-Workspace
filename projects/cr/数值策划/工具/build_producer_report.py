"""从TASK-0036新增场景及Accepted底稿生成受控制作人报告；不连接SVN。

python build_producer_report.py --baseline <Accepted目录> --analysis <本轮分析目录>
输出位于analysis目录；明细值只在运行时读取，不嵌入public源码。
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from build_producer_experience import write_csv


def table(headers: list[str], rows: list[list]) -> str:
    def cell(v):
        return str(v).replace('|', ' / ').replace('\n', '；') if v is not None else 'Unknown（源空）'
    return '\n' + '\n'.join(['| ' + ' | '.join(headers) + ' |',
                              '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                             ['| ' + ' | '.join(cell(v) for v in row) + ' |' for row in rows]) + '\n'


def number(value, digits=4):
    return f'{float(value):,.{digits}f}'.rstrip('0').rstrip('.') if digits else f'{float(value):,.0f}'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--baseline', required=True, type=Path)
    ap.add_argument('--analysis', required=True, type=Path)
    args = ap.parse_args()
    out = args.analysis.resolve()
    if any((p / '.git').exists() for p in (out, *out.parents)):
        raise ValueError('完整报告必须写入Git以外的受控目录')
    if (out / '制作人汇报.md').exists():
        raise ValueError('不覆盖既有报告')
    summary = json.loads((out / 'summary.json').read_text(encoding='utf-8'))
    revision = summary['applicability_revision']
    inputs = set(summary['reused_input_files'])

    def read_csv(name, root=out):
        if root == args.baseline:
            inputs.add(name + '.csv')
        with (root / (name + '.csv')).open(encoding='utf-8-sig', newline='') as f:
            return list(csv.DictReader(f))

    def source(name):
        relative = 'normalized/' + name + '.json'
        inputs.add(relative)
        d = json.loads((args.baseline / relative).read_text(encoding='utf-8'))
        assert d['revision'] == 6961
        sheet = d['sheets'][0]
        return [dict(r, source=f'{name}.xlsx/{sheet["name"]}/row={r["_excel_row"]}/{r["_row_id"]}/r6961→r{revision}')
                for r in sheet['records']]

    # 只读与本报告直接相关的表；无需重新提取或遍历全量配置内容。
    extra = {name: source(name) for name in ('DiamondChipExchange', 'CommonDiamondExchange', 'ItemExchange',
             'BPCfg', 'BPPurchase', 'BPRate', 'CommonBPLevelCondition', 'SlotsCasinoBetList', 'LevelCfg',
             'LevelAward', 'VipPrivilege', 'CardAlbumCfg', 'QuestGetLevel', 'QuestInitItem', 'CashRoyalTask')}
    for name in ('DiamondChipExchange', 'CommonDiamondExchange', 'ItemExchange', 'BPCfg', 'BPPurchase',
                 'BPRate', 'CommonBPLevelCondition'):
        write_csv(out / (name + '-现值引用.csv'), extra[name])
    spins = read_csv('Spin体验')
    activities = {(r['scenario'], r['quest_type']): r for r in read_csv('双活动体验')}
    cards = {r['scenario']: r for r in read_csv('Spin掉卡条件')}
    growth = read_csv('初始Spin成长路径')
    vip = read_csv('VIP门槛引用')
    shop = read_csv('商城配置比价')
    pass_rows = read_csv('薯片Pass口径引用')
    special = read_csv('现行_新手及活动关联RTP-引用')
    exchange = [dict(r, raw_coins_per_diamond=r['chip'] / r['diamond']) for r in extra['DiamondChipExchange']
                if r['chip'] is not None and r['diamond'] is not None and r['diamond'] > 0]
    write_csv(out / '钻石兑换配置比价.csv', exchange)
    caps = {}
    for q in (4, 5):
        stages = sorted([r for r in extra['QuestGetLevel'] if r['questType'] == q], key=lambda r: r['Id'])
        assert stages[-1]['num'] == 0
        caps[q] = sum(r['num'] for r in stages)
    coverage = [
        ['Slots Bet/RTP', 'SlotsCasinoBetList、PriceCheatSheet；机台奖励层级目录；特殊RTP原9行', '固定档位毛下注/机器期望返还/净耗；常规与特殊分层', '机器Bet列绑定、特殊优先级、完整中奖分布未定'],
        ['货币价值', 'Item、PriceSetting、PriceCheatSheet、DiamondChipExchange、ItemExchange', '金币/配置美元精确档；钻石逐兑换报价；资源分别记账', '无全局钻石美元汇率；缺档、枚举及实付不补'],
        ['等级/VIP', 'LevelCfg、LevelAward、SlotsCasinoBetList.levelExp、VipCfg、VipPrivilege', '显式Spin门槛链、后续门槛与经验字段、VIP累计差', '空type默认、经验入账/加成和动态换档未定'],
        ['任务福利', 'CashRoyalTask、SignReward、OnlineReward、FreeBonusHourly/Wheel、FrenzyMission', '固定奖励/目标、按次福利条件期望、日常宝箱门槛', '不同领取条件/时间窗口不叠加为1000Spin总量'],
        ['常驻系统', 'SysUnlock、VoyageChapter、DailyTreasurePoint及全目录原有常驻/其他玩法分组', '解锁/目标/消耗/奖励关系；其余组保留现值', '有配置不等于本版启用；建造关闭，源残留不计收入'],
        ['商城礼包/Pass', 'PriceSetting、商品标价全目录、SnackItemPack/PassReward、BPCfg/BPRate/BPPurchase', '明确单位的配置比价；薯片共享进度与追领；其他Pass独立', '参考价/SKU不推定美元；最终兑现和混合奖总价值未定'],
        ['卡包卡册', 'SlotsCasinoDropCards、CardPack声明组成、CardAlbumCfg/CardChapter', '固定档掉落事件期望；季节/章节/声明卡数', '持卡/重复/稀有/控制状态不足，不能算新卡与整册成本'],
        ['9.22薯片+777', 'QuestPickGet/Points/GetLevel/InitItem；0034/0035 Accepted规则', '积分连续跨档的道具分布、首份概率、叠加成本与上限', '完整状态奖励EV留Unknown，不重开已闭合forceTurn']]
    write_csv(out / '范围覆盖与资源关系.csv', [dict(zip(['系统', '证据', '已交付', '边界'], r)) for r in coverage])
    unknowns = [
        ['U01', 'G01/G02', '机器Bet列、解锁可选档及特殊RTP优先级', '常规模型不能代表实际适用RTP；不相加新手/活动比例', '机台/数值策划：提供现行适用关系'],
        ['U02', 'G04', '初始可用余额与完整输赢分布', '不能计算破产概率、分位数、最长无奖或实际能玩多少Spin', '机台数值策划：提供配置分布与分析用初始余额；不要求线上数据'],
        ['U03', 'G15', 'levelUpType空值默认、levelExp逐Spin入账及VIP经验叠加', '只能列门槛和原经验字段，不能预测100/500/1000Spin到达等级/VIP', '成长策划：确认现行经验/空值语义和升级时换档规则'],
        ['U04', 'G17', '福利的领取条件组合、时间单位/次数、轮盘基础奖励', '不能从Spin数量推每日福利，也不能重复叠加互斥方案', '福利/任务策划：补领取和基础奖定义'],
        ['U05', 'G03/G14/G18', '商品参考价单位、奖励类型与精确价格档、兑现乘数', '不能给全部礼包性价比排名或实付金额；不从SKU尾号猜价格', '商城/Pass策划：提供数值定义和明确标价，无需支付技术审计'],
        ['U06', 'G19', '当前持卡、卡组/稀有/重复与实际适用池状态', '只能给掉落事件和声明卡数，不能给新卡/整册完成概率', '卡册数值策划：提供明确的分析状态及现行抽卡定义'],
        ['U07', 'G08/G09/G22', '薯片状态奖励接续与777特殊格/临时内圈的完整价值输入', '业务流程及forceTurn已Closed，但不能从道具数推出整轮金币EV', '活动策划：需要整轮价值时补状态到奖励的完整数值映射'],
        ['U08', 'G16/G20', '常驻/其他玩法本版适用说明', '保留现值不等于关闭；建造已关闭且源残留不得计作可用产出', '对应模块策划：只补业务适用性，不开展线上审计'],
        ['U09', 'G05/G06/G21', 'Accepted中原缓存/外链与机台JSON解释限制', '沿用原限制，不能声称全机RTP或异常已修复', '原配置维护策划：需要受影响结论时定向补证，不重跑全库']]
    write_csv(out / '制作人Unknown.csv', [dict(zip(['编号', '历史关联', '缺什么', '影响', '谁补充'], r)) for r in unknowns])

    parts = ['# CR 9.22 全项目数值体验与制作人汇报\n\n**TASK-0036 · Review候选 · 受控商业数值，不上传public Git**\n',
      f'固定公司trunk **r{revision}**；读取于2026-09-17 15:49:34北京时间。r6961→r{revision}整个trunk变更路径摘要为空，覆盖ExcelConfigExport/Excel、QuestMap、slots及其他可能新增数值路径。全部系统复用r6961 Accepted证据，刷新源数据0；不把旧提取标成新导出。0034正式规则和0035薯片+777零数值变更候选继续有效。',
      '## Executive Summary\n',
      '当前可解释的是固定配置档位下的机器成本、活动获取与资源关系，尚不足以证明“整套经济体验好/坏”或决定调参。报告不设留存、付费或回收目标。',
      '- **成本边界明确。** 常规USD Bet≤1按95%，>1按85%。相同毛下注下机器期望净耗率由5%变为15%；Bet同时变化时，还要乘投注差。特殊新手/活动配置独立保留，不能据此声称实际玩家必定亏损。',
      f'- **双活动反馈不是无限线性回补。** 连续积分规则下，薯片/777当前积分产物总上限分别为{caps[4]}/{caps[5]}个；高投入、长窗口接近上限后，继续Spin不会同比增加该来源道具。这里是“积分来源上限”，不是完整活动抽奖成本或通关次数。',
      '- **低档与活动档要分开读。** 活动等级门槛前不应预算双活动收入；等级增长后可以变化，但静态场景不假装模拟升级过程。',
      '- **付费、卡册和常驻有资料但不能被凑成一个返还率。** 可确认配置标价与声明奖励，无法把未明参考价、所有混合资源、重复卡和福利次数合成实付回报。',
      '- **当前建议的决策仅是阅读与确认。** 先确认这些条件体验是否符合制作人对现值的理解；Unknown按负责角色补数值定义。本报告不授权改配置、冻结或发布。',
      '## 玩家分层体验\n\n以下是分析者选择的静态代表档，并非真实玩家占比、生命周期或推荐Bet。每个档位选择bet2中接近0.1配置美元、最高≤1、最低>1三个参考投注，并与活动获取矩阵精确匹配。bet2的实际机台绑定、可用Bet档未独立确认，结论均带此条件。',
      table(['档位', '等级', 'VIP', '双活动等级条件', '用途'], [[p['profile'], p['level'], p['vip'],
             '满足' if p['activity_level_condition_met'] else '不满足', '固定档比较，不模拟真实升级'] for p in summary['profiles']]),
      '场景中的N次均为按B实际扣金币的普通Spin，不包含FreeSpin或零成本Spin；固定等级/VIP/Bet且有足够余额完成指定Spin；不计算余额耗尽、改变Bet、升级后重新换档。活动从第0阶段、0积分起；道具初始赠送另列，购买和回流不加入Spin产出。活动满足等级条件不等于本次核验了线上开启。',
      '## 100/500/1000 Spin体验\n\n完整36场景见`Spin体验.csv`；72条活动结果见`双活动体验.csv`，每行保留来源表/Sheet/Excel行/行键、版本、单位与条件。以下同时展示所有档位，E为条件数学期望。配置美元不是实际支付。',
      table(['等级/VIP', 'BetIndex', '配置USD/Spin', 'Spin', 'RTP', '机器净耗配置USD', 'E薯片道具', 'E777道具', 'E掉卡事件'],
            [[f'{r["level"]}/{r["vip"]}', r['bet_index'], number(r['config_usd_bet']), r['spins'],
              f'{float(r["regular_rtp"]):.0%}', number(r['expected_machine_net_config_usd']),
              number(activities[r['scenario'], '4']['expected_items']), number(activities[r['scenario'], '5']['expected_items']),
              number(cards[r['scenario']]['conditional_expected_drop_events'])] for r in spins]),
      '同一RTP、相同Bet的100/500/1000 Spin，机器期望净耗分别为5/25/50个Bet单位（95%），或15/75/150个Bet单位（85%）。活动道具并非对应的现金返还，不能从机器净耗直接扣去道具数。卡列是掉落事件数，不是卡片或新卡数。',
      '## 资源产消与全系统覆盖\n\n各项是可追溯的配置关系，不是假造玩家流水。所有八类均有现值资料；下表“边界”不等于本轮新增冻结Gate。',
      table(['系统', '证据', '已交付', '边界'], coverage),
      '金币流：期初金币 + 机器返还 + 已兑现的福利/任务/升级/卡册/活动/购买奖励 − 毛下注 − 其他明确金币消耗。当前只计算机器这一支；未提供期初余额和全部兑现条件的支路保留Unknown。钻石、VIP经验、等级经验、薯片道具、777道具、卡包、卡片、各Pass进度分别记账，不能同列相加。',
      '金币配置美元采用PriceCheatSheet精确(priceType=17,money=100,vipType=1,level,vip)档。不同等级/VIP不用一个固定金币美元汇率；奖励type=9、17和各表类型枚举按自己的表解释。钻石兑换只给配置兑换比，不设全局美元比值。',
      table(['兑换ID', '钻石成本', '原金币奖励', '原金币/钻石', '证据'], [[r['ID'], r['diamond'], r['chip'], number(r['raw_coins_per_diamond']), r['source']] for r in exchange[:5]]),
      '上表不应用未明VIP/促销乘数，完整31行源表及可计算行另附。CommonDiamondExchange与ItemExchange是另外的资源对价，不能把不同道具兑换当同一货币汇率。',
      '任务福利方面：CashRoyalTask按resetType的日常/一次性目标分别解释；赢钱等条件目标没有用Spin数量代替。FrenzyMission目标与空奖励字段保留原样。DailyTreasurePoint里程碑和Voyage章节是目标链，缺行为速率时不能推“多少小时完成”。',
      table(['领取方案', '领取次数条件', '间隔秒', 'E配置USD/次', '证据'], [[r['type'], r['claim_count_condition'], r['interval_seconds'], r['config_usd_expected_per_claim'], r['source']] for r in read_csv('福利领取条件期望')]),
      '这些领取方案不自动同时适用，不按全天无间断领取放大。OnlineReward的原onlineTime与签到天数单列；未明时间单位不擅自转换。FreeBonusWheel只给基础奖倍数，缺基础量不能变成金币。',
      '常驻中建造模块本版关闭，相关源奖励未修改且不计有效收益。比赛/牌桌、Spades、联盟、赛马/龙虎、马戏团、轮盘、通用其他组沿用“本次不调整、保留现值”，不解释为退役；其目录在`复用目录.csv`，当前适用关系保留U08。拳击/挖矿不纳入9.22组合。',
      '## 成长节奏\n\n先展示源表明确为Spin次数的初始链，后续经验口径与之分开。',
      table(['起始等级', '目标等级', '增量Spin', '从1级累计Spin', '证据'], [[r['from_level'],r['to_level'],r['incremental_spins'],r['cumulative_spins_from_level1'],r['source']] for r in growth]),
      f'到LevelCfg等级{summary["growth_stop"]["level"]}时，levelUpType源值为空；注释定义0为默认经验、1为Spin次数，但空值是否应用默认仍未明示。不能将空值悄悄补0。SlotsCasinoBetList已存在levelExp字段，缺的是逐Spin适用/经验加成/升级换档关系，而非没有经验字段。',
      table(['固定档', '下级原门槛', '原type', '等级门槛证据'], [[p['profile'], next(r for r in extra['LevelCfg'] if r['level']==p['level'])['levelUpExp'],
              next(r for r in extra['LevelCfg'] if r['level']==p['level'])['levelUpType'], next(r for r in extra['LevelCfg'] if r['level']==p['level'])['source']] for p in summary['profiles']]),
      'LevelAward包含升级vipExp和rewardType/money，VipPrivilege包含expRate与slotRewardRate等字段；没有在机器RTP、经验和商品中重复追加这些乘数。VIP是累计经验门槛，不是花费美元门槛；下表沿用Accepted差分。',
      table(['VIP', '累计经验', '增量经验', '证据'], [[r['VIP等级'], r['累计经验门槛'], r['增量VIP经验'], r['来源']] for r in vip]),
      '因此本报告不承诺100/500/1000Spin能到某等级/VIP，也不把活动解锁等级转换成预计天数。',
      '## 付费价值与Pass\n\nPriceSetting明确money为美元×100。下表展示三个选定VIP在前三个配置价格上的原奖励比价，仅为配置值；无SKU实际兑现或额外加成承诺，不按显示折扣推荐购买。',
      table(['money键', '配置USD', 'VIP', '原金币', '金币/配置USD', '证据'], [[r['money_id'],r['config_price_usd'],r['vip'],r['configured_coins'],number(r['coins_per_config_price_usd']),r['source']]
             for r in shop if r['money_id'] in list(dict.fromkeys(x['money_id'] for x in shop))[:3]]),
      '全部可计算比价见`商城配置比价.csv`；各礼包原字段见`商城礼包现行标价-引用.csv`。SnackItemPack._money只写参考价、未明示单位，保留原值且不从SKU尾号推美元。混合金币、道具、卡包先分别展示，不把rewardType=17金额当原金币。',
      f'薯片Pass共有{len(pass_rows)}对免费/付费等级。相同levelId沿用共享门槛，购买后追领已达等级；付费源门槛空值保持空。源级门槛序列为：' + '、'.join(r['shared_threshold'] for r in pass_rows) + '。它们是各级进度门槛，不能把最后一项当整条累计成本。',
      '购买时可追领价值公式：Σ已达到levelId且未领的付费轨奖励；未来奖励要另加未来达级条件。进度到Spin及混合奖统一价值未明，暂不输出完整Pass实付返还倍数。',
      '其他Pass沿用各自表：BPCfg购买经验、BPRate累计pointTotal与coinsRate/100、BPPurchase的VIP/Rate/Times选档、CommonBPLevelCondition的LevelExp/LevelDiamond。BPRate注释的跨期累计不清空与其他Pass关卡进度不同，不能套薯片规则。',
      table(['表', '记录数', '首行证据'], [[name, len(extra[name]), extra[name][0]['source']] for name in ('BPCfg','BPRate','BPPurchase','CommonBPLevelCondition')]),
      '## 卡包卡册体验\n\n掉落模型精确匹配SlotsCasinoDropCards的level、betIndex、needVipMinCard..needVipMaxCard。条件期望=N×dropPro/10000；假定各次独立时至少一次概率=1−(1−p)^N。候选卡包ID/权重保留在明细，不把VIP的默认边界外推到未匹配行。',
      table(['9.22配置日历候选', '基础卡数', '进阶卡数', '证据'], [[r['theme'],r['base_cards'],r['prestige_cards'],r['source']] for r in summary['calendar_candidate_albums']]),
      '日历候选只由CardAlbumCfg起止日期判断，不证明线上启用。CardChapter保留全部季节/章节原行；声明卡数与实际可抽卡池、章节数和进阶状态要区分。CardPack声明组成沿用Accepted矩阵，不复用历史快照数值或未确认的向上价格选档。没有初始持卡和重复卡状态，不能计算独特卡数、整册概率及完成金币成本。',
      '## 薯片+777活动叠加\n\n同一次Spin的毛下注只计一次，分别驱动两套获取概率。每个活动内部采用固定独立命中假设；两个活动之间不假设独立，同时拿到首份道具的概率只给Fréchet上下界。',
      table(['活动', '初始itemId', '初始数量', '积分产物上限', '证据'], [['薯片' if r['questType']==4 else '777',r['itemId_3_0'],r['initItemCount_3_0'],caps[r['questType']],r['source']]
            for r in extra['QuestInitItem'] if r['questType'] in (4,5)]),
      '薯片每开一次消耗一个道具、一次一奖；多开连续执行，主奖励池不返薯片，Jackpot可重复，Pass另计。777普通格命中移除，清圈进圈、三圈进轮，永久特殊格进入临时内圈取一次奖励；forceTurn按当前圈付费抽奖计数，未自然命中普通格N则第N次强制，提前命中取消、换圈/轮重置、特殊格排除。以上沿用Accepted，不重做业务Gate。',
      'Spin获取的道具上限不等于能完成多少圈/轮：初始物品、每轮每圈消耗、重复特殊格、返还ID差异和状态奖都需要保留。尤其不能把777积分来源总量重用为旧“每格一次”完整清盘成本。',
      '积分模型：K~Binomial(N,p)，每次命中得g积分；用Accepted连续结算函数S处理K×g，E[道具]=ΣP(K=k)S(k×g)。从0积分起，首份道具概率=Σ在该k下S>0的概率。不能用S(E[积分])代替E[S(积分)]。接近上限时应读期望值和浮点容差，不能把四舍五入后的上限称为保证拿满。',
      '## 风险与Unknown\n\n以下是本报告解释能力的边界，不新增配置冻结前置，也不要求本轮关闭全部历史22项。',
      table(['编号', '历史关联', '缺什么', '影响', '谁补充'], unknowns),
      '## 方法、验证与复核导航\n\n设N为Spin数，B为金币Bet，C为精确档每配置美元金币，r为常规RTP。毛下注W=N×B；机器期望返还=W×r；机器期望净耗=W×(1−r)；对应配置美元均除C。活动金币占毛下注=E[已确定的活动金币]/W；活动金币占机器净耗=E[活动金币]/E[机器净耗]，本轮分子未齐不输出完整比率，绝不混用实付分母。',
      '新模型6项测试覆盖概率分布枚举、0/1边界、1000次质量与均值、离散跨档期望和USD Bet=1边界；另按输出核对36/72场景、源Bet一致、成本只计一次。具体以`验证结果.json`为准。未重跑0033/0034/0035全量Accepted验收，未重算原源表公式。缓存/外链异常仍按原Accepted分类，不当成运行故障。',
      '复核包中baseline/为实际读取的Accepted文件白名单，analysis/为本轮结果，methods/为可复算脚本；source-summary.json不含内部地址。脚本输出须写新目录。CSV保留未四舍五入计算值，报告仅展示四舍五入值。概率数值容差1e-9；期望道具不是个体保证。',
      '本轮仅Git候选交ChatGPT Review；不修改原始表或数值候选、不调参、不提交SVN、不冻结、不发布，不合并或finalize。Subagents: none。']
    (out / '制作人汇报.md').write_text('\n\n'.join(parts) + '\n', encoding='utf-8')
    (out / 'report-inputs.json').write_text(json.dumps(sorted(inputs), ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'report': str(out / '制作人汇报.md'), 'coverage_domains': len(coverage),
                      'unknown_groups': len(unknowns), 'reused_inputs': len(inputs)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
