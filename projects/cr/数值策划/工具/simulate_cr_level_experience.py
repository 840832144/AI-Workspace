"""TASK-0036：只读dev r7237等级，比较CF历史表的成本与成长节奏。

python simulate_cr_level_experience.py --base <受控CR根目录> --output <受控输出目录>
输入复用已回读的r7237配置；新增依赖须先定向svn export -r7237。
不随机编造机台分布，不修改配置；完整计算仅写非Git受控目录。
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import openpyxl

from producer_dashboard_models import max_unlocked
from producer_workbook_sources import read_source


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def play(rows: list[dict], start: int, budget: float) -> dict:
    """沿逐级门槛推进；CF允许原表已有的小数期望Spin，不新增插值源点。"""
    remaining, gross, reward = budget, 0.0, 0.0
    completed = 0
    for r in rows[start-1:]:
        used = min(remaining, r['spins'])
        gross += used * r['net_usd'] / r['spins']
        remaining -= used
        if used + 1e-9 < r['spins']:
            return {'level': r['level'], 'progress': used/r['spins'],
                    'completed': completed, 'spent_spins': budget-remaining,
                    'machine_net_usd': gross, 'reward_usd': reward,
                    'after_reward_usd': gross-reward, 'boundary': False}
        completed += 1
        reward += r['reward_usd']
        if remaining < 1e-9:
            return {'level': r['level']+1, 'progress': 0.0,
                    'completed': completed, 'spent_spins': budget,
                    'machine_net_usd': gross, 'reward_usd': reward,
                    'after_reward_usd': gross-reward, 'boundary': r is rows[-1]}
    return {'level': rows[-1]['level']+1, 'progress': 0.0,
            'completed': completed, 'spent_spins': budget-remaining,
            'machine_net_usd': gross, 'reward_usd': reward,
            'after_reward_usd': gross-reward, 'boundary': True}


def simulate_cr_ticks(rows: list[dict], start: int, budget: int) -> tuple[int, float]:
    """独立逐Spin推进实际配置门槛；单次上限1，溢出不带入下一级。"""
    level, progress = start, 0
    for _ in range(budget):
        if level == 5000:
            break
        r = rows[level-1]
        progress += 1 if r['mode'] == 1 else r['exp_per_spin']
        if progress >= r['threshold']:
            level += 1
            progress = 0
    return level, progress


def report(result: dict) -> str:
    first = result['first300']
    lines = [
        '# CR升级难度曲线核验简报 — dev r7237', '',
        '2026-09-21 · TASK-0036 · 等待ChatGPT Review · Subagents: none。', '',
        '**结论：1–300级目标难度曲线与CF同级一致；配置实现曲线存在整数门槛取整误差，累计约+0.49%，单级最大约+3.17%。**', '',
        'User再次确认：本任务核验升级难度曲线，指标沿用已闭合的每级机器理论净耗USD；不要求Spin数量或固定Spin后的等级一致。此前据Spin差异判断“不符合要求”、建议改成Spin对标，属于Agent误判，已撤回。dev r7237不因Spin差异而被否定。', '',
        '## 曲线核验', '',
        '| 比较项 | 结果 |', '|---|---|',
        '| 1–300级目标 | 300个已有点与CF同级原值对应，未拉伸、压缩或重排 |',
        f'| 1–300级实际配置反算 | 整数门槛落表后的偏差约0至+{first["max_cost_delta"]:.2%}；142级在数值容差内一致 |',
        f'| 前300次升级累计难度 | CR比CF高{first["cost_delta"]:.2%}；分母为同区间CF累计机器理论净耗 |',
        '| 301–4999级 | 按CF末段趋势拟合；缺少同级CF原始点，不宣称逐点已验 |',
        '| 5000级 | 等级终点保持原样，不产生5000→5001 |', '',
        '目标逐级一致与实际配置误差分别保留；没有自行设定误差通过阈值或把本轮标为Accepted。', '',
        '## 累计难度对比', '',
        '按同一目标等级归一，CF=100%。到达N级只累计1→N的N−1次升级；不是固定Spin比较。', '',
        '| 到达等级 | CF累计难度 | CR累计难度 | 相对偏差 |', '|---:|---:|---:|---:|',
    ]
    for row in result['milestones']:
        if row['reach_level'] in (10, 20, 50, 100, 200, 300):
            lines.append(f'| {row["reach_level"]} | 100% | {1+row["cost_delta"]:.3%} | {row["cost_delta"]:+.3%} |')
    lines += [
        '', '## 方法与边界', '',
        '- CR使用dev r7237的LevelCfg远端回读值及提交时已核实未变的Bet/EXP/价值依赖。CF使用旧正式CashRoyal数值.xlsx中cashFrenzy等级的同级G列难度值。',
        '- CR难度=达到配置门槛所需Spin×BetUSD×5%；CF难度=原表Spin×Bet金币×15%÷基础金币美元比÷等级倍率。两者分别沿用既定95%/85%成本模型。Spin是计算过程，不是对标目标；毛下注、奖励后净成本、实付金额不替换当前指标。',
        '- 已有配置模拟、CF来源公式与逐级误差证据继续有效。本轮只改判定口径和报告，未重跑数值模型或改配置；Spin场景和返还明细保留在受控计算中，不作为本次难度曲线验收项。',
        '- 后段采用CF250–300末段“净耗×等级金币倍率”的趋势，锚定300级，再按CR现有等级倍率还原成本；这是拟合，非CF真实5000级数据。本报告不判断在线RTP或真实游戏表现。',
        '', '本轮不新增SVN提交、不调参、不冻结或发布。VIP继续暂存，PR #10保持OPEN，原reservation不finalize。', '',
        '复核方法：`projects/cr/数值策划/工具/simulate_cr_level_experience.py`。完整逐级值与JSON继续留在受控目录`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/outputs/task0036-level-simulation-r7237/`，不进public Git。',
    ]
    return '\n'.join(lines)+'\n'


def run(base: Path, output: Path) -> dict:
    assert not any((p/'.git').exists() for p in (output.resolve(), *output.resolve().parents))
    prior = base/'outputs/task0036-level-dev-20260921'
    receipt = json.loads((prior/'svn-result.json').read_text(encoding='utf-8'))
    assert receipt['committed_revision'] == 7237 and receipt['remote_cell_diff'] == 0
    export = json.loads((output/'source.local.json').read_text(encoding='utf-8'))
    assert export['revision'] == 7237 and export['environment'] == 'CR dev'
    levels = read_source(prior/'LevelCfg.remote-r7237.xlsx')['records']
    bets = {r['levelId']: r for r in read_source(prior/'dev-before/SlotsCasinoBetList.xlsx')['records']}
    unlocks = read_source(prior/'dev-before/SlotsCasinoBetUnlock.xlsx')['records']
    prices = [r for r in read_source(prior/'dev-before/PriceCheatSheet.xlsx')['records']
              if (r['money'], r['priceType'], r['vipType']) == (100, 17, 1)]
    source = output/'source-r7237'
    awards = {r['level']: r for r in read_source(source/'LevelAward.xlsx')['records']}
    cap = next(r for r in read_source(source/'CommCfg.xlsx')['records'] if r['id'] == 161)
    assert cap['val'] == 1
    shops = [r for r in read_source(source/'PayDiamond.xlsx')['records']
             if r['payType'] == 1 and r['itemShow'] == 1 and r['currencyType'] == 2 and (r['diamond'] or 0) > 0]
    shop = min(shops, key=lambda r: r['money_dollar'])
    diamond_usd = shop['money_dollar']/100/shop['diamond']

    def rate(level: int) -> float:
        return max((r for r in prices if r['level'] <= level), key=lambda r: r['level'])['vip_16_0']

    cr = []
    assert [r['level'] for r in levels] == list(range(1, 5001))
    for r in levels[:-1]:
        lv = r['level']
        bet = bets[max_unlocked(unlocks, lv)['betlevel']]
        mode = r['levelUpType'] or 0
        assert mode in (0, 1) and r['levelUpExp'] > 0 and bet['levelExp'] > 0
        spins = int(r['levelUpExp']) if mode == 1 else math.ceil(r['levelUpExp']/bet['levelExp'])
        award = awards[lv+1]
        assert award['rewardType'] == 1 and award['money'] is not None
        reward = award['money']/rate(lv+1) + (award['diamond'] or 0)*diamond_usd
        cr.append({'level': lv, 'mode': mode, 'threshold': r['levelUpExp'],
                   'exp_per_spin': bet['levelExp'], 'bet_usd': bet['bet2']/rate(lv),
                   'spins': spins, 'net_usd': spins*bet['bet2']/rate(lv)*.05,
                   'reward_usd': reward, 'level_cell': f'Sheet1!C{r["_excel_row"]}',
                   'bet_row': bet['_excel_row'], 'award_row': award['_excel_row']})
    w = openpyxl.load_workbook(base/'CashRoyal数值.xlsx', read_only=True, data_only=True)
    sheet = w['cashFrenzy等级']
    loss, base_coin = sheet['X2'].value, sheet['Y2'].value
    cf = []
    for r in sheet.iter_rows(min_row=2, max_row=301, max_col=9, values_only=True):
        lv, bet, spins, _, coin, reward, net, _, inflation = r
        assert math.isclose(net, bet*spins*loss/base_coin/inflation, rel_tol=1e-12)
        assert math.isclose(reward, coin/base_coin/inflation, rel_tol=1e-12, abs_tol=1e-12)
        cf.append({'level': lv, 'spins': spins, 'bet_usd': bet/base_coin/inflation,
                   'net_usd': net, 'reward_usd': reward})
    w.close()
    assert [r['level'] for r in cf] == list(range(1, 301))
    comparisons = []
    for a, b in zip(cr, cf):
        comparisons.append({'level': a['level'], 'CR_spins': a['spins'], 'CF_spins': b['spins'],
                            'spin_ratio': a['spins']/b['spins'], 'CR_net_usd': a['net_usd'],
                            'CF_net_usd': b['net_usd'], 'cost_delta': a['net_usd']/b['net_usd']-1,
                            'CR_reward_usd': a['reward_usd'], 'CF_reward_usd': b['reward_usd'],
                            'CR_return': a['reward_usd']/a['net_usd'],
                            'CF_return': b['reward_usd']/b['net_usd']})
    scenarios = []
    for start in (1, 50, 100, 200, 300, 1000):
        for budget in (100, 500, 1000):
            a = play(cr, start, budget)
            actual_level, actual_exp = simulate_cr_ticks(cr, start, budget)
            assert actual_level == a['level']
            if actual_level < 5000:
                r = cr[actual_level-1]
                expected = a['progress']*r['spins']*(1 if r['mode'] == 1 else r['exp_per_spin'])
                assert math.isclose(actual_exp, expected, abs_tol=1e-5)
            b = play(cf, start, budget) if start <= 300 else None
            scenarios.append({'start': start, 'budget_spins': budget, 'CR': a, 'CF': b})
    milestones = []
    for dest in (10, 20, 50, 100, 200, 300, 301, 500, 1000, 2000, 5000):
        def totals(rows: list[dict]) -> dict:
            rs = rows[:dest-1]
            return {key: sum(r[key] for r in rs) for key in ('spins', 'net_usd', 'reward_usd')}
        a, b = totals(cr), totals(cf) if dest <= 301 else None
        milestones.append({'reach_level': dest, 'CR': a, 'CF': b,
                           'spin_ratio': a['spins']/b['spins'] if b else None,
                           'cost_delta': a['net_usd']/b['net_usd']-1 if b else None})
    c, f = cr[:300], cf
    summary = {'revision': 7237, 'method': 'deterministic expected progression; no random win distribution',
               'CR_loss': .05, 'CF_historical_loss': loss,
               'first300': { 'CR_spins': sum(r['spins'] for r in c), 'CF_spins': sum(r['spins'] for r in f),
                'spin_ratio': sum(r['spins'] for r in c)/sum(r['spins'] for r in f),
                'cost_delta': sum(r['net_usd'] for r in c)/sum(r['net_usd'] for r in f)-1,
                'CR_return': sum(r['reward_usd'] for r in c)/sum(r['net_usd'] for r in c),
                'CF_historical_return': sum(r['reward_usd'] for r in f)/sum(r['net_usd'] for r in f),
                'min_spin_ratio': min(r['spin_ratio'] for r in comparisons),
                'max_spin_ratio': max(r['spin_ratio'] for r in comparisons),
                'max_cost_delta': max(r['cost_delta'] for r in comparisons)},
               'scenarios': scenarios, 'milestones': milestones,
               'validation': {'raw_CF_formula_checks': 600, 'CR_tick_scenarios': len(scenarios),
                              'CR_transitions': len(cr), 'terminal': 5000, 'source_writes': 0}}
    for dest in (10, 100, 301):
        n = sum(r['spins'] for r in cr[:dest-1])
        assert simulate_cr_ticks(cr, 1, n) == (dest, 0)
        assert simulate_cr_ticks(cr, 1, n-1)[0] == dest-1
    write_csv(output/'CR_levels.csv', cr)
    write_csv(output/'CR_CF_first300.csv', comparisons)
    (output/'simulation.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    (output/'等级体验模拟简报.md').write_text(report(summary), encoding='utf-8')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.base, args.output)
    print(json.dumps({'first300': result['first300'], 'validation': result['validation'],
                      'from_level1': result['scenarios'][:3], 'milestones': result['milestones']}, ensure_ascii=False))
