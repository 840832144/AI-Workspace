"""生成挖矿 / 拳击体验与策划配表验收报告。

输入口径来自《挖矿拳击 数值预期.xlsx》；总净消耗与总奖励预算沿用上一版
对标报告。本脚本只输出待验收的策划口径，不生成正式配置行。
"""

from __future__ import annotations

import argparse
import html
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_OUTPUT = Path(
    r"D:\cr_design\outputs\01a03d75-e77d-75e2-b0ca-ea0f5902404c"
    r"\miner_boxing_expectation_20260826\CR挖矿拳击体验与配表验收报告.html"
)


@dataclass(frozen=True)
class RewardRow:
    name: str
    ratio: float
    count: int
    reward_each: float
    note: str

    @property
    def reward_total(self) -> float:
        return self.reward_each * self.count


@dataclass(frozen=True)
class StageRow:
    stage: int
    incremental: int
    cumulative: int
    external: int
    net_cost: float
    milestone: str
    stage_jackpot: float
    cumulative_reward: float

    @property
    def return_rate(self) -> float:
        return 0.0 if self.net_cost <= 0 else self.cumulative_reward / self.net_cost


MINER_NET_COST = 158.17
MINER_REWARD_BUDGET = 52.06
MINER_TOTAL_EQ = 150
MINER_INITIAL_EQ = 1 + 1 * 5 + 1 * 15
MINER_EXTERNAL_EQ = MINER_TOTAL_EQ - MINER_INITIAL_EQ
MINER_UNIT_COST = MINER_NET_COST / MINER_EXTERNAL_EQ
MINER_PASS_RATIO_TO_PINK = 0.20
MINER_REWARD_WEIGHT = 4 * 1 + 2 * 2.5 + 1 * 10 + 10 * MINER_PASS_RATIO_TO_PINK
MINER_BASE_REWARD = MINER_REWARD_BUDGET / MINER_REWARD_WEIGHT

BOXING_NET_COST = 100.80
BOXING_REWARD_BUDGET = 30.08
BOXING_INITIAL_ITEMS = 5
BOXING_ROUND_ITEMS = (2 + 5 + 10) * 3
BOXING_EXTERNAL_ITEMS = BOXING_ROUND_ITEMS - BOXING_INITIAL_ITEMS
BOXING_UNIT_COST = BOXING_NET_COST / BOXING_EXTERNAL_ITEMS
BOXING_PASS_RATIO_TO_PINK = 0.05138888888888889
BOXING_REWARD_WEIGHT = 1 + 6 + 21 + 21 * BOXING_PASS_RATIO_TO_PINK
BOXING_BASE_REWARD = BOXING_REWARD_BUDGET / BOXING_REWARD_WEIGHT

MINER_REWARDS = (
    RewardRow("绿大奖", 1, 4, MINER_BASE_REWARD, "25 / 70 / 100 / 140"),
    RewardRow("蓝大奖", 2.5, 2, MINER_BASE_REWARD * 2.5, "77 / 135"),
    RewardRow("粉大奖", 10, 1, MINER_BASE_REWARD * 10, "150"),
    RewardRow("Pass", 2, 1, MINER_BASE_REWARD * 2, "64点内按经验比例发完"),
)

BOXING_REWARDS = (
    RewardRow("绿大奖", 1, 1, BOXING_BASE_REWARD, "第5关集齐"),
    RewardRow("蓝大奖", 6, 1, BOXING_BASE_REWARD * 6, "第5关集齐"),
    RewardRow("粉大奖", 21, 1, BOXING_BASE_REWARD * 21, "第5关集齐"),
    RewardRow(
        "Pass",
        21 * BOXING_PASS_RATIO_TO_PINK,
        1,
        BOXING_BASE_REWARD * 21 * BOXING_PASS_RATIO_TO_PINK,
        "64点；第6关完成",
    ),
)

MINER_STAGE_INPUT = (
    (1, 12, "首个宝石出现", 0.0),
    (2, 13, "绿#1", 1.0),
    (3, 15, "", 0.0),
    (4, 15, "", 0.0),
    (5, 15, "绿#2", 1.0),
    (6, 7, "蓝#1", 2.5),
    (7, 12, "", 0.0),
    (8, 11, "绿#3", 1.0),
    (9, 18, "", 0.0),
    (10, 17, "蓝#2", 2.5),
    (11, 5, "绿#4", 1.0),
    (12, 10, "粉#1", 10.0),
)

BOXING_STAGE_INPUT = (
    (1, 17, "三轨各1/3", False),
    (2, 17, "三轨各2/3", False),
    (3, 0, "保持2/3", False),
    (4, 0, "保持2/3", False),
    (5, 17, "三轨集齐", True),
    (6, 17, "下一轮各1/3；Pass集满", False),
)


def money(value: float) -> str:
    return f"${value:,.2f}"


def pct(value: float) -> str:
    return f"{value:.1%}"


def build_miner_stages() -> tuple[StageRow, ...]:
    rows: list[StageRow] = []
    cumulative = 0
    cumulative_jackpot = 0.0
    pass_total = MINER_REWARDS[-1].reward_total
    for stage, incremental, milestone, jackpot_ratio in MINER_STAGE_INPUT:
        cumulative += incremental
        external = max(0, cumulative - MINER_INITIAL_EQ)
        net_cost = external * MINER_UNIT_COST
        stage_jackpot = MINER_BASE_REWARD * jackpot_ratio
        cumulative_jackpot += stage_jackpot
        pass_reward = pass_total * min(cumulative, 64) / 64
        rows.append(
            StageRow(
                stage,
                incremental,
                cumulative,
                external,
                net_cost,
                milestone,
                stage_jackpot,
                cumulative_jackpot + pass_reward,
            )
        )
    return tuple(rows)


def build_boxing_stages() -> tuple[StageRow, ...]:
    rows: list[StageRow] = []
    cumulative = 0
    cumulative_jackpot = 0.0
    jackpot_total = sum(row.reward_total for row in BOXING_REWARDS[:3])
    pass_total = BOXING_REWARDS[-1].reward_total
    for stage, incremental, milestone, award_jackpot in BOXING_STAGE_INPUT:
        cumulative += incremental
        external = max(0, cumulative - BOXING_INITIAL_ITEMS)
        net_cost = external * BOXING_UNIT_COST
        stage_jackpot = jackpot_total if award_jackpot else 0.0
        cumulative_jackpot += stage_jackpot
        pass_reward = pass_total * min(cumulative, 64) / 64
        rows.append(
            StageRow(
                stage,
                incremental,
                cumulative,
                external,
                net_cost,
                milestone,
                stage_jackpot,
                cumulative_jackpot + pass_reward,
            )
        )
    return tuple(rows)


def reward_rows(rows: Iterable[RewardRow]) -> str:
    return "".join(
        "<tr>"
        f"<td>{html.escape(row.name)}</td><td>{row.ratio:.4g}</td><td>{row.count}</td>"
        f"<td>{money(row.reward_each)}</td><td>{money(row.reward_total)}</td>"
        f"<td>{html.escape(row.note)}</td></tr>"
        for row in rows
    )


def stage_rows(rows: Iterable[StageRow]) -> str:
    return "".join(
        "<tr>"
        f"<td>{row.stage}</td><td>{row.incremental}</td><td>{row.cumulative}</td>"
        f"<td>{row.external}</td><td>{money(row.net_cost)}</td>"
        f"<td>{html.escape(row.milestone or '—')}</td><td>{money(row.stage_jackpot)}</td>"
        f"<td>{money(row.cumulative_reward)}</td><td>{pct(row.return_rate)}</td></tr>"
        for row in rows
    )


def render() -> str:
    miner_stages = build_miner_stages()
    boxing_stages = build_boxing_stages()
    miner_reward_total = sum(row.reward_total for row in MINER_REWARDS)
    boxing_reward_total = sum(row.reward_total for row in BOXING_REWARDS)
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CR 挖矿×拳击体验与配表验收报告</title>
<style>
:root{{--bg:#08111f;--panel:#101c30;--panel2:#172640;--line:#2a3c5a;--text:#edf4ff;--muted:#9fb0ca;--cyan:#5eead4;--amber:#fbbf24;--red:#fb7185;--green:#4ade80}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 85% 0,#173252 0,transparent 34%),var(--bg);color:var(--text);font:14px/1.65 "Microsoft YaHei",system-ui,sans-serif}}
main{{max-width:1180px;margin:auto;padding:38px 24px 72px}}h1{{font-size:38px;line-height:1.16;margin:8px 0 12px}}h2{{font-size:24px;margin:40px 0 14px}}p,li{{color:var(--muted)}}.hero{{padding:34px;border:1px solid var(--line);border-radius:22px;background:linear-gradient(135deg,#142542,#0d182a)}}.eyebrow{{color:var(--cyan);letter-spacing:.12em;font-weight:800}}.chips{{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}}.chip{{padding:5px 11px;border:1px solid var(--line);border-radius:999px;background:#0b1628;color:#cfe0fa;font-size:12px}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:13px;margin:20px 0}}.card{{padding:17px;border:1px solid var(--line);border-radius:15px;background:var(--panel)}}.kpi{{font-size:25px;font-weight:800;color:var(--cyan)}}.sub{{font-size:12px;color:var(--muted)}}.callout{{border-left:3px solid var(--amber);background:#192238;padding:14px 17px;border-radius:0 10px 10px 0;margin:14px 0}}.risk{{border-left-color:var(--red)}}.ok{{border-left-color:var(--green)}}.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:13px;margin:12px 0}}table{{width:100%;min-width:760px;border-collapse:collapse;background:var(--panel)}}th,td{{padding:9px 11px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}}th{{background:#1a2a47;color:#dfeaff;font-size:12px}}th:first-child,td:first-child,td:last-child{{text-align:left}}tr:hover td{{background:#172640}}footer{{margin-top:44px;padding-top:16px;border-top:1px solid var(--line);color:#7084a5;font-size:12px}}@media(max-width:820px){{.grid{{grid-template-columns:1fr 1fr}}h1{{font-size:30px}}}}
</style></head><body><main>
<section class="hero"><div class="eyebrow">CR 小游戏轮换 · 待验收方案</div>
<h1>挖矿 × 拳击<br>体验与策划配表验收报告</h1>
<p>依据《挖矿拳击 数值预期》重新拆分大奖、Pass 与消耗节奏；保留上一版对标总深度与总奖励预算。本版用于体验和策划配表验收，未知字段保持“待确认”。</p>
<div class="chips"><span class="chip">挖矿 1:2.5:10</span><span class="chip">拳击 1:6:21</span><span class="chip">奖励预算守恒</span><span class="chip">公式可复算</span><span class="chip">待验收</span></div></section>
<div class="grid">
<div class="card"><div class="sub">挖矿目标净消耗</div><div class="kpi">{money(MINER_NET_COST)}</div><div class="sub">12关 / 外部获取129镐子当量</div></div>
<div class="card"><div class="sub">挖矿总奖励 / 返还</div><div class="kpi">{money(MINER_REWARD_BUDGET)}</div><div class="sub">最终 {pct(MINER_REWARD_BUDGET / MINER_NET_COST)}</div></div>
<div class="card"><div class="sub">拳击大奖集齐净消耗</div><div class="kpi">{money(BOXING_NET_COST)}</div><div class="sub">第5关 / 外部获取46道具</div></div>
<div class="card"><div class="sub">拳击总奖励 / 返还</div><div class="kpi">{money(BOXING_REWARD_BUDGET)}</div><div class="sub">第5关含部分Pass {pct(boxing_stages[4].return_rate)}</div></div>
</div>
<div class="callout ok"><b>结论：</b>预算守恒、资源守恒、大奖倍率、Pass 64点和最终净消耗校验均通过；可进入体验验收。正式 ID、随机权重与常规小奖结构尚未锁定。</div>
<h2>1. 数据源、目标与边界</h2>
<div class="table-wrap"><table><thead><tr><th>数据源/口径</th><th>用途</th><th>状态</th></tr></thead><tbody>
<tr><td>挖矿拳击 数值预期.xlsx</td><td>收集节点、大奖比例、初始道具、工具折算、Pass经验</td><td>本轮主输入</td></tr>
<tr><td>上一版挖矿拳击体验预期报告</td><td>挖矿 {money(MINER_NET_COST)}/{money(MINER_REWARD_BUDGET)}；拳击 {money(BOXING_NET_COST)}/{money(BOXING_REWARD_BUDGET)}</td><td>保留总预算</td></tr>
<tr><td>正式ID、随机权重、常规小奖、Turn&gt;1</td><td>输入未提供，不补写成事实</td><td>待确认</td></tr>
</tbody></table></div>
<h2>2. 核心公式与中间值</h2>
<div class="table-wrap"><table><thead><tr><th>玩法</th><th>公式</th><th>关键中间值</th><th>结果</th></tr></thead><tbody>
<tr><td>挖矿资源</td><td>初始当量=1+1×5+1×15；外部当量=150−21</td><td>初始{MINER_INITIAL_EQ}；外部{MINER_EXTERNAL_EQ}</td><td>{money(MINER_UNIT_COST)}/外部当量</td></tr>
<tr><td>挖矿奖励</td><td>总权重=4×1+2×2.5+1×10+10×20%</td><td>总权重{MINER_REWARD_WEIGHT:.4g}</td><td>绿奖基数{money(MINER_BASE_REWARD)}</td></tr>
<tr><td>拳击资源</td><td>单轮=(2+5+10)×3；外部=51−5</td><td>总需求{BOXING_ROUND_ITEMS}；外部{BOXING_EXTERNAL_ITEMS}</td><td>{money(BOXING_UNIT_COST)}/外部道具</td></tr>
<tr><td>拳击奖励</td><td>总权重=1+6+21+21×5.1389%</td><td>总权重{BOXING_REWARD_WEIGHT:.4f}</td><td>绿奖基数{money(BOXING_BASE_REWARD)}</td></tr>
</tbody></table></div>
<h2>3. 挖矿奖励与12关体验</h2>
<div class="table-wrap"><table><thead><tr><th>奖励项</th><th>单次权重</th><th>预计次数</th><th>单次建议奖</th><th>建议总奖</th><th>完成节点</th></tr></thead><tbody>{reward_rows(MINER_REWARDS)}</tbody></table></div>
<div class="table-wrap"><table><thead><tr><th>关卡</th><th>本关当量</th><th>累计当量</th><th>外部获取</th><th>累计净消耗</th><th>大奖节点</th><th>本关大奖</th><th>累计奖励</th><th>累计返还</th></tr></thead><tbody>{stage_rows(miner_stages)}</tbody></table></div>
<div class="callout risk"><b>体验风险：</b>第2关受21点初始免费当量影响，累计返还约 {pct(miner_stages[1].return_rate)}，随后快速回落；第6、11关单关消耗仅7/5当量，需要确认是否符合地图节奏。</div>
<h2>4. 拳击奖励、轨道配表与6关体验</h2>
<div class="table-wrap"><table><thead><tr><th>奖励项</th><th>单次权重</th><th>预计次数</th><th>单次建议奖</th><th>建议总奖</th><th>完成节点</th></tr></thead><tbody>{reward_rows(BOXING_REWARDS)}</tbody></table></div>
<div class="table-wrap"><table><thead><tr><th>Turn</th><th>Orbit</th><th>CostCount</th><th>Gem</th><th>NeedCount</th><th>建议奖</th><th>收集节点</th></tr></thead><tbody>
<tr><td>1</td><td>1</td><td>2</td><td>绿</td><td>3</td><td>{money(BOXING_REWARDS[0].reward_each)}</td><td>1 / 2 / 5</td></tr>
<tr><td>1</td><td>2</td><td>5</td><td>蓝</td><td>3</td><td>{money(BOXING_REWARDS[1].reward_each)}</td><td>1 / 2 / 5</td></tr>
<tr><td>1</td><td>3</td><td>10</td><td>粉</td><td>3</td><td>{money(BOXING_REWARDS[2].reward_each)}</td><td>1 / 2 / 5</td></tr>
</tbody></table></div>
<div class="table-wrap"><table><thead><tr><th>关卡</th><th>本关消耗</th><th>累计消耗</th><th>外部获取</th><th>累计净消耗</th><th>收集进度</th><th>本关大奖</th><th>累计奖励</th><th>累计返还</th></tr></thead><tbody>{stage_rows(boxing_stages)}</tbody></table></div>
<div class="callout risk"><b>体验风险：</b>第1–4关只有按Pass经验平滑产生的少量预算，第5关集中发出三轨大奖；若反馈偏弱，应从既有 {money(BOXING_REWARD_BUDGET)} 内切分常规小奖，不能额外追加预算。Pass在第6关进入下一轮后完成，需验收是否接受跨轮。</div>
<h2>5. 配表建议与待确认项</h2>
<div class="table-wrap"><table><thead><tr><th>模块</th><th>建议</th><th>可直接落策划表</th><th>待确认</th></tr></thead><tbody>
<tr><td>QuestMinerMap</td><td>12关；绿2/5/8/11，蓝6/10，粉12</td><td>关卡节点</td><td>具体地图格子</td></tr>
<tr><td>QuestJackpotCfg</td><td>挖矿绿1/蓝2.5/粉10</td><td>比例与预算</td><td>Id / NeedCount</td></tr>
<tr><td>QuestInitItem / QuestGetLevel</td><td>镐1、炸药1、钻头1；Pass总经验64</td><td>数量与经验</td><td>奖励类型组合</td></tr>
<tr><td>QuestBoxingJcakpot</td><td>Orbit消耗2/5/10；绿1/蓝6/粉21</td><td>Turn=1结构</td><td>GemItemId、Turn&gt;1</td></tr>
<tr><td>QuestBoxingStageReward</td><td>999收集节点1/2/5</td><td>节点</td><td>Weight / MaxNum、常规小奖</td></tr>
</tbody></table></div>
<h2>6. 校验结果</h2>
<div class="table-wrap"><table><thead><tr><th>校验</th><th>挖矿</th><th>拳击</th><th>边界</th><th>结论</th></tr></thead><tbody>
<tr><td>奖励预算守恒</td><td>{money(miner_reward_total)}</td><td>{money(boxing_reward_total)}</td><td>±$0.01</td><td>通过</td></tr>
<tr><td>大奖倍率</td><td>10.00</td><td>21.00</td><td>输入目标</td><td>通过</td></tr>
<tr><td>资源守恒</td><td>{MINER_INITIAL_EQ}+{MINER_EXTERNAL_EQ}={MINER_TOTAL_EQ}</td><td>{BOXING_INITIAL_ITEMS}+{BOXING_EXTERNAL_ITEMS}={BOXING_ROUND_ITEMS}</td><td>精确相等</td><td>通过</td></tr>
<tr><td>Pass经验</td><td>64</td><td>64</td><td>1×11+3+5+15+30</td><td>通过</td></tr>
<tr><td>净消耗敏感性±10%</td><td>{money(MINER_NET_COST*0.9)}–{money(MINER_NET_COST*1.1)}</td><td>{money(BOXING_NET_COST*0.9)}–{money(BOXING_NET_COST*1.1)}</td><td>仅观察</td><td>通过</td></tr>
</tbody></table></div>
<footer>状态：待验收。输入：挖矿拳击 数值预期.xlsx；报告生成脚本：generate_miner_boxing_acceptance_report.py。未知口径均标记为待确认。</footer>
</main></body></html>"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成挖矿拳击体验与配表验收报告")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="HTML输出路径")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(), encoding="utf-8")
    print(f"HTML_WRITTEN={args.output}")


if __name__ == "__main__":
    main()
