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
        '# CR新等级体验模拟简报 — dev r7237',
        '',
        '2026-09-21 · TASK-0036 · 定向配置模拟，等待ChatGPT Review · Subagents: none。',
        '',
        '**结论：美元机器净消耗接近CF历史模型，但升级节奏不一致，不能称为体验完全对标。**',
        '',
        f'- 前300次升级（1→301）：CR {first["CR_spins"]:,} Spin，CF历史模型 {first["CF_spins"]:,.1f} Spin；CR是CF的 **{first["spin_ratio"]:.2f}倍**。单级为{first["min_spin_ratio"]:.1f}–{first["max_spin_ratio"]:.1f}倍。',
        f'- 同一升级区间机器理论净耗只高 **{first["cost_delta"]:.2%}**；单级最大偏差{first["max_cost_delta"]:.2%}，来自整数Spin。这个结果只证明成本对标。',
        f'- 按各自表的奖励口径，累计奖励价值/机器净耗：CR **{first["CR_return"]:.2%}**，CF历史表 **{first["CF_historical_return"]:.2%}**。CR返还也未完全对齐；CF按原表同一行F/G，不冒充已核实的现行领奖时点。',
        '- 根因是上一轮对标指标为“每级机器理论净耗USD”。CR保留自身Bet，等级成本模型采用95% RTP；CF原表采用85% RTP。因此相同美元净耗不意味着相同Spin。',
        '',
        '## 固定Spin：从1级、进度0开始',
        '',
        '| Spin预算 | CR最终等级（本级进度） | CF历史模型等级（本级进度） |',
        '|---:|---:|---:|',
    ]
    for row in result['scenarios'][:3]:
        a, b = row['CR'], row['CF']
        lines.append(f'| {row["budget_spins"]} | {a["level"]}级（{a["progress"]:.1%}） | {b["level"]}级（{b["progress"]:.1%}） |')
    lines += ['', '## 达到指定等级的累计Spin', '',
              '到达N级只计1→N的N−1次升级；与“前300次升级”分母不同。', '',
              '| 到达等级 | CR Spin | CF历史Spin | CR/CF |', '|---:|---:|---:|---:|']
    for row in result['milestones']:
        if row['reach_level'] not in (10, 20, 50, 100, 300, 1000, 5000):
            continue
        cf_spins = f'{row["CF"]["spins"]:,.1f}' if row['CF'] else 'N/A'
        ratio = f'{row["spin_ratio"]:.2f}倍' if row['CF'] else 'N/A'
        lines.append(f'| {row["reach_level"]} | {row["CR"]["spins"]:,} | {cf_spins} | {ratio} |')
    lines += [
        '', '## 模拟口径与判断边界', '',
        '- CR固定dev r7237的LevelCfg远端回读文件；Bet/解锁/价值依赖复用提交时已确认到r7237未变的版本化导出。本轮只补读同版CommCfg、LevelAward、PayDiamond；单次升级上限=1，溢出丢弃。VIP0、普通最大解锁Bet的bet2列、无Buff/活动/额外经验，假设金币充足且不中断下注。',
        '- CR按配置逐Spin累计计数或经验，过门槛升一级；CF用旧正式CashRoyal数值.xlsx/cashFrenzy等级的A2:I301、X2、Y2原值与公式。CF的C列含小数期望Spin，原样保留；这是历史理论进度，不是CF当前App实测。',
        '- CR预计Spin=Spin型门槛，或CEIL(经验门槛/每Spin经验)；机器净耗=Spin×BetUSD×5%。CF机器净耗=原表Spin×原表Bet金币×15%÷基础金币美元比÷等级倍率。返还率=累计奖励美元价值÷同区间机器净耗；没有把毛下注、净耗或商城实付混用。',
        '- 95%是本Task已确认的等级计算假设，不等于在线所有机台的实际RTP。模型不生成未经证实的中奖分布，不据此断言破产率、连输体验、在线RTP或真实分钟数。两者Spin速度相同时，Spin倍数才等于时间倍数。',
        '- 301级以后只有CR拟合，没有CF对应原始数据；到5000级约204万Spin是模型结果，不能宣称后段与CF体验一致。CF路径到301级停止，缺数据不补。',
        '- 已运行18组CR逐Spin场景（起点1/50/100/200/300/1000，各100/500/1000 Spin），与分段推进结果一致；10/100/301级门槛前后边界通过，CF原表成本/奖励公式600项定向复核通过。仅配置与期望路径模拟通过，未运行游戏客户端。',
        '',
        '本轮结论交Review，不自动调参、不新增SVN提交、不冻结或发布；VIP仍暂存，PR #10不合并、不finalize。',
        '', '## 复核位置', '',
        '- 生成器：`projects/cr/数值策划/工具/simulate_cr_level_experience.py`。',
        '- 受控根：`%LOCALAPPDATA%/AI-Workspace/cr-numerics-20260922/outputs/task0036-level-simulation-r7237/`。',
        '- 完整逐级数值：`CR_levels.csv`、`CR_CF_first300.csv`；18组路径、阶段成本/奖励、来源与校验：`simulation.json`及同目录固定源。完整数值不进public Git。',
        '- 复跑：`python simulate_cr_level_experience.py --base <受控CR根> --output <上述受控输出目录>`，只读源配置。',
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
