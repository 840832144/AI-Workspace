#!/usr/bin/env python3
"""TASK-0034 R2: 只应用 PR #7 的 User 决定；只读 r6961 与首轮证据。

输出为受控分析层，不改源配置，不重跑 TASK-0033 或首轮完整证据工具。
python apply_freeze_gate_decisions.py --inventory <r6961目录> --prior <首轮final目录> --output <新的受控目录>
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

DECISION = 'https://github.com/840832144/AI-Workspace/pull/7#issuecomment-5708414314'


def settle(points: int, index: int, stages: list[dict]) -> tuple[int, int, int]:
    """单次入账后的连续结算；返回积分余量、当前档、道具发放数。

    末档循环；num=0 的末档仍扣门槛但不发道具。外部活动结束即停止调用。
    """
    reward = 0
    while points >= stages[index]['LevelUpPoints']:
        stage = stages[index]
        threshold = stage['LevelUpPoints']
        if threshold <= 0:
            raise ValueError('门槛必须为正')
        if index == len(stages) - 1:
            count, points = divmod(points, threshold)
            return points, index, reward + count * stage['num']
        points -= threshold
        reward += stage['num']
        index += 1
    return points, index, reward


def cumulative_spins(threshold: int, gain: int, probability: Fraction) -> Fraction:
    """固定命中后积分g及独立命中率p时，累计门槛的首次到达期望。"""
    if threshold < 0 or gain <= 0 or not 0 < probability <= 1:
        raise ValueError('无有效期望分母')
    return Fraction(math.ceil(Fraction(threshold, gain)), 1) / probability


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('inventory', 'prior', 'output'):
        parser.add_argument('--' + flag, type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or any((p / '.git').exists() for p in (output, *output.parents)):
        raise ValueError('输出必须是新的受控目录，不能位于 Git 工作树')
    old = json.loads((args.prior / 'gate-evidence.json').read_text(encoding='utf-8'))
    if old['revision'] != 6961 or old['task_id'] != 'TASK-0034':
        raise ValueError('需要 TASK-0034 首轮 r6961 证据')
    loaded: dict = {}

    def rows(name: str) -> list[dict]:
        if name not in loaded:
            data = json.loads((args.inventory / 'normalized' / (name + '.json')).read_text(encoding='utf-8'))
            if data['revision'] != 6961:
                raise ValueError('拒绝混 revision: ' + name)
            loaded[name] = next(s for s in data['sheets'] if s['name'] == 'Sheet1')
        return loaded[name]['records']

    def ref(name: str, row: dict, fields: str) -> str:
        return f'{name}.xlsx/Sheet1/行{row["_excel_row"]}/{row["_row_id"]}/{fields}/r6961'

    evidence: dict = {'task_id': 'TASK-0034', 'revision': 6961, 'decision': DECISION,
        'layer': 'User规则覆盖的条件分析；不是修改后的配置或线上行为证明',
        'prior': '007202e / gate-evidence.json；本轮不重新访问SVN或正式文档',
        'read_tables': [], 'G07': {}, 'G13': {}}
    stages_csv = []
    for example in old['G07']['stage_examples']:
        q = example['questType']
        stages = sorted((r for r in rows('QuestGetLevel') if r['questType'] == q), key=lambda r: r['Id'])
        p, gain = Fraction(str(example['p'])), example['g']
        if any(r['LevelUpPoints'] <= 0 for r in stages):
            raise ValueError('非正积分门槛')
        # 对末档正奖励只演示第二次循环，避免把无限循环当成活动无限时长。
        sequence = stages + ([stages[-1]] if stages[-1]['num'] > 0 else [])
        threshold = rewards = 0
        previous = Fraction(0)
        for cycle, r in enumerate(sequence):
            threshold += r['LevelUpPoints']
            rewards += r['num']
            cumulative = cumulative_spins(threshold, gain, p)
            stages_csv.append({'questType': q, 'step': cycle + 1, 'Id': r['Id'],
                'threshold': r['LevelUpPoints'], 'num': r['num'], 'p': str(p), 'g': gain,
                'cumulative_points': threshold, 'cumulative_rewards': rewards,
                'expected_cumulative_spins': str(cumulative), 'expected_marginal_spins': str(cumulative - previous),
                'source': ref('QuestGetLevel', r, 'LevelUpPoints,num'), 'gain_source': example['source']})
            previous = cumulative
        evidence['G07'][q] = {'source_stages': len(stages), 'terminal_num': stages[-1]['num'],
            'terminal_rule': '循环末档；num=0后不再产道具；受活动结束约束',
            'formula': 'E累计Spin=ceil(sum(T)/g)/p；边际=相邻累计期望之差；不是sum(ceil(T/g)/p)',
            'assumption': 'Type=2/BetId=1/level=0/VIP=0 示例上下文固定；不把Spin数当毛下注或实付',
            'source_conflict': 'r6961注释升级后清0保留；User后续明确决定覆盖分析规则，不证明源表已改'}

    evidence['G08'] = {'cost_unit': '1次开盒=1个薯片；多开连续执行',
        'reward': '每次只中一种奖励；主池薯片返还=0；Jackpot期内可重复收集/领奖；Pass独立',
        'formula': '主池薯片毛耗=n，净耗=n，薯片返还率=0/n（n>0）；其他奖励按各自单位列示',
        'limits': '没有把源概率列直接相加归一；不输出未定义抽取映射下的完整奖励EV',
        'prior_source': old['G08']['nonexclusive_example']}

    removed = []

    def keep_reward(name: str, r: dict, kind: str, item: str, count: str) -> dict | None:
        result = {'type': r[kind], 'item': r[item], 'quantity': r[count],
                  'source': ref(name, r, f'{kind},{item},{count}')}
        if r[kind] is None:
            return None
        if r[kind] == 3 and r[item] == 192001:
            removed.append(result)
            return None
        return result

    for name in ('SnackPassReward', 'QuestBoxingPass'):
        paired = []
        rs = rows(name)
        total = 0
        for free in sorted((r for r in rs if r['category'] == 0), key=lambda r: r['levelId']):
            paid, = [r for r in rs if r['category'] == 1 and r['levelId'] == free['levelId']]
            total += free['LevelExp']
            rewards = []
            for r in (free, paid):
                for i in range(2):
                    reward = keep_reward(name, r, f'rewardType_2_{i}', f'rewardId_2_{i}', f'rewardNum_2_{i}')
                    if reward is not None:
                        rewards.append({'category': r['category'], **reward})
            paired.append({'levelId': free['levelId'], 'free_threshold': free['LevelExp'],
                'source_paid_threshold': paid['LevelExp'], 'effective_paid_threshold': free['LevelExp'],
                'shared_cumulative_threshold': total, 'rewards': rewards,
                'free_source': ref(name, free, 'LevelExp'), 'paid_source': ref(name, paid, 'LevelExp')})
        evidence['G13'][name] = {'levels': paired,
            'claim_rule': '购买后可追溯领取levelId<=已达等级的付费奖励；免费/付费不重复扣进度'}

    pools: dict = defaultdict(list)
    for r in rows('QuestBoxingStageReward'):
        reward = keep_reward('QuestBoxingStageReward', r, 'RewardItemType', 'RewardItemId', 'RewardItemCount')
        if reward is not None:
            pools[(r['Turn'], r['orbit'])].append({'weight': r['Weight'], 'max_num': r['MaxNum'], **reward})
    boxing = []
    for (turn, orbit), pool in pools.items():
        denominator = sum(r['weight'] for r in pool)
        for r in pool:
            r['initial_category_probability'] = str(Fraction(r['weight'], denominator))
            r['quantity_expectation'] = 'unknown；有MaxNum时1<=E[K]<=MaxNum，不假设均匀；空值不补0'
        boxing.append({'Turn': turn, 'orbit': orbit, 'weight_sum': denominator, 'items': pool})
    evidence['G10'] = {'pools_without_building_currency': boxing,
        'paid_action': '每次消耗抽一组；单轨组抽完继续填充下一组，不以类别数乘单次成本',
        'transition': '抽完类别j后移除j；P(i|剩余集合S)=Weight_i/sum(Weight_S)；MaxNum不乘权重',
        'limits': '组内数量分布未配置时只列边界/符号期望，不自动取均值；不升级为冻结Gate'}

    miner = []
    for r in rows('QuestMinerDropItem'):
        known = r['EmptyProb'] + r['BombProb'] + r['CashNum'] + r['ChipProb'] + r['CardPageProb']
        miner.append({'id': r['id'], 'BoxNum': r['BoxNum'], 'source_empty_mass': r['EmptyProb'],
            'source_unassigned_mass': 10000 - known, 'excluded_building_mass': r['CashNum'],
            'bomb_mass': r['BombProb'], 'coin_mass': r['ChipProb'], 'card_mass': r['CardPageProb'],
            'no_redistribution_empty_mass': 10000 - r['BombProb'] - r['ChipProb'] - r['CardPageProb'],
            'coin_amount': r['chipNum'], 'card_id': r['CardPageItemId'],
            'source': ref('QuestMinerDropItem', r, 'EmptyProb,BombProb,CashNum,ChipProb,chipNum,CardPageProb,CardPageItemId')})
    evidence['G11'] = {'states': miner, 'denominator': 10000,
        'projection': 'User允许空结果；仅作移除建造币且不重分配其概率的条件投影，不宣称User决定了新的空奖配置',
        'EV_per_destroyed_tile': '金币查价面额=ChipProb/10000*chipNum（配置money单位，非实际金币或实付USD）；卡包数=CardPageProb/10000；炸弹单列，触发连锁不额外扣道具',
        'limits': '每次主动点击1道具；连锁毁格各结算；成本=主动点击数，不是毁格数；价值/完整路径EV未填0'}
    map_ids = sorted({r['id'] for r in rows('QuestMinerMap')})
    stage_rewards = []
    for r in rows('QuestMinerStageReward'):
        rewards = [keep_reward('QuestMinerStageReward', r, f'RewardItemType_3_{i}',
                               f'RewardItemIds_3_{i}', f'RewardItemCount_3_{i}') for i in range(3)]
        stage_rewards.append({'id': r['id'], 'round': r['round'], 'rewards': [v for v in rewards if v is not None],
                              'source': ref('QuestMinerStageReward', r, 'id,round')})
    evidence['G12'] = {'rule': 'map.id=reward.id；最大12；12关结束不循环；不按cliMapNumber或取模映射',
        'map_ids': map_ids, 'source_rewards': stage_rewards,
        'source_missing_reward_ids': sorted(set(map_ids) - {r['id'] for r in stage_rewards}),
        'limits': '规则已由User决定；r6961仅id1..3且各有round行，不猜round选档；未补id4..12或计算12关总奖励；不把规则Closed说成现表配置齐备'}

    retained = []
    for gap in old['G03']['price_gaps']:
        name, _, excel, _, quantity, _ = gap['source'].split('/')
        name = name.removesuffix('.xlsx')
        r, = [r for r in rows(name) if r['_excel_row'] == int(excel.removeprefix('行'))]
        kind = quantity.replace('Count', 'Type') if quantity.startswith('RewardItemCount') else quantity.replace('rewardNum', 'rewardType')
        if r[kind] != 17 or r[quantity] != gap['money']:
            raise ValueError('缺档引用与首轮证据不一致')
        retained.append({**gap, 'source_reward_type': r[kind], 'survives_building_removal': True})
    evidence['G03'] = {'retained_references': retained,
        'condition': '仅拳击/挖矿剩余奖励仍需价值比较时阻塞；不重查PriceCheatSheet、不插值、不补0'}
    evidence['G09'] = {'rule': '普通格命中移除，清完普通格进下圈，三圈后下轮；永久特殊格不移除，临时进入内圈随机1奖；特殊格不得force命中',
        'force_rows': old['G09']['force_rows'], 'force_definition': '仅选777时确认计数对象、重置时点和触发方式',
        'resource': 'User确认骰子就是抽奖道具；源ID保留作provenance，不把ID差异继续列业务问题',
        'cost_formula': '成本=各实际扣费抽取次数×所在轮圈单次道具成本；不把临时内圈奖励自动计作另一次付费抽取',
        'limits': '普通/特殊集合按User语义建模，源表未显式标识的不猜gridId；旧每格一次清盘账本退出当前周期成本/EV'}
    evidence['excluded_building_rewards'] = removed
    evidence['read_tables'] = sorted(loaded)
    output.mkdir(parents=True)
    (output / 'decision-models.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    with (output / 'G07-连续积分阶段成本.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(stages_csv[0]))
        writer.writeheader()
        writer.writerows(stages_csv)
    print(json.dumps({'read_tables': len(loaded), 'stage_rows': len(stages_csv),
        'retained_price_gaps': len(retained), 'removed_building_reward_slots': len(removed),
        'pass_pairs': sum(len(v['levels']) for v in evidence['G13'].values())}, ensure_ascii=False))


if __name__ == '__main__':
    main()
