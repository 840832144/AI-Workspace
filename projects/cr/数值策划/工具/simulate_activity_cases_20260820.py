r"""等级0/VIP0 活动模拟报告：不同持金×bet 的奖励-净消耗曲线（v2 修复）。

口径（等级0、VIP0，1USD=100万金币，PriceCheatSheet R=100万）：
- RTP：bet<100万 95%（净损5%），bet>=100万 85%（净损15%）
- 每净消耗 $1 的积分：低于门槛 2000÷0.05=40000；门槛及以上 4000÷0.15=26666.67
- 薯片：积分→160级上限（7500/12000/23500/33000），1.1144盒/枚，Jackpot 1.1/3.1/11/30（160枚=178.3盒，Grand不可达）
- 777：骰子7000积分/枚，384骰/3轮上限，奖励 12.04/22.05/30.08
- 每张图两条曲线：95%档（<100万）与 85%档（>=100万）；同档内不同 bet 曲线重合
"""

from __future__ import annotations

import json
from pathlib import Path

OUTPUT_DIR = Path(r"D:\cr_design\outputs\019ffe04-ee02-7f92-a661-34673faabe3f\activity_cases_20260820")
HTML_PATH = OUTPUT_DIR / "CR活动模拟报告_等级0VIP0.html"

BOXES_PER_SNACK = 1.1144
CASH_EV_PER_BOX = 0.03
JACKPOT = [1.10, 3.10, 11.00, 30.00]
JACKPOT_BOXES = [13.524, 35.556, 72.5, 178.571]
SNACK_CAP = 160
SNACK_THRESHOLDS = [7500] * 12 + [12000] * 20 + [23500] * 33 + [33000] * (SNACK_CAP - 65)
SNACK_CUM = [0]
for p in SNACK_THRESHOLDS:
    SNACK_CUM.append(SNACK_CUM[-1] + p)

DICE_POINTS = 7000.0
DICE_PER_ROUND = [80, 124, 180]
CIRCLE_CASH = [[2.09, 3.38, 1.88], [1.43, 2.34, 1.30], [0.99, 1.64, 0.90]]
COLLECT = [4.69, 4.94, 4.50]
ROUND_STEP_DICE = [[20, 36, 24], [40, 48, 36], [60, 72, 48]]
FREE_PASS = [(1, 0.06), (2, 0.07), (4, 0.07), (6, 0.08), (8, 0.08), (10, 0.09), (12, 0.09),
             (14, 0.10), (16, 0.10), (18, 0.11), (20, 0.11), (25, 0.12), (30, 0.12), (35, 0.13), (40, 0.17)]

BANKROLLS = [5, 10, 20, 50, 100]
BETS = [10000, 100000, 1000000, 5000000, 10000000]
STEP = 0.2

POINTS_PER_NET = {"below": 2000 / 0.05, "above": 4000 / 0.15}
ENDPOINT_NET = round(sum(SNACK_THRESHOLDS) / POINTS_PER_NET["above"], 2)  # 全部活动终点：85%档薯片 $159.02
LUCKY_ENDPOINT_NET = round(DICE_POINTS * sum(DICE_PER_ROUND) / POINTS_PER_NET["above"], 2)  # 85%档777 $100.80
BANKROLLS = BANKROLLS + [ENDPOINT_NET]  # 追加“全部活动终点”持金档


def snack_reward(points: float) -> float:
    count = 0
    for cum in SNACK_CUM[1:]:
        if points >= cum:
            count += 1
    boxes = count * BOXES_PER_SNACK
    cash = boxes * CASH_EV_PER_BOX
    jp = 0.0
    for index, thr in enumerate(JACKPOT_BOXES):
        if boxes >= thr:
            jp += JACKPOT[index]
    tickets = boxes * 0.5
    free = sum(r for t, r in FREE_PASS if tickets >= t)
    return cash + jp + free


def lucky_reward(dice: float) -> float:
    reward = 0.0
    cum = 0
    for r_idx, (need, cash_circles, collect) in enumerate(zip(DICE_PER_ROUND, CIRCLE_CASH, COLLECT)):
        round_start = cum
        circle_cum = 0
        for c_idx, c_dice in enumerate(ROUND_STEP_DICE[r_idx]):
            circle_cum += c_dice
            if dice >= round_start + circle_cum - 1e-9:
                reward += cash_circles[c_idx]
        if dice >= round_start + need - 1e-9:
            reward += collect
        cum += need
    return reward


def rewards_at_net(net: float, tier: str) -> tuple[float, float, float]:
    points = POINTS_PER_NET[tier] * net
    snack = snack_reward(points)
    lucky = lucky_reward(points / DICE_POINTS)
    return snack, lucky, snack + lucky


def build_case(bankroll: float) -> dict:
    xs = [round(i * STEP, 2) for i in range(0, int(ENDPOINT_NET / STEP) + 1)]
    series = []
    for tier in ["below", "above"]:
        ys = [round(rewards_at_net(n, tier)[2], 3) for n in xs]
        series.append({"tier": tier, "pts": [{"x": x, "y": y} for x, y in zip(xs, ys)]})
    summary = []
    for bet in BETS:
        tier = "below" if bet < 1_000_000 else "above"
        net_rate = 0.05 if tier == "below" else 0.15
        spins = bankroll / ((bet / 1_000_000) * net_rate)
        snack, lucky, total = rewards_at_net(bankroll, tier)
        summary.append({
            "bet_label": f"{bet // 10000}万", "tier": tier, "spins": spins,
            "snack": snack, "lucky": lucky, "total": total, "rate": total / bankroll,
        })
    return {"bankroll": bankroll, "series": series, "summary": summary, "endpoint": ENDPOINT_NET}


def fmt_usd(v: float) -> str:
    return f"${v:,.2f}"


def render_html(cases: list[dict]) -> str:
    cards = []
    scripts = []
    colors = {"below": "#ffb44d", "above": "#75e0cf"}
    for case in cases:
        b = case["bankroll"]
        cid = f"c{int(b)}"
        is_end = b >= case["endpoint"] - 0.001
        title = f"持金 {fmt_usd(b)}（{int(b * 100)}万金币）" + ("，覆盖全部活动终点" if is_end else "")
        cards.append(
            f"<h3>{title}</h3>"
            f"<canvas id=\"{cid}\" width=\"600\" height=\"600\"></canvas>"
            "<p class=\"sub\">横纵轴均为 $0–" + fmt_usd(case["endpoint"]) + "（同尺度，覆盖全部活动终点），斜率=返还率(净)。"
            "黄线=95%档（bet&lt;100万），青线=85%档（bet≥100万）；同档内不同 bet 曲线重合；虚线=该持金的净消耗耗尽点。</p>"
        )
        rows = "".join(
            "<tr>"
            f"<td>{fmt_usd(b)}</td><td>{r['bet_label']}</td><td>{'95%' if r['tier'] == 'below' else '85%'}</td>"
            f"<td>{r['spins']:,.0f}</td><td>{fmt_usd(r['snack'])}</td><td>{fmt_usd(r['lucky'])}</td>"
            f"<td>{fmt_usd(r['total'])}</td><td>{r['rate'] * 100:.1f}%</td></tr>"
            for r in case["summary"]
        )
        cards.append(
            "<div class=\"table-wrap\"><table><thead><tr><th>累计净消耗(持金)</th><th>Bet</th><th>RTP档</th><th>总Spin</th>"
            "<th>薯片奖励</th><th>777奖励</th><th>合计奖励</th><th>合计返还率(净)</th></tr></thead><tbody>"
            + rows + "</tbody></table></div>"
        )
        scripts.append(
            f"const s{cid}={{'below':{json.dumps(case['series'][0]['pts'])},'above':{json.dumps(case['series'][1]['pts'])}}};"
            f"draw('{cid}',s{cid},{case['endpoint']},{b if not is_end else 'null'});"
        )
    draw_js = (
        "function draw(cid,s,maxv,mark){"
        "const c=document.getElementById(cid),x=c.getContext('2d'),W=c.width,H=c.height,p=55,"
        "X=(v)=>p+(v/maxv)*(W-2*p),Y=(v)=>(H-p)-(v/maxv)*(H-2*p);"
        "x.clearRect(0,0,W,H);x.font='12px Microsoft YaHei';"
        "for(let i=0;i<=5;i++){let v=maxv*i/5,yy=Y(v),xx=X(v);"
        "x.strokeStyle='#2b3b59';x.beginPath();x.moveTo(p,yy);x.lineTo(W-p,yy);x.stroke();"
        "x.beginPath();x.moveTo(xx,p);x.lineTo(xx,H-p);x.stroke();"
        "x.fillStyle='#9eb0cd';x.fillText('$'+v.toFixed(0),8,yy+4);x.fillText('$'+v.toFixed(0),xx-12,H-p+20)}"
        "function line(pts,col){x.strokeStyle=col;x.lineWidth=2.5;x.beginPath();"
        "pts.forEach((pt,i)=>{let xx=X(pt.x),yy=Y(pt.y);i?x.lineTo(xx,yy):x.moveTo(xx,yy)});x.stroke()}"
        "line(s.below,'#ffb44d');line(s.above,'#75e0cf');"
        "if(mark!=null&&mark<maxv-0.001){let mx=X(mark);x.strokeStyle='#55688c';x.setLineDash([6,4]);"
        "x.beginPath();x.moveTo(mx,p);x.lineTo(mx,H-p);x.stroke();x.setLineDash([]);"
        "x.fillStyle='#9eb0cd';x.fillText('持金$'+mark.toFixed(2)+' 耗尽',mx+5,p+14)}"
        "x.fillStyle='#ffb44d';x.fillText('95%档(<100万)',W-190,24);"
        "x.fillStyle='#75e0cf';x.fillText('85%档(≥100万)',W-190,44)}"
    )
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>CR 活动模拟报告（等级0/VIP0）</title>
<style>
:root{{--bg:#09101f;--panel:#121c31;--panel2:#18253e;--text:#edf3ff;--muted:#9eb0cd;--line:#2b3b59;--snack:#ffb44d;--lucky:#75e0cf}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 85% 0,#172c4d 0,transparent 35%),var(--bg);color:var(--text);font:14px/1.65 "Microsoft YaHei",system-ui,sans-serif}}main{{max-width:1080px;margin:auto;padding:40px 24px 80px}}h1{{font-size:36px}}h2{{font-size:22px;margin:36px 0 12px}}h3{{font-size:16px;margin:20px 0 8px}}p{{color:var(--muted)}}.chips{{display:flex;gap:9px;flex-wrap:wrap;margin:14px 0}}.chip{{padding:5px 11px;border:1px solid var(--line);border-radius:999px;color:#cbd8ee;background:#0d1628}}.card-wide{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px;margin:18px 0}}canvas{{display:block;max-width:480px;width:100%;height:auto;margin:10px auto;background:#0e1729;border:1px solid var(--line);border-radius:12px}}.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:12px;margin:10px 0}}table{{border-collapse:collapse;width:100%;min-width:640px;background:var(--panel)}}th,td{{padding:9px 12px;border-bottom:1px solid var(--line);white-space:nowrap;text-align:right}}th{{background:#1b2944;color:#dce7f9;font-size:12px}}th:first-child,td:first-child{{text-align:left}}tr:hover td{{background:#17243d}}.callout{{border-left:3px solid var(--lucky);background:#101d31;padding:12px 16px;border-radius:0 12px 12px 0;margin:12px 0;color:#dbe7fa}}footer{{margin-top:40px;color:#7185a6;font-size:12px;border-top:1px solid var(--line);padding-top:16px}}
</style></head><body><main>
<h1>CR 活动模拟报告</h1>
<p>等级 0 / VIP0，1 USD = 100 万金币。简单期望模拟：不同持金 × 不同 bet 的“累计奖励-累计净消耗”曲线（薯片+777 合计），按当前 v6 配置逐点计算。</p>
<div class="chips"><span class="chip">RTP：&lt;100万 95% / ≥100万 85%</span><span class="chip">净消耗积分/$：40,000 / 26,667</span><span class="chip">薯片上限160枚（Grand不可达）</span><span class="chip">777上限384骰/3轮</span><span class="chip">窗口到全部活动终点 $159.02</span></div>
<div class="callout"><b>说明：</b>同 RTP 档内不同 bet 的“奖励-净消耗”曲线完全重合，因此每张图只画 95% 与 85% 两条；返还率(净)=薯片+777 合计奖励÷累计净消耗（并行推进口径）；虚线=该持金净消耗耗尽点，虚线右侧为持金无法达到的区间。</div>
<div class="table-wrap"><table><thead><tr><th>活动终点</th><th>RTP档</th><th>累计净消耗</th><th>累计奖励</th><th>终点返还率(净)</th></tr></thead><tbody>
<tr><td>薯片 160 枚（Grand 差 0.27 盒不可达，止于 Major）</td><td>85%</td><td>$159.02</td><td>$22.05</td><td>13.9%</td></tr>
<tr><td>薯片 160 枚（Grand 差 0.27 盒不可达，止于 Major）</td><td>95%</td><td>$106.01</td><td>$22.05</td><td>20.8%</td></tr>
<tr><td>777 三轮（384 骰）</td><td>85%</td><td>$100.80</td><td>$30.08</td><td>29.8%</td></tr>
<tr><td>777 三轮（384 骰）</td><td>95%</td><td>$67.20</td><td>$30.08</td><td>44.8%</td></tr>
<tr><td>双活动合计（到薯片终点）</td><td>85%</td><td>$159.02</td><td>$52.13</td><td>32.8%</td></tr>
<tr><td>双活动合计（到薯片终点）</td><td>95%</td><td>$106.01</td><td>$52.13</td><td>49.2%</td></tr>
</tbody></table></div>
<p class="sub">与之前报告一致：85% 档 $100 节点合计返还率 45.1%（v5 同节点 45%）；777 终点返还率 30% 与 v5 一致。注意：v5 报告薯片终点 $52.06（含 Grand），而当前 v6 配置 160 枚=178.3 盒、Grand 需 178.57 盒，终点实际止于 Major（$22.05），因此薯片终点返还率从 v5 的 33% 降到 13.9%（85% 档）/20.8%（95% 档）。95% 档每 $1 净消耗对应积分更高（40,000 vs 26,667），同一奖励对应的净消耗更浅，返还率整体更高。各图窗口统一到全部活动终点 $159.02，虚线=该持金净消耗耗尽点，虚线右侧为该持金无法达到的区间。</p>
{"".join(cards)}
<footer>数据源：QuestPickGet / QuestPointsCheatSheet / QuestGetLevel / SnackDropItemCfg / QuestJackpotCfg / SnackPassReward / StrikeLucky / StrikeLuckyRound / PriceCheatSheet。生成日期：2026-08-20。</footer>
</main>
<script>
{draw_js}
{"".join(scripts)}
</script></body></html>"""


def main() -> None:
    cases = [build_case(b) for b in BANKROLLS]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    HTML_PATH.write_text(render_html(cases), encoding="utf-8")
    print(f"HTML_WRITTEN={HTML_PATH}")
    for case in cases:
        print(f"持金 ${case['bankroll']}:")
        for s in case["summary"]:
            print(f"  bet {s['bet_label']} tier={s['tier']} spins={s['spins']:.0f} snack={s['snack']:.2f} lucky={s['lucky']:.2f} total={s['total']:.2f} rate={s['rate']*100:.1f}%")


if __name__ == "__main__":
    main()
