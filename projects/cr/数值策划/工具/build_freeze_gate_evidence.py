#!/usr/bin/env python3
"""TASK-0034 定向证据：复用 Accepted r6961 提取结果，不重跑全量盘点。

只读取指定关系表/既有目录；输出到新建受控目录，不改输入，不访问外部系统。
输出不是自动冻结判定；条件模型、策划决策与配置载值分开。
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

from recalculate_numerical_inventory import group, stage_spins


def regular_rtp(usd: Fraction) -> Fraction:
    """User 2026-09-17 决策，仅常规层，不覆盖新手/活动条件。"""
    if usd < 0:
        raise ValueError('Bet 不能为负数')
    return Fraction(85 if usd > 1 else 95, 100)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, required=True)
    parser.add_argument('--svn-delta', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source, output = args.inventory.resolve(), args.output.resolve()
    if any((p / '.git').exists() for p in (output, *output.parents)):
        raise ValueError('完整证据不得写入 Git 工作树')
    if output.exists():
        raise ValueError('请使用新的输出目录，保留既有证据')
    delta = json.loads(args.svn_delta.read_text(encoding='utf-8-sig'))
    if delta['baseline_revision'] != 6961 or delta['changed_paths'] or delta['environment'] != 'trunk':
        raise ValueError('本工具只复用已确认无变化的 trunk r6961；有变化须先重新锁版整理')
    data = {}

    def sheet(name):
        if name not in data:
            d = json.loads((source / 'normalized' / (name + '.json')).read_text(encoding='utf-8'))
            if d['revision'] != 6961:
                raise ValueError('拒绝混 revision: ' + name)
            data[name] = d
        sheets = data[name]['sheets']
        primary = [s for s in sheets if s['name'] == 'Sheet1']
        if not primary and len(sheets) != 1:
            raise ValueError('必须显式选择主表: ' + name)
        return primary[0] if primary else sheets[0]

    def rows(name):
        return sheet(name)['records']

    def ref(name, row, fields):
        return f'{name}.xlsx/{sheet(name)["name"]}/行{row["_excel_row"]}/{row["_row_id"]}/{fields}/r6961'

    def selected(name, predicate, fields):
        return [{**{k: r.get(k) for k in fields}, 'source': ref(name, r, ','.join(fields))}
                for r in rows(name) if predicate(r)]

    evidence = {'revision': 6961, 'task_id': 'TASK-0034',
                'svn_comparison': {k: v for k, v in delta.items() if not k.endswith('_url')},
                'decision': '常规USD Bet>1:85%; <=1:95%; 特殊条件不覆盖、不改配置'}
    # Only the changed decision boundary; Accepted full Bet matrix stays untouched.
    with (source / '复算_Bet全条件.csv').open(encoding='utf-8-sig') as f:
        equal = [r for r in csv.DictReader(f) if r['参考美金Bet'] and Fraction(r['参考美金Bet']) == 1]
    for row in equal:
        row.update({'本轮常规决策RTP': str(regular_rtp(Fraction(1))),
                    '本轮规则来源': 'User 2026-09-17；不代表当前配置符合',
                    '单次理论净耗_配置美元': str(Fraction(1) - regular_rtp(Fraction(1)))})
    evidence['G01_G02'] = {
        'exact_one_reference_combinations': len(equal),
        'switch_example': selected('SlotsCasinoResultSwitchStrategy', lambda r: r['_excel_row'] == 5,
                                   ['machineId', 'level', 'vip', 'betIndex', 'spinNum', 'rtp']),
        'switch_comments': {m['key']: m['comment'] for m in sheet('SlotsCasinoResultSwitchStrategy')['fields']},
        'special_conditions': selected('SlotsCasinoNewbieConfig', lambda r: True,
            ['id', 'minUnlockLevel', 'maxUnlockLevel', *[f'activityId_5_{i}' for i in range(5)], 'rtpTier']),
        'limits': '不推定Bet列绑定、区间查档、特殊条件匹配或配置优先级；等于1仅决策层闭合'}
    prices = rows('PriceCheatSheet')
    evidence['G03'] = {'comments': {m['key']: m['comment'] for m in sheet('PriceCheatSheet')['fields'][:4]},
                      'limits': '精确money/level/priceType/vipType及VIP列才可引用；缺档不插值、不擅自向上选档'}
    # A small, traceable stage example per activity, not a new all-condition run.
    gains = rows('QuestPointsCheatSheet')
    picks = rows('QuestPickGet')
    levels = rows('QuestGetLevel')
    stage_examples = []
    for q in (4, 5, 8, 9):
        pick = next(r for r in picks if r['questType'] == q and r['Type'] == 2 and r['BetId'] == 1)
        gain = next(r for r in gains if r['questType'] == q and r['Id'] == pick['Id'] and r['level'] == 0)
        level = next(r for r in levels if r['questType'] == q and r['Id'] == 0)
        p = pick['Probability'] / 1000
        stage_examples.append({'questType': q, 'p': p, 'g': gain['vip_16_0'],
            'T': level['LevelUpPoints'], 'num': level['num'],
            'conditional_E_spins': stage_spins(level['LevelUpPoints'], gain['vip_16_0'], p),
            'formula': 'ceil(T/g)/p；p=Probability/1000；只在g为命中后积分、固定独立概率、升级清零时成立',
            'source': ' | '.join([ref('QuestPickGet', pick, 'Probability,BetId'),
                ref('QuestPointsCheatSheet', gain, 'vip_16_0'), ref('QuestGetLevel', level, 'LevelUpPoints,num')])})
    evidence['G07'] = {'stage_examples': stage_examples,
        'level_comment': next(m['comment'] for m in sheet('QuestGetLevel')['fields'] if m['key'] == 'LevelUpPoints'),
        'difficulty_config_types': sorted({r['Type'] for r in rows('QuestPicksDifficulty')}),
        'init_resources': selected('QuestInitItem', lambda r: r['questType'] in (4, 5, 8, 9),
            ['questType', 'itemId_3_0', 'itemId_3_1', 'itemId_3_2']),
        'limits': '不将Points验证列当发放量；不将Type=1难度套入四活动；未证明末档循环或num目标道具'}
    evidence['G08'] = {
        'luck_stages': selected('SnackAddLuck', lambda r: True,
            ['id', 'usedItemCountMin', 'usedItemCountMax', 'addLuck']),
        'nonexclusive_example': selected('SnackDropItemCfg', lambda r: r['boxNum'] == 2 and r['luck'] == 0,
            ['boxNum', 'luck', 'resetItemProb', 'passItemProb', 'chipItemProb']),
        'jackpot_definitions': selected('QuestJackpotCfg', lambda r: r['Type'] == 4,
            ['Id', 'NeedCount', 'ReduceLuck']),
        'limits': '概率不能相加后归一；增加幸运值为0不证明初值或重置规则；ReduceLuck空不当0'}
    lucky_costs = {r['round']: r for r in rows('StrikeLuckyRound')}
    full_clear = []
    for (round_id, ring), items in group(rows('StrikeLucky'), ('round', 'inout')).items():
        cost = lucky_costs[round_id]
        rewards = Counter()
        for r in items:
            rewards[(r['itemType'], r['itemId'])] += r['itemCount']
        full_clear.append({'round': round_id, 'ring': ring, 'grids': len(items),
            'cost_item': cost[f'costItemId_3_{ring-1}'],
            'gross_cost_full_clear': len(items) * cost[f'costCount_3_{ring-1}'],
            'rewards_separate_units': [{'type': k[0], 'item_id': k[1], 'quantity': v} for k, v in rewards.items()],
            'source': ref('StrikeLuckyRound', cost, f'costCount_3_{ring-1}') + ' | ' +
                      ';'.join(ref('StrikeLucky', r, 'gridId,itemType,itemId,itemCount') for r in items),
            'condition': '仅每格抽中一次且清完本圈；不是实际轮次EV；大奖收集物不作为金币；不抵扣异ID骰子'})
    evidence['G09'] = {'full_clear_conditional': full_clear,
        'initial_resources': selected('QuestInitItem', lambda r: r['questType'] == 5,
                                     ['questType', 'itemId_3_0', 'initItemCount_3_0']),
        'configured_progression_num_sum': sum(r['num'] for r in levels if r['questType'] == 5),
        'progression_source': 'QuestGetLevel.xlsx/Sheet1/questType=5/Id=0..384/num/r6961；总量吻合不证明玩法映射',
        'force_rows': selected('StrikeLucky', lambda r: r['forceTurn'] is not None,
                              ['gridId', 'round', 'inout', 'forceTurn']),
        'resource_definitions': selected('Item', lambda r: r['itemID'] in (215003, 215006),
                                        ['itemID', 'name', 'name_zh', '_comm']),
        'exchange_matches': selected('ItemExchange', lambda r: r['itemId'] in (215003, 215006),
                                    ['id', 'itemId', 'rewardId', 'rewardCount']),
        'limits': '无ItemExchange映射不证明没有兑换；清盘总量不解决落点/强制顺序或提前结束'}
    evidence['G10'] = {
        'blank_caps': selected('QuestBoxingStageReward', lambda r: r['MaxNum'] is None,
            ['Turn', 'orbit', 'Weight', 'MaxNum', 'RewardItemType', 'RewardItemId']),
        'cost_and_gem_links': selected('QuestBoxingJcakpot', lambda r: True,
            ['Turn', 'Orbit', 'CostItemId', 'CostItemCount', 'GemItemId', 'GemItemCount']),
        'gem_definitions': selected('QuestJackpotCfg', lambda r: r['Type'] == 8, ['Id', 'Type', 'Name', 'NeedCount']),
        'limits': 'MaxNum=单组最大随机数量，不证明剩余数量乘权重；空上限与每击抽几次未定'}
    drop = rows('QuestMinerDropItem')
    prob_fields = ['EmptyProb', 'BombProb', 'CashNum', 'ChipProb', 'CardPageProb']
    sums = Counter(sum(r[k] for k in prob_fields) for r in drop)
    evidence['G11'] = {'probability_sum_counts': dict(sums),
        'example': selected('QuestMinerDropItem', lambda r: r['_excel_row'] in (5, 6),
            ['id', 'BoxNum', *prob_fields, 'chipNum', 'CardPageItemId']),
        'limits': '分母仍10000；不足部分不补空奖，不改分母为9500；CashNum是概率不是建造币数量'}
    evidence['G12'] = {
        'maps': selected('QuestMinerMap', lambda r: r['row'] == 1, ['id', 'cliMapNumber', '_descc']),
        'reward_keys': selected('QuestMinerStageReward', lambda r: True, ['id', 'round', '_descc']),
        'drop_fallback_comment': drop[0].get('_descc'),
        'limits': 'cliMapNumber注释仅客户端地图编号，不证明奖励id映射；不按格子数当镐成本；不替用户选择清图路径'}
    evidence['G13'] = {}
    for name in ('SnackPassReward', 'QuestBoxingPass'):
        rs = rows(name)
        by_level = group(rs, ('levelId',))
        evidence['G13'][name] = {'free_levels': sum(r['category'] == 0 for r in rs),
            'paid_levels': sum(r['category'] == 1 for r in rs),
            'paid_empty_thresholds': sum(r['category'] == 1 and r['LevelExp'] is None for r in rs),
            'paired_level_ids': all({r['category'] for r in group_rows} == {0, 1} for group_rows in by_level.values()),
            'example': selected(name, lambda r: r['levelId'] == min(by_level)[0],
                ['id', 'category', 'levelId', 'LevelExp']),
            'limits': '一一对应仅支持共享门槛假说，不证明免费/付费同步解锁或可补领'}
    with (source / '全系统配置目录.csv').open(encoding='utf-8-sig') as f:
        catalog = [r for r in csv.DictReader(f) if r['系统'] == '同trunk其他玩法/归属待确认' and int(r['行数'] or 0)>0]
    evidence['G20'] = {'nonempty_sheets': len(catalog), 'workbooks': len({r['表名'] for r in catalog}),
        'catalog': catalog,
        'activity_scope': selected('Activity', lambda r: r['id'] in (1033, 1034, 1035, 1036),
            ['id', 'type', 'startTime', 'endTime', 'duration', 'interval']),
        'limits': '目录、旧日期或FeatureOnOff不能替代9.22策划适用清单；同trunk其他玩法不当成101输入'}
    # G03: narrow the missing-price decision to actual candidate reward references.
    specs = [('SnackDropItemCfg', None, 'chipNum'), ('QuestJackpotCfg', 'RewardType', 'RewardNum'),
        ('StrikeLucky', 'itemType', 'itemCount'), ('StrikeLuckyRound', 'cherryItemType', 'cherryItemCount'),
        ('StrikeLuckyRound', 'sevenItemType', 'sevenItemCount'),
        ('QuestBoxingStageReward', 'RewardItemType', 'RewardItemCount'),
        ('QuestBoxingJcakpot', 'RewardItemType', 'RewardItemCount')]
    specs += [(n, f'rewardType_2_{i}', f'rewardNum_2_{i}')
              for n in ('SnackPassReward', 'QuestBoxingPass') for i in range(2)]
    specs += [('QuestMinerStageReward', f'RewardItemType_3_{i}', f'RewardItemCount_3_{i}') for i in range(3)]
    price_index = group([r for r in prices if r['priceType'] == 17 and r['vipType'] == 1], ('money', 'level'))
    price_levels = sorted({key[1] for key in price_index})
    checks = []
    for name, kind, quantity in specs:
        for r in rows(name):
            if (kind and r[kind] != 17) or not r[quantity]:
                continue
            if name == 'QuestJackpotCfg' and r['Type'] not in (4, 8, 9):
                continue
            missing = [level for level in price_levels if (r[quantity], level) not in price_index]
            duplicates = [level for level in price_levels if len(price_index.get((r[quantity], level), [])) > 1]
            checks.append({'money': r[quantity], 'missing_levels': missing, 'duplicate_levels': duplicates,
                           'source': ref(name, r, quantity)})
    evidence['G03'].update({'mapping_condition': '按priceType=17/vipType=1检查；没有明确vipType的奖励仍须确认映射',
        'reference_count': len(checks), 'exact_level_tiers': price_levels,
        'exact_unambiguous_reference_count': sum(not c['missing_levels'] and not c['duplicate_levels'] for c in checks),
        'price_gaps': [c for c in checks if c['missing_levels'] or c['duplicate_levels']],
        'limits': '同版候选奖励定向查档；缺档不向上取值、不插值。未证明非精确等级或VIP默认规则'})
    evidence['read_tables'] = sorted(data)
    output.mkdir(parents=True)
    (output/'gate-evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2),encoding='utf-8')
    if equal:
        with (output/'USD-Bet-等于1-决策覆盖.csv').open('w', encoding='utf-8-sig', newline='') as f:
            writer=csv.DictWriter(f, fieldnames=list(equal[0]));writer.writeheader();writer.writerows(equal)
    print(json.dumps({'task':'TASK-0034','revision':6961,'target_tables':len(data),
                      'equal_one_overlay_rows':len(equal),'candidate_activity_examples':len(stage_examples)},ensure_ascii=False))


if __name__ == '__main__':
    main()
