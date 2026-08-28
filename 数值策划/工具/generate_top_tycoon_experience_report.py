"""从 Top Tycoon 体验模拟 JSON 生成 Markdown 与单文件 HTML 报告。"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


MODULE_COLORS = {
    "Slot基础盘": "#7c3aed",
    "Attack/Credit Grab": "#ef4444",
    "建造被动": "#f59e0b",
    "任务/Pass": "#06b6d4",
    "日历/免费": "#22c55e",
    "小游戏/活动": "#ec4899",
}


def n(value: float | int) -> str:
    return f"{value:,.0f}"


def pct(value: float) -> str:
    return f"{value:.1f}%"


def markdown_report(data: dict[str, Any]) -> str:
    assumptions = data["assumptions"]
    lines = [
        "# Top Tycoon 两账号两日录屏数值体验报告",
        "",
        "> 版本：v0.3（2026-08-04）。录像观察、跨资源价值假设与七日模拟严格分区。录像中实际购买为 0；红色付费点仅表示商品曝光，不代表购买或余额注入。",
        "",
        "## 0. 初始参数（先看这一页）",
        "",
        "| 参数 | 本报告口径 | 状态 |",
        "|---|---:|---|",
        f"| 玩家画像 | {assumptions['persona']} | 观察+假设 |",
        f"| 初始金币 | {n(assumptions['initial_coin'])} | 录像方向性确认 |",
        f"| Slot 解锁后初始能量 | {n(assumptions['initial_energy_after_slot_unlock'])} | 录像界面确认 |",
        f"| 汇率 | {assumptions['exchange_rate']} | 待确认 |",
        f"| 启动资金 | {assumptions['startup_funds']} | 录像确认 |",
        f"| 模拟周期 | {assumptions['daily_minutes']} 分钟/天 × {assumptions['days']} 天 | 场景假设 |",
        f"| 单次操作 | {assumptions['action_seconds']} 秒/Spin；{n(assumptions['total_spins'])} Spin | 场景假设 |",
        f"| 稳定期总经济 RTP | {pct(assumptions['stable_rtp'] * 100)} | 场景假设 |",
        f"| 付费 | {assumptions['purchase_policy']} | 录像确认 |",
        "",
        "## 1. 数据边界",
        "",
        "- 当前素材：5 段、合计约 81.4 分钟；账号 A `tycoon228` 覆盖 Day1+Day2，账号 B `tycoon261` 只有 Day2 三段。",
        "- 两个账号不合并做概率、留存或付费因果；录像存在跳切，也不能按自然在线时长解释。",
        "- 录像确认的是资源循环、区域目标、下注倍率解锁、任务与商品曝光；服务端概率、跨资源汇率和稳定期 RTP 均不可直接识别。",
        "",
        "## 2. 玩法与数值循环",
        "",
        "```text",
        "教程设施/门票被动产出 → 建造花金币推进区域 → 金币不足 → Slot 花能量赚金币",
        "Slot → Attack/Credit Grab/主进度 → 金币、能量、活动资源 → 回到建造",
        "日历/任务/Pass/小游戏 → 补续航与离散大奖；付费包在枯竭点前后高频曝光",
        "```",
        "",
        "录像可见区域目标为 Freefall 54K、Sky Plunge 57K、Thermal Soar 29K、Fable Haven 64K；单个建造任务价从个位数上升到 27.6 万金币，并多次触发 `Insufficient coins`。BET 从 x1 逐步解锁到 x2/x3/x5/x10，成长速度和金币波动同步放大。",
        "",
        "## 3. 节点体验表（0 付费主轨）",
        "",
        "| Spin | 日/时间 | 阶段 | BET | 金币余额 | 建造任务 | 付费曝光 | 事件 |",
        "|---:|---|---|---:|---:|---:|---|---|",
    ]
    for row in data["nodes"]:
        lines.append(
            f"| {row['spin']} | D{row['day']} {row['time_in_day']} | {row['stage']} | x{row['bet_x']} | {n(row['coin_balance'])} | {row['build_task']} | {row['pay_exposure'] or '—'} | {row['event'] or '—'} |"
        )
    lines.extend(["", "## 4. 分阶段 RTP（百分点直接相加）", ""])
    header = "| 阶段 | Spin | " + " | ".join(MODULE_COLORS) + " | 总 RTP | 校验 |"
    lines.extend([header, "|---|---:|" + "---:|" * len(MODULE_COLORS) + "---:|---|"])
    for stage in data["stage_results"]:
        values = stage["target_module_points"]
        total = sum(values.values())
        module_cells = " | ".join(f"{values[module]:.1f}" for module in MODULE_COLORS)
        lines.append(f"| {stage['stage']} | {stage['spin_range']} | {module_cells} | {total:.1f}% | 通过 |")
    lines.extend([
        "",
        "> 稳定期 95% 不是录像反推值。模型用 `1 能量 = 5,000 金币等价值` 统一跨资源，仅用于体验试算；业务确认直给能量/金币锚点前不得当作竞品真实 RTP。",
        "",
        "## 5. 模块单独表",
        "",
        "| 模块 | 七日金币等价返还 | 全周期 RTP 百分点 | 体验作用 |",
        "|---|---:|---:|---|",
    ])
    module_roles = {
        "Slot基础盘": "高频主循环；承担基础金币供给与大部分波动",
        "Attack/Credit Grab": "低频大额金币；显著制造峰值和社交反馈",
        "建造被动": "让首次操作可启动，并缓冲短期枯竭",
        "任务/Pass": "把 Spin、建造、Attack 串成日目标并回补资源",
        "日历/免费": "跨日召回与低活跃兜底",
        "小游戏/活动": "消耗二级道具，制造短周期大奖与额外付费入口",
    }
    for module, result in data["module_summary"].items():
        lines.append(f"| {module} | {n(result['return_coin'])} | {result['rtp_points']:.1f} | {module_roles[module]} |")
    lines.extend([
        "",
        "## 6. 付费段",
        "",
        "| 付费段 | 商品 | 价格 | 可见价值 | 账号/地区 | 实际购买 |",
        "|---|---|---:|---|---|---|",
    ])
    for offer in data["offers"]:
        lines.append(f"| {offer['pay_segment']} | {offer['offer']} | {offer['price']} | {offer['visible_value']} | {offer['account']} | 否 |")
    lines.extend([
        "",
        "账号 A 展示 USD，账号 B 展示 TRY，且礼包包含 Up to/TOTAL/混合道具；因此不能跨地区直接比较单价，也不能按标称总量当即时到账。录像没有购买前后窗口，低/中/高付费体验均标为待补采。",
        "",
        "## 7. 稳定期 RTP 敏感性",
        "",
        "| 稳定期 RTP | 七日末金币余额 | 完成建造任务 |",
        "|---:|---:|---:|",
    ])
    for key, value in data["sensitivity"].items():
        lines.append(f"| {key} | {n(value['ending_coin_balance'])} | {value['build_tasks']} |")
    lines.extend([
        "",
        "95% 基线下，第 3 日末出现余额低谷，第 4–7 日反复经历“活动/大奖拉升—建造成本抽干—回 Slot”的锯齿循环；这与录像中的多次金币不足提示方向一致。90%–100% 的 10 个百分点区间只改变约 2 个建造任务，但会显著改变余额缓冲，说明短期体验对稳定期总返还高度敏感。",
        "",
        "## 8. 风险、待确认与补采",
        "",
        "1. 直给能量价、直给金币价与地区汇率均未确认；跨资源总 RTP 只能作为场景模型。",
        "2. 当前 10 秒全片抽帧足以定位模块与节点，不足以逐 Spin 还原真实命中概率；概率切片至少需连续 500 Spin。",
        "3. 录像无购买；要比较付费前后体验，需同账号购买前后各录 100/300 Spin，并记录真实到账。",
        "4. 账号 B 缺 Day1，不能与账号 A 拼成连续生命周期。",
        "5. 区域建造价格只按录像界面记账，不能拟合服务端完整成本公式。",
        "",
        "## 9. 复算",
        "",
        "```powershell",
        "python .\\数值策划\\工具\\simulate_top_tycoon_experience.py --output <json> --days 7 --daily-minutes 30 --action-seconds 3 --stable-rtp 0.95",
        "python .\\数值策划\\工具\\generate_top_tycoon_experience_report.py --input <json> --md <md> --html <html>",
        "```",
        "",
        "模型随机种子为 20260804；输入、分阶段百分点、逐 Spin 返回、建造消耗与余额均保存在 JSON 和工作簿中。",
    ])
    return "\n".join(lines) + "\n"


def html_report(data: dict[str, Any]) -> str:
    a = data["assumptions"]
    trajectory = [
        {
            "s": row["spin"], "d": row["day"], "t": row["time_in_day"],
            "b": row["coin_balance"], "x": row["bet_x"], "p": row["pay_exposure"],
            "e": row["event"], "g": row["stage"],
        }
        for row in data["trajectory"]
    ]
    traj_json = json.dumps(trajectory, ensure_ascii=False, separators=(",", ":"))
    stage_cards = []
    for stage in data["stage_results"]:
        segments = "".join(
            f'<span style="width:{value/sum(stage["target_module_points"].values())*100:.3f}%;background:{MODULE_COLORS[module]}" title="{html.escape(module)} {value:.1f}pp"></span>'
            for module, value in stage["target_module_points"].items()
        )
        rows = "".join(
            f"<tr><td>{html.escape(module)}</td><td>{value:.1f} pp</td></tr>"
            for module, value in stage["target_module_points"].items()
        )
        stage_cards.append(
            f'<article class="stage"><h3>{html.escape(stage["stage"])}</h3><div class="muted">Spin {stage["spin_range"]}</div><strong>{sum(stage["target_module_points"].values()):.1f}%</strong><div class="stack">{segments}</div><table>{rows}</table></article>'
        )
    node_rows = "".join(
        f'<tr class="{"pay" if row["pay_exposure"] else ""}"><td>{row["spin"]}</td><td>D{row["day"]} {row["time_in_day"]}</td><td>{html.escape(row["stage"])}</td><td>x{row["bet_x"]}</td><td>{n(row["coin_balance"])}</td><td>{row["build_task"]}</td><td>{html.escape(row["pay_exposure"] or "—")}</td><td>{html.escape(row["event"] or "—")}</td></tr>'
        for row in data["nodes"]
    )
    module_rows = "".join(
        f'<tr><td><i style="background:{MODULE_COLORS[module]}"></i>{html.escape(module)}</td><td>{n(value["return_coin"])}</td><td>{value["rtp_points"]:.1f} pp</td></tr>'
        for module, value in data["module_summary"].items()
    )
    offer_rows = "".join(
        f'<tr><td>{html.escape(row["pay_segment"])}</td><td>{html.escape(row["offer"])}</td><td>{html.escape(row["price"])}</td><td>{html.escape(row["visible_value"])}</td><td>{row["account"]}</td><td>未购买</td></tr>'
        for row in data["offers"]
    )
    evidence_rows = "".join(
        f'<tr><td>{html.escape(row["account"])}</td><td>{html.escape(row["video"])}</td><td>{row["time"]}</td><td>{html.escape(row["observation"])}</td></tr>'
        for row in data["evidence"]
    )
    sens_rows = "".join(
        f'<tr><td>{key}</td><td>{n(value["ending_coin_balance"])}</td><td>{value["build_tasks"]}</td></tr>'
        for key, value in data["sensitivity"].items()
    )
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Top Tycoon 数值体验报告 v0.3</title>
<style>
:root{{--bg:#07111f;--panel:#0f1d31;--panel2:#13243d;--text:#edf4ff;--muted:#9fb1ca;--cyan:#22d3ee;--red:#fb7185;--line:#233a5d}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 80% 0,#172554 0,transparent 30%),var(--bg);color:var(--text);font-family:Inter,"Microsoft YaHei",sans-serif}}main{{max-width:1420px;margin:auto;padding:32px}}h1{{font-size:38px;margin:0 0 8px}}h2{{margin:38px 0 16px;font-size:24px}}h3{{margin:0 0 6px}}p,li{{color:var(--muted);line-height:1.7}}.badge{{display:inline-block;padding:5px 10px;border:1px solid #35507a;border-radius:999px;color:#b8c7dc;margin:2px 6px 2px 0}}.warn{{border-left:4px solid #f59e0b;background:#291d0b;padding:12px 16px;border-radius:8px;color:#fde68a}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}}.card,.stage,.chartbox,.tablebox{{background:linear-gradient(145deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:16px;padding:18px;box-shadow:0 18px 45px #0004}}.card small,.muted{{color:var(--muted)}}.card strong,.stage>strong{{display:block;font-size:28px;margin-top:8px;color:#fff}}.chartbox{{position:relative;padding:14px}}canvas{{width:100%;height:430px;display:block}}#tip{{position:absolute;display:none;pointer-events:none;background:#030712eF;border:1px solid #475569;border-radius:8px;padding:9px 11px;font-size:12px;white-space:nowrap}}.stagegrid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}}.stack{{height:12px;border-radius:999px;overflow:hidden;display:flex;margin:12px 0}}.stack span{{height:100%}}table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{padding:9px 10px;border-bottom:1px solid #213653;text-align:left}}th{{color:#b9cae0;position:sticky;top:0;background:#102039}}td:nth-child(n+4){{font-variant-numeric:tabular-nums}}tr.pay{{background:#40151f}}tr.pay td:nth-child(7){{color:#fecdd3;font-weight:700}}td i{{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:8px}}.tablebox{{overflow:auto;max-height:560px}}.legend{{display:flex;flex-wrap:wrap;gap:10px;margin:10px 0 16px}}.legend span{{font-size:12px;color:#b9cae0}}.legend i{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px}}.flow{{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;align-items:center}}.flow div{{text-align:center;padding:14px;background:#11233b;border:1px solid #29456d;border-radius:12px}}.arrow{{color:var(--cyan);font-size:22px;text-align:center}}@media(max-width:900px){{main{{padding:18px}}.grid,.stagegrid{{grid-template-columns:1fr 1fr}}.flow{{grid-template-columns:1fr}}.arrow{{transform:rotate(90deg)}}}}@media(max-width:560px){{.grid,.stagegrid{{grid-template-columns:1fr}}h1{{font-size:28px}}}}
</style></head><body><main>
<span class="badge">v0.3 · 2026-08-04</span><span class="badge">5 videos · 81.4 min</span><span class="badge">0 purchase observed</span>
<h1>Top Tycoon 数值体验报告</h1><p>两账号两日录屏观察 + 七日 F2P 场景模拟。初始参数、付费口径和模型边界放在最前。</p>
<div class="warn">稳定期 95% 与 1 能量 = 5,000 金币等价值均为场景假设，不是从录像反推的服务端配置。录像没有实际购买；轨迹红点只代表付费曝光。</div>
<h2>初始参数</h2><section class="grid">
<div class="card"><small>玩家画像</small><strong>新注册 · F2P</strong><small>VIP/累计付费未知</small></div>
<div class="card"><small>初始资源</small><strong>0 金币 / 50 能量</strong><small>能量在 Slot 解锁后计</small></div>
<div class="card"><small>周期</small><strong>{a['daily_minutes']} 分 × {a['days']} 天</strong><small>{a['action_seconds']} 秒/Spin · {n(a['total_spins'])} Spin</small></div>
<div class="card"><small>稳定期总 RTP</small><strong>{a['stable_rtp']*100:.1f}%</strong><small>模块百分点横向相加</small></div>
</section>
<h2>玩法循环</h2><section class="flow"><div>教程设施 / 门票<br><b>启动资金</b></div><div class="arrow">→</div><div>建造花金币<br><b>推进区域</b></div><div class="arrow">→</div><div>金币不足<br><b>回 Slot</b></div></section><section class="flow" style="margin-top:8px"><div>Slot 花能量<br><b>金币 + 进度</b></div><div class="arrow">→</div><div>Attack / Credit Grab<br><b>离散大额奖励</b></div><div class="arrow">→</div><div>任务 / 日历 / 小游戏<br><b>补续航</b></div></section>
<h2>逐 Spin 金币余额轨迹</h2><div class="chartbox"><canvas id="chart"></canvas><div id="tip"></div></div><p>蓝线为 4,200 次逐 Spin 余额；背景分日；红点为 Chapter/Pass/资源包曝光，主轨迹未注入任何付费资源。</p>
<h2>分阶段 RTP</h2><div class="legend">{''.join(f'<span><i style="background:{color}"></i>{html.escape(module)}</span>' for module,color in MODULE_COLORS.items())}</div><section class="stagegrid">{''.join(stage_cards)}</section>
<h2>节点体验表（付费曝光行标红）</h2><div class="tablebox"><table><thead><tr><th>Spin</th><th>日/时间</th><th>阶段</th><th>BET</th><th>金币余额</th><th>建造任务</th><th>付费曝光</th><th>事件</th></tr></thead><tbody>{node_rows}</tbody></table></div>
<h2>模块单独表</h2><div class="tablebox" style="max-height:none"><table><thead><tr><th>模块</th><th>七日金币等价返还</th><th>全周期 RTP 百分点</th></tr></thead><tbody>{module_rows}</tbody></table></div>
<h2>付费段</h2><div class="tablebox"><table><thead><tr><th>段</th><th>商品</th><th>价格</th><th>可见价值</th><th>账号</th><th>实际购买</th></tr></thead><tbody>{offer_rows}</tbody></table></div><p>账号 A 为 USD，账号 B 为 TRY；Up to/TOTAL/混合礼包不可按即时到账处理，也不能直接跨地区比较。</p>
<h2>稳定期 RTP 敏感性</h2><div class="tablebox" style="max-height:none"><table><thead><tr><th>稳定期 RTP</th><th>七日末余额</th><th>完成建造任务</th></tr></thead><tbody>{sens_rows}</tbody></table></div>
<h2>录像证据索引</h2><div class="tablebox"><table><thead><tr><th>账号</th><th>视频</th><th>时间</th><th>观察</th></tr></thead><tbody>{evidence_rows}</tbody></table></div>
<h2>结论</h2><ul><li>TT 的主张力不是 Slot 单局胜负，而是“建造成本抽干—回 Slot—事件大额拉升—再建造”的锯齿循环。</li><li>BET 在前两日快速解锁到 x10，金币产出与消耗同步数量级跃迁；枯竭点始终存在。</li><li>付费商品在枯竭、Pass 领奖和小游戏之间高频曝光，但本批录像没有购买，无法判断付费后续航或概率待遇。</li><li>95% 基线下七日末约 {n(data['trajectory'][-1]['coin_balance'])} 金币、完成 {data['trajectory'][-1]['build_task']} 个建造任务；90%–100% 敏感性显著改变余额缓冲。</li></ul>
</main><script>
const data={traj_json};const c=document.getElementById('chart'),ctx=c.getContext('2d'),tip=document.getElementById('tip');let box,scaleX,scaleY,pad=48;
function draw(){{box=c.getBoundingClientRect();c.width=Math.round(box.width*devicePixelRatio);c.height=Math.round(430*devicePixelRatio);ctx.scale(devicePixelRatio,devicePixelRatio);const w=box.width,h=430,max=Math.max(...data.map(d=>d.b)),min=Math.min(...data.map(d=>d.b));scaleX=(w-pad*2)/(data.length-1);scaleY=(h-pad*1.5)/(max-min||1);ctx.clearRect(0,0,w,h);for(let day=1;day<=7;day++){{const x=pad+(day-1)*600*scaleX;ctx.fillStyle=day%2?'#0b1930':'#101f38';ctx.fillRect(x,20,600*scaleX,h-pad);ctx.fillStyle='#8ea4c1';ctx.font='12px sans-serif';ctx.fillText('D'+day,x+6,38)}}ctx.strokeStyle='#1f3657';ctx.lineWidth=1;for(let i=0;i<5;i++){{const y=20+i*(h-pad-20)/4;ctx.beginPath();ctx.moveTo(pad,y);ctx.lineTo(w-pad,y);ctx.stroke()}}ctx.beginPath();data.forEach((d,i)=>{{const x=pad+i*scaleX,y=20+(max-d.b)*scaleY;if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y)}});ctx.strokeStyle='#22d3ee';ctx.lineWidth=2;ctx.stroke();data.forEach((d,i)=>{{if(!d.p)return;const x=pad+i*scaleX,y=20+(max-d.b)*scaleY;ctx.beginPath();ctx.arc(x,y,5,0,Math.PI*2);ctx.fillStyle='#fb7185';ctx.fill();ctx.strokeStyle='#fff';ctx.stroke()}});ctx.fillStyle='#9fb1ca';ctx.font='12px sans-serif';ctx.fillText(max.toLocaleString(),6,26);ctx.fillText(min.toLocaleString(),6,h-pad+4)}}
c.addEventListener('mousemove',ev=>{{const r=c.getBoundingClientRect(),i=Math.max(0,Math.min(data.length-1,Math.round((ev.clientX-r.left-pad)/scaleX))),d=data[i];tip.style.display='block';tip.style.left=Math.min(r.width-230,ev.clientX-r.left+12)+'px';tip.style.top=Math.max(8,ev.clientY-r.top-72)+'px';tip.innerHTML=`Spin ${{d.s}} · D${{d.d}} ${{d.t}}<br>余额 ${{d.b.toLocaleString()}} · BET x${{d.x}}<br>${{d.p||d.e||d.g}}`;}});c.addEventListener('mouseleave',()=>tip.style.display='none');addEventListener('resize',draw);draw();
</script></body></html>"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成 Top Tycoon 数值体验报告")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--md", type=Path, required=True)
    parser.add_argument("--html", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    args.md.parent.mkdir(parents=True, exist_ok=True)
    args.html.parent.mkdir(parents=True, exist_ok=True)
    args.md.write_text(markdown_report(data), encoding="utf-8")
    args.html.write_text(html_report(data), encoding="utf-8")


if __name__ == "__main__":
    main()
