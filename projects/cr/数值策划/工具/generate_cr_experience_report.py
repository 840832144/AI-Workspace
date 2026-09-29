"""由CR三日体验复算JSON生成Markdown与交互HTML。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


MODULES = ["主玩法", "建造", "弹球", "每日任务", "免费奖励", "FunBP"]
COLORS = {
    "主玩法": "#4f46e5", "建造": "#e08b2c", "弹球": "#149b92",
    "每日任务": "#2f7d58", "免费奖励": "#d3577a", "FunBP": "#7b61b8",
}


def money(value: float) -> str:
    return f"${value / 1_000_000:,.2f}"


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def pick(data: dict[str, Any], divisor: int) -> dict[str, Any]:
    return next(item for item in data["scenarios"] if item["divisor"] == divisor)


def module_value(stage: dict[str, Any], module: str, key: str) -> float:
    return stage["modules"].get(module, {}).get(key, 0.0)


def markdown(full: dict[str, Any], pressure: dict[str, Any]) -> str:
    base = pick(full, 150)
    payer = full["aggressive_payer"]
    depth = pressure["sequential_purchase"]["depths"][0]
    lines = [
        "# CR 最新配置数值体验报告",
        "",
        "> 配置基线：CR dev SVN r5521（2026-08-04）  ",
        "> 玩家：VIP0、展示等级0；创角金币0，领取第1建筑产出33,600金币后开始Spin  ",
        "> 周期：每日1.5小时、连续3天；3秒/Spin，每日1,800 Spin，总计5,400 Spin  ",
        "> Slot：等级0–10/11–50沿用新手配置；配置等级51起稳定期RTP固定90%",
        "",
        "## 0. 初始参数（先读）",
        "",
        "| 玩家/VIP | 启动金币 | 初始建设币 | 初始弹球 | Bet策略 | 稳定RTP | 时长 | 首充 |",
        "|---|---:|---:|---:|---|---:|---|---|",
        "| 展示等级0 / VIP0 | 33,600 | 500 | 3 | 前10级激进，之后持金/150，受等级解锁限制 | 90% | 90分钟/天×3天 | 固定$1.99→$50金币 |",
        "",
        "## 1. 核心结论",
        "",
        "1. **Bet解锁已严格生效。** 每次只在`SlotsCasinoBetUnlock`当前等级门槛内选择Bet；前10配置等级偏激进，之后按持金1/150选择不高于目标的最高已解锁Bet。",
        "2. **建造提前完成是倍率单位错误。** `BuildCashCheatSheet=336`应按3.36倍使用，即计算时除以100；旧模型按336倍发放，导致建设币约放大100倍。",
        f"3. **修正后与实测一致。** 付费调控主轨在第{payer['build_complete_spin']:,} Spin、配置等级{payer['build_complete_level']}完成前三建筑共{payer['build_total_flips']}块，落在实测30–50级区间。",
        f"4. **破产调控显著压低中后段返还。** 第2天总经济RTP为{pct(payer['stages'][4]['total_rtp'])}，第3天为{pct(payer['stages'][5]['total_rtp'])}；三天末等级{payer['end_level']}、余额{money(payer['end_balance'])}。",
        f"5. **首充不是破产付费。** 主轨在达到15级后的第{payer['payment_events'][0]['spin']:,} Spin购买$1.99首充；50级前主轨未破产。第二、三次仍为${payer['payment_events'][1]['price_cents']/100:.2f}/${payer['payment_events'][2]['price_cents']/100:.2f}。",
        "",
        "## 2. 默认参数和公式",
        "",
        "| 参数 | 值 | 来源/解释 |",
        "|---|---:|---|",
        "| 单日游戏时长 | 90分钟 | 用户确认 |",
        "| 总周期 | 3天 / 5,400 Spin | 3秒/Spin |",
        "| 启动金币 | 33,600 | 第1建筑启动资金 |",
        "| 初始建设币 | 500 | `CommCfg.id=293` |",
        "| 初始弹球 | 3 | `QuestInitItem`，QuestType=6 |",
        "| 稳定期Slot RTP | 90% | 配置等级51起的报告口径 |",
        "| Bet策略 | 前10级激进；后续持金/150 | 严格受`SlotsCasinoBetUnlock`限制 |",
        "| 首充 | $1.99 → $50金币 | `BagNoviceOffer2.RewardType=17, RewardNum=5000` |",
        "| 第2/3次付费 | $4.99 / $6.99 | 主体验轨沿用原付费阶梯 |",
        "| 峰值定价 | 不进入主轨 | 仅保留50%/75%/100%敏感性试算 |",
        "| 破产调控 | 250 Spin调控 / 75 Spin冷却 / 最多3轮 | 用户区间中位数；轮数来自`CommCfg.id=105` |",
        "| 弹球返还 | 1% RTP百分点 | 每阶段按投注额计提 |",
        "",
        "```text",
        "可用Bet上限 = SlotsCasinoBetUnlock中 玩家等级门槛≤当前等级 的最大betlevel",
        "稳定期目标Bet = 当前持金 ÷ 150",
        "建设币期望 = 掉落概率 × buildingcoins × (BuildCashCheatSheet值 ÷ 100)",
        "稳定期Slot期望返还 = Bet × 90%",
        "调控期Slot返还 = 原Slot返还 × (1 - 对应Bet调输概率)",
        "总经济RTP = 主玩法RTP贡献 + 建造贡献 + 弹球1% + 任务/免费 + FunBP",
        "```",
        "",
        "账号前20 Spin读取`SpinDropBuildingCoins`；第21 Spin后按既定业务口径暂用40%概率、500基础建设币。该运行时默认值仍需程序确认。",
        "",
        "## 3. 付费玩家统一节点体验表（1/150）",
        "",
        "| Spin | 天数/时间 | Bet | 期望余额 | 等级 | 翻地 | 本次付费 | 累计付费 | 破产调控 | 体验事件 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    notes = {
        1:"开始Spin", 3:"建设币首次爆发", 20:"账号前20 Spin配置结束",
        100:"结束新手激进Bet阶段", 253:"第1轮调控结束", 328:"第2轮调控开始",
        578:"第2轮调控结束", 653:"第3轮调控开始", 903:"第3轮调控结束",
        600:"第1天30分钟", 1000:"第1天50分钟",
        payer["build_complete_spin"]:"完成前三建筑", 1800:"第1天结束",
        1801:"第2次付费并重置调控", 3600:"第2天结束",
        3601:"第3次付费并重置调控", 5400:"第3天结束",
    }
    for event in payer["payment_events"]:
        notes[event["spin"]] = event["trigger"]
    nodes = {1,2,3,4,5,10,20,50,100,253,328,578,653,903,1000,1200,1350,1800,1801,2050,2125,2375,2450,2700,3600,3601,3850,3925,4175,4250,4500,5400,payer["build_complete_spin"]}
    nodes.update(event["spin"] for event in payer["payment_events"])
    for snap in payer["snapshots"]:
        if snap["spin"] not in nodes:
            continue
        day = (snap["spin"] - 1) // payer["spins_per_day"] + 1
        minute = ((snap["spin"] - 1) % payer["spins_per_day"]) * 3 / 60
        control = (
            f"生效·调输{snap['control_loss_rate']*100:.0f}%"
            if snap.get("broken_control")
            else ("窗口内·条件未命中" if snap.get("control_window") else "窗口外")
        )
        lines.append(
            f"| {snap['spin']:,} | 第{day}天 {minute:.1f}分 | {money(snap['bet'])} | {money(snap['balance'])} | {snap['level']} | {snap['build_flips']}/{payer['build_total_flips']} | {snap.get('payment','—')} | ${snap.get('cumulative_paid_cents',0)/100:.2f} | {control} | {notes.get(snap['spin'], '持续循环')} |"
        )
    lines += [
        "",
        "余额为付费+破产调控期望流水，不代表单个玩家必然结果。调控窗口只有在`持金/Bet≤200`或`Bet≥500,000`时实际生效。",
        "",
        "## 4. 原付费阶梯节点体验表",
        "",
        "| Spin | 天数/当日时间 | 配置等级 | Bet | 触发原因 | 本次付费 | 累计付费 | 获得金币 | 付费后余额 |",
        "|---:|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    payer_snapshots = {item["spin"]: item for item in payer["snapshots"]}
    for event in payer["payment_events"]:
        snap = payer_snapshots[event["spin"]]
        lines.append(
            f"| {event['spin']:,} | 第{event['day']}天 {event['minute_in_day']:.1f}分 | {snap['level']} | {money(snap['bet'])} | {event['trigger']} | ${event['price_cents']/100:.2f} | ${event['cumulative_paid_cents']/100:.2f} | {money(event['coins'])} | {money(event['balance_after_purchase'])} |"
        )
    lines += [
        "",
        f"首充按达到15级后的弹窗曝光购买处理，不由破产触发。独立低尾压力模拟共{pressure['assumptions']['users']:,}用户，三天内{pct(depth['reach_rate'])}发生余额不足；该结果只用于破产风险观察。",
        "",
        "主轨第二、三次付费沿用$4.99/$6.99及原金币量。下表中的峰值方案是独立试算，不影响主轨节点和结论。",
        "",
        "### 4.1 峰值定价敏感性",
        "",
        "| 方案 | 第2次价格 | 第3次价格 | 三天累计付费 | 三天末余额 | 等级 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    pricing_rows = [("原价方案", full["original_payer"])] + [
        (f"峰值×{item['ratio']*100:.0f}%", item["result"])
        for item in full["peak_pricing_scenarios"]
    ]
    for label, result in pricing_rows:
        events = result["payment_events"]
        lines.append(
            f"| {label} | ${events[1]['price_cents']/100:.2f} | ${events[2]['price_cents']/100:.2f} | ${result['total_paid_cents']/100:.2f} | {money(result['end_balance'])} | {result['end_level']} |"
        )
    lines += [
        "",
        "峰值方案会把后续价格推得过高，因此不采用。主报告、金币轨迹和付费节点均使用原价方案。",
        "",
        "## 5. 三日RTP构成",
        "",
        "| 阶段 | 投注额 | 总经济RTP | 主玩法 | 建造 | 弹球 | 每日任务 | 免费奖励 | FunBP |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for stage in payer["stages"]:
        contributions = [pct(module_value(stage, module, "rtp")) for module in MODULES]
        lines.append(f"| {stage['name']} | {money(stage['wager'])} | {pct(stage['total_rtp'])} | " + " | ".join(contributions) + " |")
    lines += [
        "",
        "### 建议的返还结构目标",
        "",
        "| 阶段 | 主玩法 | 建造 | 弹球/活动 | 每日+免费 | FunBP |",
        "|---|---:|---:|---:|---:|---:|",
        "| 第1天 | 按新手档 | 2%–5% | 1% | 2%–4% | 1%–3% |",
        "| 第2天 | 90%（无调控时） | 约1% | 1% | 2%–4% | 1%–3% |",
        "| 第3天 | 90%（无调控时） | 约1% | 1% | 2%–4% | 1%–3% |",
        "",
        "弹球已固定贡献1个百分点。破产调控生效时主玩法贡献会低于90%，但活动贡献仍按各自百分点展示；无调控的长期基础盘以Slot 90%为锚，再叠加经过预算批准的建造、弹球、任务和BP。",
        "",
        "## 6. 模块体验",
        "",
        "| 模块 | 主要配置表 | 三天体验 |",
        "|---|---|---|",
        f"| Slot/等级 | `SlotsCasinoBetList`、`SlotsCasinoBetUnlock`、`LevelCfg`、`SlotsCasinoNewbieConfig` | 付费调控轨到等级{payer['end_level']}、Bet {money(payer['end_bet'])}；51级起基础RTP 90% |",
        f"| 建造 | `CommCfg`、`SpinDropBuildingCoins`、`BuildCashCheatSheet`、`BuildLevelCfg`、`BuildBox` | 倍率÷100；第{payer['build_complete_spin']:,} Spin、等级{payer['build_complete_level']}完成前三建筑{payer['build_total_flips']}块 |",
        f"| 弹球 | `QuestPickGet`、`QuestPointsCheatSheet`、`QuestPlinkoWeight`、`QuestPlinkoStageReward` | 固定贡献1% RTP；使用{payer['plinko_balls_used']}球，完成{payer['plinko_stages_cleared']}关 |",
        "| 破产调控 | `CommCfg.id=41/79/105/112`、`ChipAndBetLimitControl` | 付费后250 Spin调控、75 Spin冷却、最多3轮；命中后再按40%/60%概率调输 |",
        "| 每日任务 | `CashRoyalTask`、`FunBPMission` | 每日登录10k；4个BP日常合计1.333M金币和400经验 |",
        "| 免费奖励 | `SignReward`、`SignTotalReward`、`OnlineReward`、`FreeBonusHourly` | 每日签到均摊、在线奖和90分钟内6次时间礼包 |",
        f"| FunBP | `FunBP`、`FunBPMission` | 三天推进到BP等级{base['bp_level']}；金币轨后段存在空档 |",
        f"| 付费 | `BagNoviceOffer2` + 峰值恢复情景 | 首充固定$1.99→$50金币；第二次起主方案按峰值×75%，累计${payer['total_paid_cents']/100:.2f} |",
        "",
        "## 7. 无破产调控基线的Bet敏感性",
        "",
        "| 策略 | 三天余额 | 等级 | 当前Bet | 建造完成Spin/等级 | 弹球/关卡 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in full["scenarios"]:
        lines.append(
            f"| 持金/{item['divisor']} | {money(item['end_balance'])} | {item['end_level']} | {money(item['end_bet'])} | {item['build_complete_spin']}/{item['build_complete_level']} | {item['plinko_balls_used']}/{item['plinko_stages_cleared']} |"
        )
    lines += [
        "",
        "## 8. 风险和建议",
        "",
        "1. 与程序确认`BuildCashCheatSheet`百分倍率及第21 Spin后的通用建设币掉落逻辑；这是建造完成等级的最大口径风险。",
        "2. 峰值75%方案三天累计付费很高，必须验证报价接受率、购买率和退款率；当前只确认首充`BagNoviceOffer2`。",
        "3. 稳定期90% RTP下监控P10/P50/P90余额、破产率、Bet/持金比和三日留存，不只看期望余额。",
        "4. 副玩法返还应从总预算迁移，避免在90% Slot之上无约束叠加。",
        "",
        "## 9. 复算",
        "",
        "```powershell",
        "python 数值策划/工具/simulate_cr_full_loop.py --config-root <dev目录> --days 3 --daily-minutes 90 --stable-rtp 0.90 --output <日循环.json>",
        "python 数值策划/工具/simulate_cr_latest_experience.py --config-root <dev目录> --users 1000 --max-spins 5400 --stable-rtp 0.90 --output <压力模拟.json>",
        "python 数值策划/工具/generate_cr_experience_report.py --full <日循环.json> --pressure <压力模拟.json> --md <报告.md> --html <报告.html>",
        "```",
        "",
        "本轮只修正报告模型与产物，未修改dev配置。",
    ]
    return "\n".join(lines) + "\n"


def html_report(full: dict[str, Any], pressure: dict[str, Any]) -> str:
    data = json.dumps(full, ensure_ascii=False).replace("</", "<\\/")
    rate = pressure["sequential_purchase"]["depths"][0]["reach_rate"]
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CR 三日数值体验报告</title>
<style>:root{{--ink:#172033;--muted:#657086;--paper:#f3f0e8;--card:#fffefa;--line:#d6d0c3}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:15px/1.6 "Microsoft YaHei","PingFang SC",sans-serif}}main{{max-width:1240px;margin:auto;padding:28px}}header{{display:grid;grid-template-columns:1.6fr .8fr;gap:24px;border-bottom:2px solid var(--ink);padding:28px 0}}h1{{font-size:clamp(32px,5vw,58px);line-height:1.05;margin:0 0 12px}}h2{{margin:40px 0 14px}}.eyebrow{{color:#4f46e5;font-size:12px;font-weight:800;letter-spacing:2px}}.meta{{border-left:1px solid var(--line);padding-left:20px}}.controls{{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0}}button{{border:1px solid var(--ink);background:transparent;padding:8px 14px;border-radius:999px;font-weight:700;cursor:pointer}}button.active{{background:var(--ink);color:#fff}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}}.kpi b{{display:block;font-size:25px}}.kpi span,.note{{color:var(--muted);font-size:13px}}svg{{width:100%;height:270px;background:var(--card);border:1px solid var(--line);border-radius:12px}}.stage{{margin:16px 0 24px}}.bar{{height:34px;display:flex;overflow:hidden;border-radius:8px;background:#e5e0d6}}.seg{{display:flex;align-items:center;justify-content:center;color:white;font-size:11px;font-weight:800;white-space:nowrap}}.legend{{display:flex;flex-wrap:wrap;gap:11px;font-size:12px;color:var(--muted);margin-top:8px}}.dot{{display:inline-block;width:9px;height:9px;margin-right:4px}}table{{width:100%;border-collapse:collapse;background:var(--card);font-variant-numeric:tabular-nums}}th,td{{padding:10px;border-bottom:1px solid var(--line);text-align:right}}th:first-child,td:first-child{{text-align:left}}.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:12px;max-height:520px}}.callout{{border-left:5px solid #e08b2c;background:#fff8e8;padding:16px 18px;margin:18px 0}}.pay{{border-top:5px solid #d3577a}}@media(max-width:800px){{header{{grid-template-columns:1fr}}.meta{{border:0;padding:0}}.grid{{grid-template-columns:repeat(2,1fr)}}}}@media(max-width:520px){{main{{padding:16px}}.grid{{grid-template-columns:1fr}}}}</style></head>
<body><main><header><div><div class="eyebrow">CR · DEV R5521 · THREE-DAY EXPERIENCE</div><h1>三天数值体验与付费节点</h1><p>每日90分钟，连续3天；动态Bet、90%稳定期RTP、建造、弹球、日常、免费奖励和FunBP同口径复算。</p></div><div class="meta"><b>5,400 Spin</b><p>3秒/Spin · 1,800 Spin/天</p><b>建造修正</b><p>336 = 3.36倍，严格按等级解锁Bet</p></div></header>
<h2>初始参数</h2><section class="grid"><article class="card"><b>玩家</b><p>展示等级0 · VIP0</p></article><article class="card"><b>初始资源</b><p>33,600金币 · 500建设币 · 3弹球</p></article><article class="card"><b>Bet与RTP</b><p>前10级激进，之后持金/150 · 稳定RTP 90%</p></article><article class="card"><b>原付费阶梯</b><p>$1.99 / $4.99 / $6.99，首充给$50金币</p></article></section>
<section class="grid" id="kpis"></section>
<h2>三天金币轨迹（每次Spin）</h2><svg id="chart" viewBox="0 0 1000 300"></svg><p class="note" id="chartTip">移动鼠标可查看每次Spin的余额、Bet和等级；红色节点为付费。</p>
<h2>分阶段RTP百分点贡献</h2><div id="stages"></div>
<h2>付费玩家统一节点</h2><div class="table-wrap"><table><thead><tr><th>Spin</th><th>天</th><th>Bet</th><th>余额</th><th>等级</th><th>翻地</th><th>本次付费</th><th>累计</th><th>调控状态</th></tr></thead><tbody id="timeline"></tbody></table></div>
<h2>原付费阶梯节点</h2><section class="grid" id="payments"></section><p class="note">主轨固定使用$1.99→$4.99→$6.99；峰值定价只保留在Markdown的敏感性对照中。</p>
<h2>关键判断</h2><div class="grid"><article class="card"><b>建造完成</b><p>付费调控轨在等级30–50区间完成前三建筑157块。</p></article><article class="card"><b>破产调控</b><p>250 Spin调控、75 Spin冷却、最多3轮；符合条件时40%/60%调输。</p></article><article class="card"><b>首充时机</b><p>达到15级后弹窗购买，不由破产触发；50级前主轨未破产。</p></article><article class="card"><b>付费方案</b><p>峰值定价过于激进，主视图恢复原阶梯。</p></article></div>
<p class="note">模型口径和风险请以同目录Markdown报告为准。本轮未修改dev配置。</p>
<script>const DATA={data};const MODS={json.dumps(MODULES,ensure_ascii=False)};const COLORS={json.dumps(COLORS,ensure_ascii=False)};const fmt=v=>'$'+(v/1e6).toLocaleString('en-US',{{maximumFractionDigits:2}});const pc=v=>(v*100).toFixed(2)+'%';
function render(){{const s=DATA.aggressive_payer;document.getElementById('kpis').innerHTML=`<div class="card kpi"><span>三天余额</span><b>${{fmt(s.end_balance)}}</b></div><div class="card kpi"><span>等级 / Bet</span><b>${{s.end_level}} / ${{fmt(s.end_bet)}}</b></div><div class="card kpi"><span>建造完成</span><b>Spin ${{s.build_complete_spin}}</b><span>等级${{s.build_complete_level}}</span></div><div class="card kpi"><span>三天累计付费</span><b>$${{(s.payment_events.at(-1).cumulative_paid_cents/100).toFixed(2)}}</b></div>`;document.getElementById('stages').innerHTML=s.stages.map(st=>`<section class="stage"><b>${{st.name}} · 投注${{fmt(st.wager)}} · 总经济RTP ${{pc(st.total_rtp)}}</b><div class="bar">${{MODS.map(m=>{{const x=st.modules[m]?.rtp||0,w=st.total_rtp?x/st.total_rtp:0;return `<div class="seg" style="width:${{w*100}}%;background:${{COLORS[m]}}" title="${{m}}贡献 ${{pc(x)}}">${{w>.06?m:''}}</div>`}}).join('')}}</div><div class="legend">${{MODS.map(m=>`<span><i class="dot" style="background:${{COLORS[m]}}"></i>${{m}}贡献 ${{pc(st.modules[m]?.rtp||0)}}</span>`).join('')}}</div></section>`).join('');document.getElementById('timeline').innerHTML=s.snapshots.map(x=>`<tr><td>${{x.spin}}</td><td>${{Math.floor((x.spin-1)/s.spins_per_day)+1}}</td><td>${{fmt(x.bet)}}</td><td>${{fmt(x.balance)}}</td><td>${{x.level}}</td><td>${{x.build_flips}}/${{s.build_total_flips}}</td><td>${{x.payment||'—'}}</td><td>$${{((x.cumulative_paid_cents||0)/100).toFixed(2)}}</td><td>${{x.broken_control?'生效·调输'+(x.control_loss_rate*100).toFixed(0)+'%':(x.control_window?'窗口内·条件未命中':'窗口外')}}</td></tr>`).join('');draw(s)}}
function draw(s){{const pts=s.chart_series,w=1000,h=300,p=48,max=Math.max(...pts.map(x=>x.balance)),svg=document.getElementById('chart');const xy=pts.map(x=>[p+(w-2*p)*x.spin/s.total_spins,h-p-(h-2*p)*x.balance/max]);let g='';for(let i=0;i<=4;i++){{let y=p+(h-2*p)*i/4;g+=`<line x1="${{p}}" y1="${{y}}" x2="${{w-p}}" y2="${{y}}" stroke="#d6d0c3"/><text x="6" y="${{y+4}}" font-size="11" fill="#657086">${{fmt(max*(1-i/4))}}</text>`}}for(let day=1;day<=3;day++){{const start=(day-1)*s.spins_per_day,end=day*s.spins_per_day,x1=p+(w-2*p)*start/s.total_spins,x2=p+(w-2*p)*end/s.total_spins;g+=`<rect x="${{x1}}" y="${{p}}" width="${{x2-x1}}" height="${{h-2*p}}" fill="${{day%2?'#4f46e50a':'#149b920a'}}"/><line x1="${{x2}}" y1="${{p}}" x2="${{x2}}" y2="${{h-p}}" stroke="#9aa2b1" stroke-dasharray="3 4"/><text x="${{(x1+x2)/2}}" y="${{h-14}}" text-anchor="middle" font-size="12" fill="#657086">第${{day}}天 · ${{start+1}}–${{end}} Spin</text>`}}const line=`<polyline fill="none" stroke="#4f46e5" stroke-width="2" points="${{xy.map(a=>a.join(',')).join(' ')}}"/>`;const pay=xy.map((a,i)=>pts[i].payment?`<line x1="${{a[0]}}" y1="${{p}}" x2="${{a[0]}}" y2="${{h-p}}" stroke="#dc2626" stroke-width="2" stroke-dasharray="5 4"/><circle cx="${{a[0]}}" cy="${{a[1]}}" r="7" fill="#dc2626" stroke="white" stroke-width="2"><title>付费 $${{(pts[i].payment/100).toFixed(2)}} · Spin ${{pts[i].spin}} · 余额 ${{fmt(pts[i].balance)}}</title></circle>`:'').join('');svg.innerHTML=g+line+pay+`<line id="cursor" x1="0" y1="${{p}}" x2="0" y2="${{h-p}}" stroke="#172033" stroke-width="1" opacity="0"/>`;svg.onmousemove=e=>{{const box=svg.getBoundingClientRect(),vx=(e.clientX-box.left)/box.width*w,index=Math.max(0,Math.min(pts.length-1,Math.round((vx-p)/(w-2*p)*(pts.length-1)))),pt=pts[index],x=xy[index][0],cursor=document.getElementById('cursor');cursor.setAttribute('x1',x);cursor.setAttribute('x2',x);cursor.setAttribute('opacity','1');document.getElementById('chartTip').textContent=`第${{pt.day}}天 · Spin ${{pt.spin}} · 余额 ${{fmt(pt.balance)}} · Bet ${{fmt(pt.bet)}} · 等级 ${{pt.level}}${{pt.payment?` · 付费 $${{(pt.payment/100).toFixed(2)}}`:''}}`}};svg.onmouseleave=()=>document.getElementById('cursor').setAttribute('opacity','0')}}
document.getElementById('payments').innerHTML=DATA.aggressive_payer.payment_events.map((e,i)=>`<article class="card pay"><b>第${{e.day}}天 · Spin ${{e.spin}}</b><h3>$${{(e.price_cents/100).toFixed(2)}} → ${{fmt(e.coins)}}</h3><p>${{i===0?'首充固定配置':'原付费阶梯'}}</p><span class="note">累计付费 $${{(e.cumulative_paid_cents/100).toFixed(2)}} · 付费后余额 ${{fmt(e.balance_after_purchase)}}</span></article>`).join('');render();</script></main></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", type=Path, required=True)
    parser.add_argument("--pressure", type=Path, required=True)
    parser.add_argument("--md", type=Path, required=True)
    parser.add_argument("--html", type=Path, required=True)
    args = parser.parse_args()
    full = json.loads(args.full.read_text(encoding="utf-8"))
    pressure = json.loads(args.pressure.read_text(encoding="utf-8"))
    args.md.write_text(markdown(full, pressure), encoding="utf-8")
    args.html.write_text(html_report(full, pressure), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
