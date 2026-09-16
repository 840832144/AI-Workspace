r"""薯片+777 净消耗模拟（2026-08-19 v5.1，未提交）。

口径：
- 门槛 bet = $1（85%）；薯片 Mini 前按 95%
- 薯片：Jackpot 1.1/3.1/11/30；Pass 1.5/10；一轮（Grand）净消耗≈$158.2，一轮后按终点封顶不再产奖
- 777：骰子7000积分/枚，三轮共384骰子、净消耗≈$100.8；每轮奖励≈12/10/8，第3轮后通关不再产奖
- 里程碑表合并为序号1-4：1=薯片Mini/777第1轮、2=Minor/第2轮、3=Major/第3轮、4=Grand/777已通关
- 合计曲线画到净消耗$200：薯片$158.2后、777$100.8后奖励封顶，曲线为水平线
"""

from __future__ import annotations

import json
from pathlib import Path

OUTPUT_DIR = Path(r"D:\cr_design\outputs\019ffe04-ee02-7f92-a661-34673faabe3f\snack_777_v5_20260819")
HTML_PATH = OUTPUT_DIR / "CR薯片与777净消耗体验报告.html"

BOXES_PER_SNACK = 1.1144
CASH_EV_PER_BOX = 0.03
NET_RATE_MINI = 0.05
NET_RATE_AFTER = 0.15
PASS_PURCHASE = 4.99
K_LOW = 2000.0
K_HIGH = 4000.0
ENDPOINT_SNACK = 1347

JACKPOT_REWARDS = [1.10, 3.10, 11.00, 30.00]
JACKPOT_BOXES = [13.524, 35.556, 72.5, 178.571]
CYCLE_BOXES = sum(JACKPOT_BOXES)
MILESTONE_SNACK = [boxes / BOXES_PER_SNACK for boxes in JACKPOT_BOXES]

FREE_PASS_TIERS: list[tuple[int, float]] = [
    (1, 0.06), (2, 0.07), (4, 0.07), (6, 0.08), (8, 0.08), (10, 0.09), (12, 0.09),
    (14, 0.10), (16, 0.10), (18, 0.11), (20, 0.11),
    (25, 0.12), (30, 0.12), (35, 0.13), (40, 0.17),
]
GOLD_PASS_TIERS: list[tuple[int, float]] = [
    (1, 0.30), (2, 0.30), (4, 0.30), (6, 0.30), (8, 0.30), (10, 0.30), (12, 0.30),
    (14, 0.70), (16, 0.70), (18, 0.70), (20, 0.70),
    (25, 1.20), (30, 1.20), (35, 1.20), (40, 1.50),
]
PASS_TICKETS_PER_BOX = 0.5

DICE_POINTS = 7000.0
DICE_NET = DICE_POINTS / K_HIGH * NET_RATE_AFTER
DICE_PER_ROUND = [80, 124, 180]
ROUND_REWARDS = [12.04, 10.01, 8.03]
# 每格只中一次：现金随圈兑现，樱桃/777 收集满3个轮末兑现（dev v5）
CIRCLE_CASH = [[2.09, 3.38, 1.88], [1.43, 2.34, 1.30], [0.99, 1.64, 0.90]]
COLLECT_REWARD = [4.69, 4.94, 4.50]
ROUND_STEP_DICE = [[20, 36, 24], [40, 48, 36], [60, 72, 48]]

SPEND_NODES_NET = [0, 1, 2.29, 5, 11.19, 20, 21, 40.38, 53.55, 60, 100, 100.8, 158.17, 200]
START_NET_OPTIONS = [5, 10, 20, 50, 100, 200]
BET_OPTIONS = [0.01, 0.1, 1.0]


def level_points(id_: int) -> int:
    if id_ < 12:
        return 7500
    if id_ < 32:
        return 12000
    if id_ < 65:
        return 23500
    if id_ < 160:
        return 33000
    t = (id_ - 160) / (1347 - 160)
    return 33000 + round(t * (40000 - 33000))


def build_s_array() -> list[int]:
    arr = [0] * (ENDPOINT_SNACK + 1)
    acc = 0
    for i in range(1, ENDPOINT_SNACK + 1):
        acc += level_points(i - 1)
        arr[i] = acc
    return arr


S_ARR = build_s_array()


def S(n: int) -> int:
    return S_ARR[min(max(n, 0), ENDPOINT_SNACK)]


def s_frac(n: float) -> float:
    if n <= 0:
        return 0.0
    if n >= ENDPOINT_SNACK:
        return float(S(ENDPOINT_SNACK))
    lo = int(n)
    return S(lo) + (n - lo) * (S(lo + 1) - S(lo))


def inv_s(points: float) -> float:
    if points <= 0:
        return 0.0
    if points >= S(ENDPOINT_SNACK):
        return float(ENDPOINT_SNACK)
    lo, hi = 0, ENDPOINT_SNACK
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if S(mid) <= points:
            lo = mid
        else:
            hi = mid
    span = S(hi) - S(lo)
    return lo + (points - S(lo)) / span if span > 0 else float(lo)


def snack_milestone_net(n: float) -> float:
    p = s_frac(n)
    p0 = s_frac(MILESTONE_SNACK[0])
    if p <= p0:
        return p / K_LOW * NET_RATE_MINI
    return p0 / K_LOW * NET_RATE_MINI + (p - p0) / K_HIGH * NET_RATE_AFTER


def pass_value(boxes: float, tiers: list[tuple[int, float]]) -> float:
    tickets = boxes * PASS_TICKETS_PER_BOX
    return sum(r for t, r in tiers if tickets >= t)


def snack_rewards_at_n(n: float) -> tuple[float, float, float, float]:
    boxes = n * BOXES_PER_SNACK
    cash = boxes * CASH_EV_PER_BOX
    jackpot = 0.0
    for index, thr in enumerate(JACKPOT_BOXES):
        if boxes >= thr:
            jackpot += JACKPOT_REWARDS[index] * (1 + int((boxes - thr) // CYCLE_BOXES))
    return cash, jackpot, pass_value(boxes, FREE_PASS_TIERS), pass_value(boxes, GOLD_PASS_TIERS)


def snack_rewards_at_net(net: float) -> float:
    mini_net = snack_milestone_net(MILESTONE_SNACK[0])
    if net <= mini_net:
        n = inv_s(net / NET_RATE_MINI * K_LOW)
    else:
        n = inv_s(s_frac(MILESTONE_SNACK[0]) + (net - mini_net) / NET_RATE_AFTER * K_HIGH)
    n = min(n, MILESTONE_SNACK[-1])  # 一轮终点封顶：Grand 后不再产奖
    cash, jackpot, free_pass, _ = snack_rewards_at_n(n)
    return cash + jackpot + free_pass


def lucky_rewards_at_net(net: float) -> float:
    """777：每格只中一次；现金按圈（外→中→内）兑现，樱桃/777 收集满3个在轮末兑现。"""
    dice = net / DICE_NET
    reward = 0.0
    cum = 0
    for round_idx, (need, cash_circles, collect) in enumerate(zip(DICE_PER_ROUND, CIRCLE_CASH, COLLECT_REWARD)):
        round_start = cum
        circle_cum = 0
        for circle_idx, circle_dice in enumerate(ROUND_STEP_DICE[round_idx]):
            circle_cum += circle_dice
            boundary = round_start + circle_cum
            if dice >= boundary - 1e-9:
                reward += cash_circles[circle_idx]
        if dice >= round_start + need - 1e-9:
            reward += collect
        cum += need
    return reward


def build_snack_milestones() -> list[dict]:
    out = []
    for index, n in enumerate(MILESTONE_SNACK):
        net = snack_milestone_net(n)
        cash, jackpot, free_pass, gold_pass = snack_rewards_at_n(n)
        total_free = cash + jackpot + free_pass
        out.append({"name": ["Mini", "Minor", "Major", "Grand"][index], "net": net, "reward": total_free})
    return out


def build_lucky_rounds() -> list[dict]:
    out = []
    cum_dice = 0
    cum_reward = 0.0
    for index, (need, rw) in enumerate(zip(DICE_PER_ROUND, ROUND_REWARDS)):
        cum_dice += need
        cum_reward += rw
        net = cum_dice * DICE_NET
        out.append({
            "round": index + 1, "dice": need, "cum_dice": cum_dice, "net": net, "reward": rw, "cum_reward": cum_reward,
            "step_reward": rw / need, "rate": cum_reward / net,
            "circle_cash": CIRCLE_CASH[index], "collect": COLLECT_REWARD[index],
        })
    return out


def build_merged_milestones() -> list[dict]:
    snacks = build_snack_milestones()
    luckies = build_lucky_rounds()
    items = []
    for s in snacks:
        items.append({
            "act": "薯片",
            "node": s["name"],
            "net": s["net"],
            "reward": s["reward"],
            "note": f"薯片：{s['name']} Jackpot 完成",
        })
    for l in luckies:
        circle = {
            1: "外圈20格→中圈12格→内圈4格（单步1/3/6骰）",
            2: "外圈20格→中圈12格→内圈4格（单步2/4/9骰）",
            3: "外圈20格→中圈12格→内圈4格（单步3/6/12骰），777通关",
        }[l["round"]]
        items.append({
            "act": "777",
            "node": f"第{l['round']}轮",
            "net": l["net"],
            "reward": l["cum_reward"],
            "note": f"777：第{l['round']}轮完成（每枚骰子抽一格即时发奖，{circle}；累计奖励${l['cum_reward']:.2f}）",
        })
    items.sort(key=lambda x: x["net"])
    for idx, item in enumerate(items):
        item["seq"] = idx + 1
    return items


def build_nodes() -> list[dict]:
    out = []
    for net in SPEND_NODES_NET:
        snack = snack_rewards_at_net(net)
        lucky = lucky_rewards_at_net(net)
        total = snack + lucky
        out.append({"net": net, "snack": snack, "lucky": lucky, "total": total, "rate": total / net if net > 0 else 0.0})
    return out


def build_gap_merged() -> list[dict]:
    snacks = build_snack_milestones()
    luckies = build_lucky_rounds()
    snack_end = snacks[-1]["net"]
    lucky_end = luckies[-1]["net"]
    rows = []
    for start in START_NET_OPTIONS:
        s_reached = [m["name"] for m in snacks if m["net"] <= start]
        s_next = next((m for m in snacks if m["net"] > start), None)
        l_reached = [f"第{r['round']}轮" for r in luckies if r["net"] <= start]
        l_next = next((r for r in luckies if r["net"] > start), None)
        both_end = max(snack_end, lucky_end)
        rows.append({
            "start": start,
            "s_reached": "、".join(s_reached) if s_reached else "无",
            "s_next": s_next["name"] if s_next else "已通关",
            "s_gap": max(0.0, s_next["net"] - start) if s_next else 0.0,
            "l_reached": "、".join(l_reached) if l_reached else "无",
            "l_next": f"第{l_next['round']}轮" if l_next else "已通关",
            "l_gap": max(0.0, l_next["net"] - start) if l_next else 0.0,
            "both_end": both_end,
            "both_gap": max(0.0, both_end - start),
        })
    return rows


def build_smooth_breakpoints() -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """薯片：4个Jackpot节点；777：9个圈节点（现金随圈、樱桃777轮末）。"""
    snacks = build_snack_milestones()
    snack_pts = [(0.0, 0.0)] + [(m["net"], m["reward"]) for m in snacks]
    lucky_pts = [(0.0, 0.0)]
    cum_dice = 0
    cum_reward = 0.0
    for round_idx, (need, cash_circles, collect) in enumerate(zip(DICE_PER_ROUND, CIRCLE_CASH, COLLECT_REWARD)):
        round_start = cum_dice
        circle_cum = 0
        for circle_idx, circle_dice in enumerate(ROUND_STEP_DICE[round_idx]):
            circle_cum += circle_dice
            cum_dice = round_start + circle_cum
            cum_reward += cash_circles[circle_idx]
            lucky_pts.append((cum_dice * DICE_NET, cum_reward))
        cum_dice = round_start + need
        cum_reward += collect
        lucky_pts[-1] = (cum_dice * DICE_NET, cum_reward)
    return snack_pts, lucky_pts


def lerp(pts: list[tuple[float, float]], x: float) -> float:
    if x <= pts[0][0]:
        return pts[0][1]
    for i in range(1, len(pts)):
        if x <= pts[i][0]:
            x0, y0 = pts[i - 1]
            x1, y1 = pts[i]
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0) if x1 > x0 else y1
    return pts[-1][1]


def fmt_usd(value: float) -> str:
    return f"${value:,.2f}"


def render_html(merged, lucky_rs, nodes, gap) -> str:
    merged_rows = "".join(
        "<tr>"
        f"<td>{m['seq']}</td><td>{m['node']}</td>"
        f"<td>{m['act']}</td>"
        f"<td>{fmt_usd(m['net'])}</td><td>{fmt_usd(m['reward'])}</td>"
        f"<td style='text-align:left;white-space:normal;min-width:320px'>{m['note']}</td></tr>"
        for m in merged
    )
    node_rows = "".join(
        "<tr>"
        f"<td>{fmt_usd(n['net'])}</td><td>{fmt_usd(n['snack'])}</td><td>{fmt_usd(n['lucky'])}</td>"
        f"<td>{fmt_usd(n['total'])}</td><td>{n['rate']*100:.0f}%</td></tr>"
        for n in nodes
    )
    lucky_rows = "".join(
        "<tr>"
        f"<td>第{r['round']}轮</td><td>{r['dice']}</td><td>{r['cum_dice']}</td><td>{fmt_usd(r['net'])}</td>"
        f"<td>{fmt_usd(r['circle_cash'][0])}</td><td>{fmt_usd(r['circle_cash'][1])}</td><td>{fmt_usd(r['circle_cash'][2])}</td>"
        f"<td>{fmt_usd(r['collect'])}</td><td>{fmt_usd(r['reward'])}</td><td>{fmt_usd(r['cum_reward'])}</td><td>{r['rate']*100:.0f}%</td></tr>"
        for r in lucky_rs
    )
    gap_rows = "".join(
        "<tr>"
        f"<td>{fmt_usd(r['start'])}</td><td>{r['s_reached']}</td><td>{r['s_next']}</td><td>{fmt_usd(r['s_gap'])}</td>"
        f"<td>{r['l_reached']}</td><td>{r['l_next']}</td><td>{fmt_usd(r['l_gap'])}</td>"
        f"<td>{fmt_usd(r['both_end'])}</td><td>{fmt_usd(r['both_gap'])}</td></tr>"
        for r in gap
    )

    maxv = 200.0
    snack_pts, lucky_pts = build_smooth_breakpoints()
    chart_x = [round(i * 0.5, 2) for i in range(0, int(maxv / 0.5) + 1)]
    labels_js = json.dumps([0, 40, 80, 120, 160, 200])
    pts = [{"x": x, "y": round(lerp(snack_pts, x) + lerp(lucky_pts, x), 2)} for x in chart_x]
    for boundary in [100.8, 158.17]:
        yb = round(lerp(snack_pts, boundary) + lerp(lucky_pts, boundary), 2)
        pts.append({"x": round(boundary, 2), "y": yb})
    pts.sort(key=lambda p: p["x"])
    seg1 = json.dumps([p for p in pts if p["x"] <= 100.8 + 1e-9])
    seg2 = json.dumps([p for p in pts if 100.8 - 1e-9 <= p["x"] <= 158.17 + 1e-9])
    seg3 = json.dumps([p for p in pts if p["x"] >= 158.17 - 1e-9])

    html = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CR 薯片×777 净消耗体验报告（v5.1）</title>
<style>
:root{{--bg:#09101f;--panel:#121c31;--panel2:#18253e;--text:#edf3ff;--muted:#9eb0cd;--line:#2b3b59;--snack:#ffb44d;--lucky:#75e0cf;--red:#ff6d7a}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 85% 0,#172c4d 0,transparent 35%),var(--bg);color:var(--text);font:14px/1.65 "Microsoft YaHei",system-ui,sans-serif}}main{{max-width:1260px;margin:auto;padding:42px 24px 80px}}h1{{font-size:40px;line-height:1.12;margin:8px 0 12px}}h2{{font-size:24px;margin:44px 0 16px}}h3{{font-size:17px;margin:28px 0 10px}}p{{color:var(--muted)}}.eyebrow{{color:var(--lucky);letter-spacing:.14em;font-weight:700}}.hero{{padding:38px;border:1px solid var(--line);border-radius:24px;background:linear-gradient(135deg,#14223b,#0e1729)}}.chips{{display:flex;gap:9px;flex-wrap:wrap;margin-top:20px}}.chip{{padding:6px 11px;border:1px solid var(--line);border-radius:999px;color:#cbd8ee;background:#0d1628}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:22px 0}}.card{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px}}.kpi{{font-size:26px;font-weight:800;margin:2px 0}}.snack{{color:var(--snack)}}.lucky{{color:var(--lucky)}}.sub{{font-size:12px;color:var(--muted)}}.callout{{border-left:3px solid var(--lucky);background:#101d31;padding:14px 18px;border-radius:0 12px 12px 0;margin:14px 0;color:#dbe7fa}}.warn{{border-left-color:var(--red)}}.two{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:14px}}table{{border-collapse:collapse;width:100%;min-width:1100px;background:var(--panel)}}th,td{{padding:11px 12px;border-bottom:1px solid var(--line);white-space:nowrap;text-align:right}}th{{position:sticky;top:0;background:#1b2944;color:#dce7f9;font-size:12px}}th:first-child,td:first-child{{text-align:left}}tr:hover td{{background:#17243d}}canvas{{display:block;max-width:600px;width:100%;height:auto;background:var(--panel);border:1px solid var(--line);border-radius:14px}}.status{{display:inline-block;padding:2px 7px;border-radius:6px;background:#193b35;color:#8af1dc;font-size:12px}}.status.assume{{background:#40341e;color:#ffd38d}}ul{{color:var(--muted)}}footer{{margin-top:50px;color:#7185a6;font-size:12px;border-top:1px solid var(--line);padding-top:18px}}@media(max-width:800px){{.grid,.two{{grid-template-columns:1fr}}h1{{font-size:30px}}}}
</style></head><body><main>
<section class="hero"><div class="eyebrow">CR SNACK × 777 · v5.1</div><h1>薯片 × 777<br>净消耗体验报告（v5.1）</h1><p>777 重新开放：三轮共384骰子、净消耗≈$100、每轮奖励≈12/10/8。薯片保持 v4（一轮净≈$158）。里程碑表合并为序号1-4 共用节点；合计返还曲线画到净消耗$600，薯片$158.2、777$100.8 之后奖励封顶，曲线为水平线。</p><div class="chips"><span class="chip">配置口径：2026-08-19</span><span class="chip">门槛 bet $1（85%）</span><span class="chip">薯片一轮净≈$158</span><span class="chip">777 三轮净≈$100</span><span class="chip">曲线到 $600</span><span class="chip">未提交</span></div></section>

<div class="grid"><div class="card"><div class="sub">薯片一轮净消耗</div><div class="kpi snack">$158.2</div><div class="sub">奖励$52.1</div></div><div class="card"><div class="sub">777 三轮净消耗</div><div class="kpi lucky">$100.8</div><div class="sub">奖励$30.1</div></div><div class="card"><div class="sub">合计封顶奖励</div><div class="kpi snack">$82.1</div><div class="sub">$158.2 后水平</div></div><div class="card"><div class="sub">777 返还曲线</div><div class="kpi lucky">57%→41%→30%</div><div class="sub">前高后低</div></div></div>

<h2>1. 合并里程碑：薯片 Jackpot × 777 轮次（按净消耗错开排序）</h2><div class="table-wrap"><table><thead><tr><th>序号</th><th>节点</th><th>活动</th><th>净消耗</th><th>累计奖励</th><th>备注</th></tr></thead><tbody>{merged_rows}</tbody></table></div>

<h2>2. 累计净消耗节点总览（薯片+777 并行）</h2><div class="table-wrap"><table><thead><tr><th>累计净消耗</th><th>薯片奖励</th><th>777奖励</th><th>合计奖励</th><th>合计返还率</th></tr></thead><tbody>{node_rows}</tbody></table></div>

<h2>3. 付费缺口（薯片 + 777 合并）</h2><div class="table-wrap"><table><thead><tr><th>起始净消耗</th><th>薯片已达成</th><th>薯片下一里程碑</th><th>薯片还需</th><th>777已达成</th><th>777下一轮</th><th>777还需</th><th>双活动通关总净消耗</th><th>通关还需</th></tr></thead><tbody>{gap_rows}</tbody></table></div>

<h2>4. 合计返还曲线：净消耗-奖励（薯片+777，到$600）</h2><canvas id="c" width="600" height="600"></canvas><p class="sub">绘图区正方形：横纵轴 $1 实际长度相同（$0–$600），45°线即100%返还率。薯片$158.2、777$100.8后奖励不再产出，合计封顶$82.1，之后为水平直线。</p>

<h2>5. 配置事实、假设与校验</h2><div class="table-wrap"><table><thead><tr><th>项目</th><th>口径</th><th>状态</th><th>影响</th></tr></thead><tbody><tr><td>薯片</td><td>Jackpot 1.1/3.1/11/30；Pass 1.5/10；一轮净≈$158后封顶</td><td><span class="status">已确认</span></td><td>与 v4 一致</td></tr><tr><td>777 获取</td><td>骰子7000积分/枚，384级+墙；三轮净≈$100</td><td><span class="status">已确认</span></td><td>深度 $100</td></tr><tr><td>777 奖励</td><td>每轮现金≈12/10/8，累计$30</td><td><span class="status assume">方向性</span></td><td>返还 57%→41%→30%</td></tr><tr><td>777 活动</td><td>Activity 1034 重开（type=23，截止2026-12-31）</td><td><span class="status">已确认</span></td><td>待上线</td></tr><tr><td>合计曲线</td><td>并行推进；薯片一轮、777三轮后封顶</td><td><span class="status assume">方向性</span></td><td>$158.2后水平线</td></tr></tbody></table></div>

<h2>6. 风险与建议</h2><div class="two"><div class="card"><h3>体验风险</h3><ul><li>777 第1轮返还57%偏高，需防刷子。</li><li>薯片按一轮封顶：若实际按5轮终点累计，$158后曲线仍会阶梯上升。</li><li>合计曲线为并行口径，实际分配需另行约定。</li></ul></div><div class="card"><h3>建议验证</h3><ul><li>程序确认 QuestGetLevel type5 385级与积分清零行为。</li><li>按轮次/圈模拟骰子消耗与现金格命中分布。</li><li>埋点看 $21/$54/$101（777）与 $2/$11/$40/$158（薯片）。</li></ul></div></div>

<h2>7. 复算口径</h2><div class="card"><p><b>薯片：</b>净消耗=Σ积分/k×净损率；奖励=现金+Jackpot+免费Pass；一轮后封顶。<br><b>777：</b>骰子成本=7000积分/4000积分每美元=$1.75；净=$0.2625/枚；三轮=384枚=$100.8。<br><b>合计：</b>N 下薯片奖励+777奖励（并行），$158.2后封顶$82.1。</p></div>
<footer>数据源：QuestPickGet / QuestPointsCheatSheet / QuestGetLevel / SnackDropItemCfg / QuestJackpotCfg / SnackPassReward / StrikeLucky / StrikeLuckyRound / Activity。生成日期：2026-08-19。v5.1 未提交。</footer>
</main>
"""
    new_js = (
        "<script>const c=document.getElementById('c'),x=c.getContext('2d'),W=c.width,H=c.height,p=55,"
        f"MAXV={maxv:.2f},X=(v)=>p+(v/MAXV)*(W-2*p),Y=(v)=>(H-p)-(v/MAXV)*(H-2*p),"
        f"xv={labels_js}, s1={seg1}, s2={seg2}, s3={seg3};"
        "x.clearRect(0,0,W,H);x.strokeStyle='#2b3b59';x.fillStyle='#9eb0cd';x.font='13px Microsoft YaHei';"
        "for(let i=0;i<=5;i++){let v=MAXV*i/5,yy=Y(v),xx=X(v);x.strokeStyle='#2b3b59';"
        "x.beginPath();x.moveTo(p,yy);x.lineTo(W-p,yy);x.stroke();"
        "x.beginPath();x.moveTo(xx,p);x.lineTo(xx,H-p);x.stroke();"
        "x.fillText('$'+v.toFixed(0),8,yy+4)}"
        "xv.forEach(v=>{let xx=X(v);x.fillText('$'+v,xx-16,H-14)});"
        "function line(pts,color){x.strokeStyle=color;x.lineWidth=3;x.beginPath();"
        "pts.forEach((pt,i)=>{let xx=X(pt.x),yy=Y(pt.y);i?x.lineTo(xx,yy):x.moveTo(xx,yy)});x.stroke()}"
        "line(s1,'#8fe388');line(s2,'#ffb44d');line(s3,'#9eb0cd');"
        "function legend(color,label,ly){x.fillStyle=color;x.fillRect(W-250,ly,11,11);x.fillStyle='#edf3ff';x.fillText(label,W-234,ly+9)}"
        "legend('#8fe388','薯片+777 产奖',20);legend('#ffb44d','仅薯片产奖',38);legend('#9eb0cd','均不再产奖',56);</script></body></html>"
    )
    html = html.replace("里程碑表合并为序号1-4 共用节点；合计返还曲线画到净消耗$600，薯", "里程碑表按净消耗错开合并；合计返还曲线画到净消耗$200，薯")
    html = html.replace("到$600）</h2>", "到$200）</h2>")
    html = html.replace("（$0–$600）", "（$0–$200）")
    html = html.replace("<span class=\"chip\">曲线到 $600</span>", "<span class=\"chip\">曲线到 $200</span>")
    html = html.replace("每轮奖励≈12/10/8。薯片保持 v4", "轮内累计奖励≈12/10/8（每枚骰子即时抽奖）。薯片保持 v4")
    lucky_section = (
        "<h2>2. 777 轮次（每枚骰子即时抽奖发奖）</h2><div class=\"table-wrap\"><table><thead><tr>"
        "<th>轮次</th><th>本轮骰子</th><th>累计骰子</th><th>累计净消耗</th><th>外圈现金</th><th>中圈现金</th><th>内圈现金</th><th>樱桃+777</th>"
        "<th>本轮奖励</th><th>累计奖励</th><th>累计返还率(净)</th></tr></thead><tbody>"
        + lucky_rows
        + "</tbody></table></div>"
        + "<div class=\"callout\"><b>777 口径：</b>每格只中一次：现金按圈（外→中→内）兑现，樱桃/777 收集满3个在轮末兑现；卡包/返骰未计入现金返还。</div>"
    )
    html = html.replace("<h2>2. 累计净消耗节点总览（薯片+777 并行）</h2>", lucky_section + "<h2>3. 累计净消耗节点总览（薯片+777 并行）</h2>")
    html = html.replace("<h2>3. 付费缺口（薯片 + 777 合并）</h2>", "<h2>4. 付费缺口（薯片 + 777 合并）</h2>")
    html = html.replace("<h2>4. 合计返还曲线", "<h2>5. 合计返还曲线")
    html = html.replace("之后为水平直线。</p>", "曲线为节点间线性插值的平滑口径；颜色分段：绿色=薯片+777都在产奖，黄色=仅薯片产奖，灰色=均不再产奖。$100.8（777结束）、$158.2（薯片结束）后逐段切换。</p>")
    html = html.replace("<h2>5. 配置事实", "<h2>6. 配置事实")
    html = html.replace("<h2>6. 风险与建议</h2>", "<h2>7. 风险与建议</h2>")
    html = html.replace("<h2>7. 复算口径</h2>", "<h2>8. 复算口径</h2>")
    return html + new_js


def main() -> None:
    merged = build_merged_milestones()
    nodes = build_nodes()
    gap = build_gap_merged()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    lucky_rs = build_lucky_rounds()
    HTML_PATH.write_text(render_html(merged, lucky_rs, nodes, gap), encoding="utf-8")
    print(f"HTML_WRITTEN={HTML_PATH}")
    print("MERGED:")
    for m in merged:
        print(f"  {m['seq']} {m['act']} {m['node']}: net={m['net']:.2f} reward={m['reward']:.2f}")
    print("NODES:")
    for n in nodes:
        print(f"  N={n['net']:.1f} snack={n['snack']:.2f} lucky={n['lucky']:.2f} total={n['total']:.2f}")


if __name__ == "__main__":
    main()
