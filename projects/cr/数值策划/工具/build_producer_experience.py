"""TASK-0036：复用Accepted底稿，新增固定档位100/500/1000 Spin体验。

python build_producer_experience.py --baseline <r6961 Accepted目录> --lock <本轮source-lock.json> --output <新的受控目录>
仅适用定向版本差异为空的复用路径；有变化必须先更新受影响输入，不静默混版。
不连接SVN、不修改源配置、不运行旧全量工具、不计算hash。Python标准库。
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime
from fractions import Fraction
from pathlib import Path

from apply_freeze_gate_decisions import settle

WINDOWS = (100, 500, 1000)
# 分析用静态代表档，不是用户分布、生命周期分组或推荐投注。
PROFILES = (('低等级档', 10, 0), ('活动解锁档', 30, 0),
            ('中段VIP档', 150, 5), ('高段VIP档', 1000, 10))


def binomial(n: int, p: float) -> list[float]:
    """固定、独立命中下K的概率质量；不用于机台输赢分布。"""
    if n < 0 or not 0 <= p <= 1:
        raise ValueError('Invalid binomial input')
    if p in (0, 1):
        return [float(k == (n if p else 0)) for k in range(n + 1)]
    return [math.exp(math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
                     + k * math.log(p) + (n - k) * math.log1p(-p)) for k in range(n + 1)]


def experience(n: int, p: float, gain: int, stages: list[dict]) -> dict:
    if gain <= 0 or not stages or any(s['LevelUpPoints'] <= 0 for s in stages):
        raise ValueError('缺少有效积分或阶段门槛')
    pmf = binomial(n, p)
    outcomes = [settle(k * gain, 0, stages)[2] for k in range(n + 1)]
    return {'expected_items': math.fsum(prob * count for prob, count in zip(pmf, outcomes)),
            'p_any_earned_item': math.fsum(prob for prob, count in zip(pmf, outcomes) if count > 0),
            'expected_points': n * p * gain, 'probability_mass': math.fsum(pmf),
            'expected_hits_check': math.fsum(k * prob for k, prob in enumerate(pmf)),
            'items_at_mean_points_not_expectation': settle(math.floor(n * p * gain), 0, stages)[2]}


def regular_rtp(usd_bet: Fraction) -> Fraction:
    return Fraction(85 if usd_bet > 1 else 95, 100)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text('status\nno_rows\n', encoding='utf-8-sig')
        return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('baseline', 'lock', 'output'):
        parser.add_argument('--' + flag, type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists() or any((p / '.git').exists() for p in (out, *out.parents)):
        raise ValueError('Output must be a new controlled folder outside Git')
    lock = json.loads(args.lock.read_text(encoding='utf-8'))
    if lock['baseline_revision'] != 6961 or lock['changed_paths']:
        raise ValueError('本工具仅支持本轮无变化复用；变更输入需另行定向刷新')
    revision = lock['selected_revision']
    out.mkdir(parents=True)
    read_files: set[str] = set()
    cache: dict[str, dict] = {}

    def source_csv(name: str) -> list[dict]:
        read_files.add(name + '.csv')
        with (args.baseline / (name + '.csv')).open(encoding='utf-8-sig', newline='') as f:
            return list(csv.DictReader(f))

    def source(name: str) -> list[dict]:
        path = 'normalized/' + name + '.json'
        read_files.add(path)
        if name not in cache:
            cache[name] = json.loads((args.baseline / path).read_text(encoding='utf-8'))
            if cache[name]['revision'] != 6961:
                raise ValueError('Mixed evidence revision: ' + name)
        return cache[name]['sheets'][0]['records']

    def ref(name: str, r: dict, fields: str = '') -> str:
        sheet = cache[name]['sheets'][0]['name']
        return f'{name}.xlsx/{sheet}/row={r["_excel_row"]}/{r.get("_row_id", "")}/{fields}/evidence=r6961;applicable=r{revision}'

    catalog = source_csv('全系统配置目录')
    write_csv(out / '复用目录.csv', [dict(r, applicability_revision=revision, action='reuse; no source refresh') for r in catalog])
    baseline_files = source_csv('trunk完整文件目录')
    stages = {q: sorted([r for r in source('QuestGetLevel') if r['questType'] == q], key=lambda r: r['Id']) for q in (4, 5)}
    unlocks = {q: next(r for r in source('SysUnlock') if r['desc'] == text)
               for q, text in ((4, '薯片活动'), (5, 777))}
    assert all(r['unlockType_4_0'] == 0 for r in unlocks.values())
    acquisition = source_csv('复算_四活动获取矩阵')
    acq = {(int(r['questType']), int(r['等级档']), int(r['VIP']), int(r['BetIndex'])): r
           for r in acquisition if int(r['questType']) in (4, 5)}
    bets = source_csv('复算_Bet全条件')
    profiles, spins, activities, overlap, cards = [], [], [], [], []
    card_sources = source('SlotsCasinoDropCards')
    initial = {r['questType']: r for r in source('QuestInitItem') if r['questType'] in (4, 5)}
    for label, level, vip in PROFILES:
        available = [r for r in bets if int(r['等级档']) == level and int(r['VIP']) == vip and r['Bet列'] == 'bet2'
                     and all((q, level, vip, int(r['BetIndex'])) in acq for q in (4, 5))]
        ratio = lambda r: Fraction(r['金币下注']) / Fraction(r['一配置美元金币'])
        choices = [('小额参考', min(available, key=lambda r: abs(ratio(r) - Fraction(1, 10)))),
                   ('不超过1的最高参考档', max((r for r in available if ratio(r) <= 1), key=ratio)),
                   ('超过1的最低参考档', min((r for r in available if ratio(r) > 1), key=ratio))]
        profiles.append({'profile': label, 'level': level, 'vip': vip,
            'activity_level_condition_met': level >= max(r['param_4_0'] for r in unlocks.values()),
            'definition': '固定等级/VIP/Bet，余额足够完成给定Spin；非玩家分布，不随场景内升级改档',
            'eligibility_source': ' | '.join(ref('SysUnlock', r, 'unlockType_4_0,param_4_0') for r in unlocks.values())})
        for bet_case, b in choices:
            bet_id = int(b['BetIndex'])
            unit = Fraction(b['一配置美元金币'])
            bet = Fraction(b['金币下注'])
            usd = bet / unit
            rtp = regular_rtp(usd)
            for n in WINDOWS:
                scenario = f'L{level}-V{vip}-B{bet_id}-N{n}'
                gross = n * bet
                spins.append({'scenario': scenario, 'profile': label, 'level': level, 'vip': vip, 'bet_case': bet_case,
                    'bet_index': bet_id, 'bet_column': 'bet2', 'spins': n, 'coin_bet': float(bet), 'coins_per_config_usd': float(unit),
                    'config_usd_bet': float(usd), 'regular_rtp': float(rtp), 'gross_coin_wager': float(gross),
                    'expected_machine_return_coins': float(gross * rtp), 'expected_machine_net_coin_cost': float(gross * (1 - rtp)),
                    'gross_config_usd': float(gross / unit), 'expected_machine_net_config_usd': float(gross * (1 - rtp) / unit),
                    'net_cost_in_bet_units': float(n * (1 - rtp)), 'real_payment': 'unknown; not inferred',
                    'source': b['来源'], 'applicability_revision': revision,
                    'condition': '常规RTP假设；不认定机器Bet列绑定或特殊RTP优先级；余额可支持全部Spin'})
                probs = []
                for q in (4, 5):
                    a = acq[q, level, vip, bet_id]
                    assert Fraction(a['毛下注金币每Spin']) == bet, '不可将不一致Bet绑定到共享Spin'
                    p = float(Fraction(a['概率千分值']) / 1000)
                    gain = int(a['条件命中积分'])
                    eligible = level >= unlocks[q]['param_4_0']
                    result = experience(n, p if eligible else 0, gain, stages[q])
                    assert abs(result['probability_mass'] - 1) < 1e-9
                    assert abs(result['expected_hits_check'] - n * (p if eligible else 0)) < 1e-7
                    probs.append(result['p_any_earned_item'])
                    activities.append({'scenario': scenario, 'quest_type': q, 'activity': '薯片' if q == 4 else '777',
                        'level_condition_met': eligible, 'spins': n, 'p_hit': p, 'gain_on_hit': gain,
                        'first_threshold_points': stages[q][0]['LevelUpPoints'],
                        'first_threshold_required_hits': math.ceil(Fraction(stages[q][0]['LevelUpPoints'], gain)),
                        'initial_item_id': initial[q]['itemId_3_0'], 'configured_initial_count': initial[q]['initItemCount_3_0'],
                        **result, 'source': a['来源'] + ' | ' + ref('QuestGetLevel', stages[q][0], 'LevelUpPoints,num'),
                        'applicability_revision': revision,
                        'condition': '从活动第0档0积分起；固定独立命中、活动可用；只算Spin产物，初始赠送/购买/回流单列'})
                overlap.append({'scenario': scenario, 'shared_spins': n, 'shared_gross_wager_coins_counted_once': float(gross),
                    'snack_p_any_earned': probs[0], 'lucky_p_any_earned': probs[1],
                    'both_first_resource_probability_lower': max(0.0, sum(probs) - 1),
                    'both_first_resource_probability_upper': min(probs),
                    'correlation': 'unknown; Frechet bounds, no assumed cross-activity independence',
                    'total_activity_coin_ev': 'unknown; do not add different item units'})
                matches = [r for r in card_sources if r['betIndex'] == bet_id and r['level'] == level
                           and r['needVipMinCard'] <= vip <= r['needVipMaxCard']]
                if len(matches) == 1:
                    r = matches[0]
                    p_drop = r['dropPro'] / 10000
                    cards.append({'scenario': scenario, 'exact_matching_rows': 1, 'drop_probability': p_drop,
                        'conditional_expected_drop_events': n * p_drop,
                        'conditional_p_at_least_one_drop': -math.expm1(n * math.log1p(-p_drop)) if p_drop < 1 else 1,
                        'pack_candidates': json.dumps([(r[f'cardId{i}'], r[f'cardWeight{i}']) for i in (1, 2, 3)], ensure_ascii=False),
                        'new_cards_or_album_completion': 'unknown', 'source': ref('SlotsCasinoDropCards', r),
                        'condition': '精确level/Bet/VIP范围命中；假设掉落独立且未叠加未明控制，不解释为新卡数'})
                else:
                    cards.append({'scenario': scenario, 'exact_matching_rows': len(matches),
                        'conditional_expected_drop_events': None, 'new_cards_or_album_completion': 'unknown',
                        'condition': '无唯一精确档，不推断上下档查找或VIP边界默认含义'})
    for filename, records in [('玩家分层', profiles), ('Spin体验', spins), ('双活动体验', activities),
                              ('活动叠加', overlap), ('Spin掉卡条件', cards)]:
        write_csv(out / (filename + '.csv'), records)

    # 非Spin系统：直接引用Accepted静态/复算底稿；只增加制作人视角聚合。
    growth, total = [], 0
    for r in source('LevelCfg'):
        if r['levelUpType'] != 1:
            growth_stop = {'level': r['level'], 'raw_level_up_type': r['levelUpType'],
                           'source': ref('LevelCfg', r), 'reason': '后续经验/空类型口径，缺每Spin经验，不能换算到指定等级的Spin'}
            break
        total += r['levelUpExp']
        growth.append({'from_level': r['level'], 'to_level': r['level'] + 1, 'incremental_spins': r['levelUpExp'],
                       'cumulative_spins_from_level1': total, 'source': ref('LevelCfg', r)})
    write_csv(out / '初始Spin成长路径.csv', growth)
    write_csv(out / 'VIP门槛引用.csv', source_csv('复算_VIP成本'))
    hours = defaultdict(list)
    for r in source_csv('复算_小时福利'):
        hours[(r['类型'], r['领取次数条件'])].append(r)
    hourly = [{'type': key[0], 'claim_count_condition': key[1],
               'config_usd_expected_per_claim': math.fsum(float(r['该档期望配置美元每次领取']) for r in rows),
               'interval_seconds': ','.join(sorted({r['间隔秒'] for r in rows})),
               'source': ' | '.join(r['来源'] for r in rows),
               'note': '既有贡献聚合；未假定每日领取次数或与其他福利叠加'} for key, rows in hours.items()]
    write_csv(out / '福利领取条件期望.csv', hourly)
    static_names = ('CashRoyalTask', 'OnlineReward', 'SignReward', 'FrenzyMission', 'DailyTreasurePoint',
                    'VoyageChapter', 'LevelAward', 'SysUnlock', 'SnackItemPack', 'StrikeLuckyRound',
                    'CardAlbumCfg', 'CardChapter', 'VipPrivilege')
    for name in static_names:
        write_csv(out / (name + '-现值引用.csv'), [dict(r, source=ref(name, r), evidence_revision=6961,
                  applicability_revision=revision) for r in source(name)])
    shop = []
    for r in source('PriceSetting'):
        if r['currencyType'] != 1 or r['vipType'] != 1:
            continue
        for vip in (0, 5, 10):
            price = Fraction(r['money'], 100)
            coins = r[f'vip{vip}']
            shop.append({'money_id': r['money'], 'vip': vip, 'config_price_usd': float(price), 'configured_coins': coins,
                'coins_per_config_price_usd': float(Fraction(coins) / price) if coins is not None and price > 0 else None,
                'source': ref('PriceSetting', r, f'money,currencyType,vipType,vip{vip}'),
                'note': '明示配置金币/配置标价，未假定实际SKU兑现或额外等级/VIP乘数；不是实付或购买建议'})
    write_csv(out / '商城配置比价.csv', shop)
    for name in ('复算_卡包声明组成', '现行_新手及活动关联RTP', '复算_福利轮盘', '商城礼包现行标价'):
        write_csv(out / (name + '-引用.csv'), source_csv(name))
    # 只引用已接受的薯片共享Pass门槛规则，不重做整个Pass盘点。
    pass_rows = source('SnackPassReward')
    pass_pairs = []
    for free in [r for r in pass_rows if r['category'] == 0]:
        paid, = [r for r in pass_rows if r['category'] == 1 and r['levelId'] == free['levelId']]
        pass_pairs.append({'level_id': free['levelId'], 'shared_threshold': free['LevelExp'],
                           'paid_raw_threshold': paid['LevelExp'], 'free_source': ref('SnackPassReward', free),
                           'paid_source': ref('SnackPassReward', paid), 'rule': '同levelId共享门槛；购买后可追领；没有新填源表'})
    write_csv(out / '薯片Pass口径引用.csv', pass_pairs)
    unknown = source_csv('疑问与缺失清单')
    closed = {'G07': '已接受连续积分规则', 'G08': '已接受单次单奖/主池不返薯片/Jackpot重复',
              'G09': '已接受流程与forceTurn；不重开业务Gate', 'G13': '薯片共享门槛与追领规则已接受',
              'G22': '9.22已选薯片+777；整游戏价值/动态EV仍为分析边界'}
    for r in unknown:
        r['本Task处理'] = closed.get(r['编号'], '非本组合' if r['编号'] in ('G10', 'G11', 'G12') else '保留体验解释边界；不新增冻结Gate')
        if r['编号'] in ('G01', 'G02'):
            r['本Task处理'] = 'USD Bet=1已归95%；常规/特殊优先级与机器绑定未确认，不推定实际RTP'
        if r['编号'] == 'G16':
            r['本Task处理'] = 'User确认本版建造关闭；不纳入有效收益预算，不修改源表'
    write_csv(out / 'Unknown与历史闭合映射.csv', unknown)
    active_albums = [r for r in source('CardAlbumCfg') if r['startTime'][:10] <= '2026-09-22' <= r['endTime'][:10]]
    result = {'task_id': 'TASK-0036', 'evidence_revision': 6961, 'applicability_revision': revision,
              'source_read_at_utc': lock['read_at_utc'], 'changed_paths': 0, 'source_refreshes': 0,
              'source_directory_entries_reused': len(baseline_files), 'catalog_sheet_rows_reused': len(catalog),
              'profiles': profiles, 'spin_scenarios': len(spins), 'activity_scenarios': len(activities),
              'card_exact_scenarios': sum(r['exact_matching_rows'] == 1 for r in cards),
              'explicit_initial_spin_growth': growth, 'growth_stop': growth_stop,
              'activity_unlock_levels': {str(q): r['param_4_0'] for q, r in unlocks.items()},
              'calendar_candidate_albums': [{'id': r['id'], 'theme': r['seasonName'], 'base_cards': r['cardNum'],
                 'prestige_cards': r['prestigeCardNum'], 'source': ref('CardAlbumCfg', r)} for r in active_albums],
              'reused_input_files': sorted(read_files), 'new_calculation_scope': '固定档位Spin经济、二项积分到道具分布、掉卡条件、制作人聚合',
              'not_recomputed': 'TASK-0033全量盘点/源公式；TASK-0034/0035已Accepted规则与候选；完整机台/活动周期EV',
              'subagents': 'none'}
    (out / 'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('task_id', 'applicability_revision', 'changed_paths', 'source_refreshes',
                                          'spin_scenarios', 'activity_scenarios', 'card_exact_scenarios')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
