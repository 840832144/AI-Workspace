"""挖矿 / 拳击 体验预期报告（对标薯片 / 777，净消耗模型）。

本报告是设计目标，不是最终配置：挖矿复用薯片的净消耗深度与返还曲线，
拳击复用 777 的净消耗深度与返还曲线；具体奖励金额待需求定稿后配置。
"""

from __future__ import annotations

import json
from pathlib import Path

OUT_DIR = Path(r"D:\cr_design\outputs\019ffe04-ee02-7f92-a661-34673faabe3f\miner_boxing_expectation_20260825")
HTML_PATH = OUT_DIR / "CR挖矿拳击体验预期报告.html"

# 对标薯片 / 777 的净消耗里程碑（85%档，净消耗=毛消耗×15%）
# 挖矿 <- 薯片，拳击 <- 777
MINER_NODES = [
    ("红宝石", "对标薯片 Mini", 2.29, 1.79),
    ("绿宝石", "对标薯片 Minor", 11.19, 6.01),
    ("蓝宝石", "对标薯片 Major", 40.38, 18.70),
    ("一轮通关", "对标薯片 Grand", 158.17, 52.06),
]
BOXING_ROUNDS = [
    ("第1轮·初级轨道·绿宝石", "对标777第1轮", 21.00, 12.04, "57%"),
    ("第2轮·中级轨道·蓝宝石", "对标777第2轮", 53.55, 22.05, "41%"),
    ("第3轮·高级轨道·粉宝石", "对标777第3轮", 100.80, 30.08, "30%"),
]

# 合并累计净消耗节点总览（挖矿+拳击 并行，来自薯片×777 v5.1 口径）
COMBINED = [
    (0.00, 0.00),
    (1.00, 0.31),
    (2.29, 0.69),
    (5.00, 2.16),
    (11.19, 8.10),
    (20.00, 12.03),
    (21.00, 18.64),
    (40.38, 21.17),
    (53.55, 41.28),
    (60.00, 41.45),
    (100.00, 45.17),
    (100.80, 50.59),
    (158.17, 82.14),
    (200.00, 82.14),
]

BETS = [10000, 100000, 1000000, 5000000, 10000000]
BANKROLLS = [5, 10, 20, 50, 100, 200]


def spins(bankroll: float, bet: int) -> int:
    bet_usd = bet / 1_000_000
    net_rate = 0.05 if bet < 1_000_000 else 0.15
    return round(bankroll / (bet_usd * net_rate))


def fmt(v: float) -> str:
    return f"${v:,.2f}"


def build_merge_table() -> str:
    rows = []
    for name, tag, net, reward in MINER_NODES:
        rows.append((net, "挖矿", name, tag, reward))
    for name, tag, net, reward, _rate in BOXING_ROUNDS:
        rows.append((net, "拳击", name, tag, reward))
    rows.sort(key=lambda x: x[0])
    html = []
    for i, (net, kind, name, tag, reward) in enumerate(rows, 1):
        rate = reward / net if net else 0
        html.append(
            f"<tr><td>{i}</td><td>{kind}</td><td>{name}</td><td>{fmt(net)}</td>"
            f"<td>{fmt(reward)}</td><td>{rate*100:.0f}%</td>"
            f"<td style='text-align:left'>{tag}</td></tr>"
        )
    return "".join(html)


def build_gap_table() -> str:
    html = []
    for br in BANKROLLS:
        for bet in BETS:
            tier = "95%" if bet < 1_000_000 else "85%"
            html.append(
                f"<tr><td>{fmt(br)}</td><td>{bet//10000}万</td><td>{tier}</td>"
                f"<td>{spins(br,bet):,}</td>"
                f"<td>{fmt(max(0.0,158.17-br))}</td>"
                f"<td>{fmt(max(0.0,100.80-br))}</td>"
                f"<td>{fmt(158.17)}</td></tr>"
            )
    return "".join(html)


def build_combined_table() -> str:
    html = []
    for net, reward in COMBINED:
        rate = reward / net if net else 0
        html.append(
            f"<tr><td>{fmt(net)}</td><td>{fmt(reward)}</td><td>{rate*100:.1f}%</td></tr>"
        )
    return "".join(html)


def render() -> str:
    seg_green = [p for p in COMBINED if p[0] <= 100.80]
    seg_yellow = [p for p in COMBINED if 100.80 <= p[0] <= 158.17]
    seg_gray = [p for p in COMBINED if p[0] >= 158.17]
    data = {
        "green": seg_green,
        "yellow": seg_yellow,
        "gray": seg_gray,
    }
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CR 挖矿×拳击 体验预期报告（净消耗）</title>
<style>
:root{{--bg:#09101f;--panel:#121c31;--panel2:#18253e;--text:#edf3ff;--muted:#9eb0cd;--line:#2b3b59;--green:#75e0cf;--yellow:#ffb44d;--gray:#7185a6;--red:#ff6d7a}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 85% 0,#172c4d 0,transparent 35%),var(--bg);color:var(--text);font:14px/1.65 "Microsoft YaHei",system-ui,sans-serif}}main{{max-width:1160px;margin:auto;padding:42px 24px 80px}}h1{{font-size:38px;line-height:1.15;margin:8px 0 12px}}h2{{font-size:23px;margin:42px 0 14px}}h3{{font-size:17px;margin:28px 0 10px}}p{{color:var(--muted)}}.eyebrow{{color:var(--green);letter-spacing:.14em;font-weight:700}}.hero{{padding:36px;border:1px solid var(--line);border-radius:22px;background:linear-gradient(135deg,#14223b,#0e1729)}}.chips{{display:flex;gap:9px;flex-wrap:wrap;margin-top:18px}}.chip{{padding:5px 11px;border:1px solid var(--line);border-radius:999px;color:#cbd8ee;background:#0d1628;font-size:12px}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:22px 0}}.card{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px}}.kpi{{font-size:25px;font-weight:800;margin:2px 0}}.miner{{color:var(--yellow)}}.boxing{{color:var(--green)}}.sub{{font-size:12px;color:var(--muted)}}.callout{{border-left:3px solid var(--green);background:#101d31;padding:14px 18px;border-radius:0 12px 12px 0;margin:14px 0;color:#dbe7fa}}.warn{{border-left-color:var(--red)}}.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:14px;margin:12px 0}}table{{border-collapse:collapse;width:100%;min-width:760px;background:var(--panel)}}th,td{{padding:10px 12px;border-bottom:1px solid var(--line);white-space:nowrap;text-align:right}}th{{position:sticky;top:0;background:#1b2944;color:#dce7f9;font-size:12px}}th:first-child,td:first-child{{text-align:left}}tr:hover td{{background:#17243d}}canvas{{display:block;max-width:620px;width:100%;height:auto;margin:12px auto;background:var(--panel);border:1px solid var(--line);border-radius:14px}}footer{{margin-top:48px;color:#7185a6;font-size:12px;border-top:1px solid var(--line);padding-top:18px}}@media(max-width:800px){{.grid{{grid-template-columns:1fr 1fr}}h1{{font-size:30px}}}}
</style></head><body><main>
<section class="hero"><div class="eyebrow">CR 小游戏轮换 · 体验预期</div>
<h1>挖矿 × 拳击<br>体验预期报告（净消耗模型）</h1>
<p>小游戏轮换暂定：挖矿对标薯片、拳击对标 777。本文给出两者的净消耗深度、返还曲线、付费缺口和合计返还曲线作为设计目标；当前配置仍为测试数据，具体奖励金额待需求定稿后按本曲线配置。</p>
<div class="chips"><span class="chip">净消耗口径</span><span class="chip">85%档 净损15% / 95%档 净损5%</span><span class="chip">1 USD = 1,000,000 金币（等级0/VIP0）</span><span class="chip">挖矿↔薯片</span><span class="chip">拳击↔777</span></div></section>

<div class="grid">
<div class="card"><div class="sub">挖矿一轮净消耗</div><div class="kpi miner">$158.17</div><div class="sub">对标薯片一轮 Grand（85%档）</div></div>
<div class="card"><div class="sub">拳击三轮净消耗</div><div class="kpi boxing">$100.80</div><div class="sub">对标777三轮（85%档）</div></div>
<div class="card"><div class="sub">合计封顶奖励</div><div class="kpi">$82.14</div><div class="sub">挖矿$158.17后水平</div></div>
<div class="card"><div class="sub">拳击返还曲线</div><div class="kpi boxing">57%→41%→30%</div><div class="sub">对标777，前高后低</div></div>
</div>

<div class="callout warn"><b>说明：</b>这是“数值体验预期”目标，不是最终配置。挖矿/拳击最终要在各自的掉落、开盒/格子、宝石 Jackpot、通关奖励里配置到与本曲线一致的净消耗深度和返还率；奖励金额待需求定稿后落地。</div>

<h2>1. 对标关系</h2>
<div class="table-wrap"><table><thead><tr><th>新玩法</th><th>对标</th><th>消耗深度</th><th>返还曲线</th></tr></thead><tbody>
<tr><td>挖矿</td><td>薯片</td><td>一轮约 $158.17（85%档）</td><td>Mini/Minor/Major/Grand 对齐薯片四档</td></tr>
<tr><td>拳击</td><td>777</td><td>三轮约 $100.80（85%档）</td><td>三轨道宝石对齐777三轮 57%→41%→30%</td></tr>
</tbody></table></div>

<h2>2. 合并里程碑（挖矿 × 拳击，按净消耗错开排序）</h2>
<div class="table-wrap"><table><thead><tr><th>序号</th><th>活动</th><th>节点</th><th>净消耗</th><th>累计奖励</th><th>返还率</th><th>对标</th></tr></thead><tbody>
{build_merge_table()}
</tbody></table></div>

<h2>3. 拳击三轮（对标777，每轮返还率）</h2>
<div class="table-wrap"><table><thead><tr><th>轮次</th><th>对标</th><th>累计净消耗</th><th>累计奖励</th><th>累计返还率(净)</th></tr></thead><tbody>
{''.join(f"<tr><td>{n}</td><td>{t}</td><td>{fmt(x)}</td><td>{fmt(r)}</td><td>{rate}</td></tr>" for n,t,x,r,rate in BOXING_ROUNDS)}
</tbody></table></div>

<h2>4. 累计净消耗节点总览（挖矿+拳击 并行）</h2>
<div class="table-wrap"><table><thead><tr><th>累计净消耗</th><th>合计奖励</th><th>合计返还率</th></tr></thead><tbody>
{build_combined_table()}
</tbody></table></div>

<h2>5. 付费缺口（不同起始净消耗 × bet）</h2>
<div class="table-wrap"><table><thead><tr><th>起始净消耗</th><th>Bet</th><th>RTP档</th><th>总Spin</th><th>挖矿还需</th><th>拳击还需</th><th>双活动通关总净消耗</th></tr></thead><tbody>
{build_gap_table()}
</tbody></table></div>

<h2>6. 合计返还曲线：净消耗-奖励（挖矿+拳击，到$200）</h2>
<canvas id="c" width="620" height="620"></canvas>
<p class="sub">绘图区正方形：横纵轴 $1 实际长度相同（$0–$200），45°线即100%返还率；节点间线性插值。绿色=挖矿+拳击都在产奖，黄色=仅挖矿产奖，灰色=均不再产奖（拳击$100.80结束、挖矿$158.17结束）。</p>

<h2>7. 口径与待确认</h2>
<div class="table-wrap"><table><thead><tr><th>项目</th><th>口径</th><th>状态</th></tr></thead><tbody>
<tr><td>净消耗</td><td>净消耗 = 毛消耗 × 净损率；85%档净损15%、95%档净损5%</td><td>已确认</td></tr>
<tr><td>挖矿对标</td><td>复用薯片四档 Jackpot 的净消耗节点与返还曲线</td><td>方向已定，奖励金额待定</td></tr>
<tr><td>拳击对标</td><td>复用777三轮的净消耗节点与返还曲线 57%→41%→30%</td><td>方向已定，奖励金额待定</td></tr>
<tr><td>等级/VIP膨胀</td><td>积分=系数×bet÷(1美金金币值)÷难度，按等级/VIP查表</td><td>待需求定稿</td></tr>
<tr><td>RTP切换</td><td>门槛 betIndex 及以上切85%、以下95%</td><td>待程序确认 spinNum</td></tr>
</tbody></table></div>

<footer>挖矿 ↔ 薯片；拳击 ↔ 777。净消耗模型；里程碑与曲线复用《CR薯片与777净消耗体验报告 v5.1》口径，待最终配置落地后按实际奖励复算更新。</footer>
</main>
<script>
const data = {json.dumps(data)};
function draw(){{const c=document.getElementById('c'),x=c.getContext('2d'),W=c.width,H=c.height,p=58,X=(v)=>p+(v/200)*(W-2*p),Y=(v)=>(H-p)-(v/200)*(H-2*p);x.clearRect(0,0,W,H);x.font='12px Microsoft YaHei';for(let i=0;i<=5;i++){{let v=i*40,yy=Y(v),xx=X(v);x.strokeStyle='#2b3b59';x.beginPath();x.moveTo(p,yy);x.lineTo(W-p,yy);x.stroke();x.beginPath();x.moveTo(xx,p);x.lineTo(xx,H-p);x.stroke();x.fillStyle='#9eb0cd';x.fillText('$'+v,6,yy+4);x.fillText('$'+v,xx-10,H-p+20)}}function line(pts,col){{x.strokeStyle=col;x.lineWidth=2.5;x.beginPath();pts.forEach((pt,i)=>{{let xx=X(pt[0]),yy=Y(pt[1]);i?x.lineTo(xx,yy):x.moveTo(xx,yy)}});x.stroke()}}line(data.green,'#75e0cf');line(data.yellow,'#ffb44d');line(data.gray,'#7185a6');x.fillStyle='#75e0cf';x.fillText('挖矿+拳击都在产奖',W-170,24);x.fillStyle='#ffb44d';x.fillText('仅挖矿产奖',W-170,44);x.fillStyle='#7185a6';x.fillText('均不再产奖',W-170,64)}}
draw();
</script></body></html>"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    HTML_PATH.write_text(render(), encoding="utf-8")
    print(f"HTML_WRITTEN={HTML_PATH}")


if __name__ == "__main__":
    main()
