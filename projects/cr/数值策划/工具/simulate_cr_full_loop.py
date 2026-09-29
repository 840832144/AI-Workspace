"""模拟动态Bet下的Slot、建造、弹球、每日任务、免费奖励与FunBP日循环。"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from simulate_cr_latest_experience import (
    LevelState,
    advance,
    build_coefficient,
    effective_rtp,
    load_config,
    policy_bet_level,
)
from simulate_new_user_spin import data_rows, integer


COINS_PER_USD = 1_000_000
COINS_PER_CENT = COINS_PER_USD // 100
COINS_PER_MILLI_USD = COINS_PER_USD // 1_000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config-root",
        type=Path,
        required=True,
        help="目标 dev 或 trunk 的 ExcelConfigExport/Excel 目录。",
    )
    parser.add_argument("--revision", default="未记录")
    parser.add_argument("--days", type=int, default=3)
    parser.add_argument("--daily-minutes", type=int, default=90)
    parser.add_argument("--spin-seconds", type=int, default=3)
    parser.add_argument("--start-coins", type=int, default=33_600)
    parser.add_argument("--aggressive-until-level", type=int, default=10)
    parser.add_argument("--stable-rtp", type=float, default=0.90)
    parser.add_argument("--stable-after-level", type=int, default=50)
    parser.add_argument("--plinko-rtp", type=float, default=0.01)
    parser.add_argument("--control-active-spins", type=int, default=250)
    parser.add_argument("--control-cooldown-spins", type=int, default=75)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def module_rows(root: Path) -> dict[str, list[list[object]]]:
    files = {
        "plinko_frame": ("QuestPlinkoFramePoints.xlsx", "Sheet1"),
        "plinko_weight": ("QuestPlinkoWeight.xlsx", "Sheet1"),
        "plinko_stage": ("QuestPlinkoStageReward.xlsx", "Sheet1"),
        "quest_pick": ("QuestPickGet.xlsx", "Sheet1"),
        "quest_cheat": ("QuestPointsCheatSheet.xlsx", "Sheet1"),
        "quest_level": ("QuestGetLevel.xlsx", "Sheet1"),
        "quest_init": ("QuestInitItem.xlsx", "Sheet1"),
        "cash_task": ("CashRoyalTask.xlsx", "Sheet1"),
        "hourly": ("FreeBonusHourly.xlsx", "Sheet1"),
        "hourly_multi": ("FreeBonusMultiplier.xlsx", "Sheet1"),
        "wheel": ("FreeBonusWheel.xlsx", "Sheet1"),
        "online": ("OnlineReward.xlsx", "reward"),
        "sign": ("SignReward.xlsx", "Sheet1"),
        "sign_total": ("SignTotalReward.xlsx", "Sheet1"),
        "funbp": ("FunBP.xlsx", "Sheet1"),
        "funbp_mission": ("FunBPMission.xlsx", "Sheet1"),
        "build": ("BuildLevelCfg.xlsx", "Sheet1"),
        "build_box": ("BuildBox.xlsx", "Sheet1"),
        "honor": ("BuildHonorLevel.xlsx", "Sheet1"),
    }
    return {name: data_rows(root / filename, sheet) for name, (filename, sheet) in files.items()}


def plinko_inputs(rows: dict[str, list[list[object]]]) -> dict[str, Any]:
    frame_points = [integer(value) for value in rows["plinko_frame"][0][2:15]]
    point_by_stage: dict[int, float] = {}
    for stage in range(8):
        variants = [row for row in rows["plinko_weight"] if integer(row[1]) == stage]
        if not variants:
            # 配置当前只覆盖到第6段；后续关卡沿用最后一段的期望落点。
            point_by_stage[stage] = point_by_stage.get(stage - 1, 0.0)
            continue
        outer_weight = sum(integer(row[17]) for row in variants)
        expected = 0.0
        for row in variants:
            weights = [integer(value) for value in row[2:15]]
            score = sum(w * p for w, p in zip(weights, frame_points)) / sum(weights)
            ball_count = max(1, integer(row[15]))
            double_factor = 1 + integer(row[16]) / 100
            expected += score * ball_count * double_factor * integer(row[17]) / outer_weight
        point_by_stage[stage] = expected
    # StageId=0是第一轮；LevelId=-1是轮次额外奖励，不并入逐关主线。
    stages = [
        {"points": integer(row[3]), "reward_cents": integer(row[9])}
        for row in rows["plinko_stage"]
        if integer(row[0]) == 0 and row[1] is not None and integer(row[1]) >= 0
    ]
    pick = {
        integer(row[4]): {"id": integer(row[0]), "probability": integer(row[5]) / 1_000}
        for row in rows["quest_pick"]
        if integer(row[1]) == 6 and integer(row[3]) == 2
    }
    cheat: dict[tuple[int, int], int] = {}
    for row in rows["quest_cheat"]:
        if integer(row[0]) == 6:
            cheat[(integer(row[1]), integer(row[2]))] = integer(row[3])
    ball_threshold = next(
        (integer(row[2]) for row in rows["quest_level"] if integer(row[1]) == 6), 150
    )
    initial_balls = next(
        (integer(row[2]) for row in rows["quest_init"] if integer(row[0]) == 6), 0
    )
    return {
        "points": point_by_stage,
        "stages": stages,
        "pick": pick,
        "cheat": cheat,
        "ball_threshold": ball_threshold,
        "initial_balls": initial_balls,
    }


def nearest_cheat(inputs: dict[str, Any], pick_id: int, level: int) -> int:
    candidates = [
        (gate, value)
        for (configured_id, gate), value in inputs["cheat"].items()
        if configured_id == pick_id and gate <= level
    ]
    return max(candidates, default=(0, 0))[1]


def free_inputs(rows: dict[str, list[list[object]]]) -> dict[str, Any]:
    sign_daily_cents = (
        sum(integer(row[3]) for row in rows["sign"]) / 7
        + sum(integer(row[3]) for row in rows["sign_total"]) / 30
    )
    hourly_weighted: dict[int, float] = {}
    for gift_type in (1, 2):
        choices = [
            row
            for row in rows["hourly"]
            if integer(row[0]) == gift_type and integer(row[5]) > 0
        ]
        hourly_weighted[gift_type] = sum(
            integer(row[3]) * integer(row[5]) for row in choices
        ) / sum(integer(row[5]) for row in choices)
    wheel = [
        row for row in rows["wheel"] if integer(row[0]) == 1 and integer(row[1]) == 1
    ]
    wheel_multiplier = sum(integer(row[3]) * integer(row[5]) for row in wheel) / sum(
        integer(row[5]) for row in wheel
    ) / 100
    multipliers = sorted(
        (integer(row[2]), integer(row[1]))
        for row in rows["hourly_multi"]
        if integer(row[0]) == 1
    )
    online = {integer(row[2]) // 3: integer(row[1]) for row in rows["online"]}
    daily_login = sum(
        integer(row[7])
        for row in rows["cash_task"]
        if integer(row[3]) == 1 and integer(row[4]) == 7
    )
    return {
        "sign_daily_coins": sign_daily_cents * COINS_PER_CENT,
        "hourly_raw": hourly_weighted[1],
        "wheel_multiplier": wheel_multiplier,
        "multipliers": multipliers,
        "online": online,
        "daily_login": daily_login,
    }


def bp_inputs(rows: dict[str, list[list[object]]]) -> dict[str, Any]:
    missions = [
        row
        for row in rows["funbp_mission"]
        if integer(row[0]) == 0 and integer(row[1]) == 0 and integer(row[2]) == 2
    ]
    # 四个任务按体验进程分布到100/300/600/1000 Spin。
    schedule = []
    for spin, row in zip((100, 300, 600, 1_000), missions):
        schedule.append(
            {
                "spin": spin,
                "exp": integer(row[8]),
                "coins": integer(row[12]) if integer(row[10]) == 1 else 0,
            }
        )
    levels = []
    for row in rows["funbp"]:
        if len(row) < 15 or not isinstance(row[0], (int, float)):
            continue
        free_coins = integer(row[7]) * COINS_PER_CENT if integer(row[5]) == 17 else 0
        paid_coins = sum(
            integer(row[offset + 2]) * COINS_PER_CENT
            for offset in (8, 11)
            if integer(row[offset]) == 17
        )
        levels.append(
            {"need": integer(row[1]), "free_coins": free_coins, "paid_coins": paid_coins}
        )
    return {"missions": schedule, "levels": levels}


def build_inputs(rows: dict[str, list[list[object]]]) -> dict[str, Any]:
    build = [
        {
            "chapter": integer(row[0]), "cost": integer(row[2]),
            "honor": integer(row[3]),
        }
        for row in rows["build"]
        if row and isinstance(row[0], (int, float)) and integer(row[0]) <= 3
    ]
    totals: dict[int, int] = defaultdict(int)
    for row in build:
        totals[row["chapter"]] += 1
    box = {integer(row[0]): row for row in rows["build_box"] if row and row[0] is not None}
    honor = [
        {"need": integer(row[1]), "reward_cents": integer(row[5]) if integer(row[3]) == 17 else 0}
        for row in rows["honor"] if row and row[0] is not None
    ]
    return {"rows": build, "totals": dict(totals), "box": box, "honor": honor}


def simulate(
    root: Path, divisor: int, args: argparse.Namespace,
    payment_schedule: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    config = load_config(root)
    rows = module_rows(root)
    plinko = plinko_inputs(rows)
    free = free_inputs(rows)
    bp = bp_inputs(rows)
    build = build_inputs(rows)
    spins_per_day = args.daily_minutes * 60 // args.spin_seconds
    total_spins = spins_per_day * args.days
    stages = [
        {"name": "第1天·新手 1–100", "start": 1, "end": 100},
        {"name": "第1天·前段 101–600", "start": 101, "end": 600},
        {"name": "第1天·中段 601–1200", "start": 601, "end": 1_200},
        {"name": "第1天·后段 1201–1800", "start": 1_201, "end": 1_800},
        {"name": "第2天", "start": 1_801, "end": 3_600},
        {"name": "第3天", "start": 3_601, "end": 5_400},
    ]
    buckets = [{"wager": 0.0, "returns": defaultdict(float)} for _ in stages]

    def bucket(spin: int) -> dict[str, Any]:
        return next(item for item, stage in zip(buckets, stages) if stage["start"] <= spin <= stage["end"])

    state = LevelState()
    balance = float(args.start_coins)
    # 签到按7日均值+月累计均摊；登录日常任务在Spin前领取，记入第一阶段。
    start_free = free["sign_daily_coins"]
    start_daily = free["daily_login"]
    balance += start_free + start_daily
    buckets[0]["returns"]["免费奖励"] += start_free
    buckets[0]["returns"]["每日任务"] += start_daily

    build_cash = float(config["initial_build_cash"])
    build_index = 0
    build_complete_spin = None
    build_complete_level = None
    build_chapter_done: dict[int, int] = defaultdict(int)
    honor_points = 20
    honor_level = 0
    honor_rewards = build["honor"]

    plinko_stage = 0
    plinko_score = 0.0
    plinko_ball_progress = float(plinko["initial_balls"])
    plinko_balls_used = 0
    plinko_stages_cleared = 0
    plinko_config_reward_coins = 0.0

    bp_exp = 0
    bp_level = 0
    snapshots = []
    payment_events = []
    cumulative_paid_cents = 0
    recent_balance_peak = balance
    chart_series = []
    payments_by_spin = {
        integer(item["spin"]): item
        for item in (payment_schedule or []) if item.get("spin") is not None
    }
    payments_by_level = sorted(
        [item for item in (payment_schedule or []) if item.get("level") is not None],
        key=lambda item: integer(item["level"]),
    )
    pressure_payments = [
        item for item in (payment_schedule or [])
        if item.get("spin") is None and item.get("level") is None
    ]
    control_active_remaining = 0
    control_cooldown_remaining = 0
    control_round = 0
    control_events = []

    def apply_payment(payment: dict[str, Any], spin: int) -> None:
        nonlocal balance, cumulative_paid_cents
        nonlocal recent_balance_peak
        nonlocal control_active_remaining, control_cooldown_remaining, control_round
        original_price_cents = integer(payment["price_cents"])
        original_coins = float(payment["coins"])
        peak_ratio = payment.get("peak_ratio")
        price_cents = original_price_cents
        coins = original_coins
        peak_price_cents = None
        if peak_ratio is not None:
            peak_price_cents = int(round(recent_balance_peak / COINS_PER_USD * peak_ratio * 100))
            price_cents = max(original_price_cents, peak_price_cents)
            coins = max(original_coins, recent_balance_peak)
        balance += coins
        cumulative_paid_cents += price_cents
        control_active_remaining = args.control_active_spins
        control_cooldown_remaining = 0
        control_round = 1
        payment_events.append(
            {
                **payment,
                "price_cents": price_cents,
                "coins": coins,
                "spin": spin,
                "day": (spin - 1) // spins_per_day + 1,
                "minute_in_day": ((spin - 1) % spins_per_day) * args.spin_seconds / 60,
                "cumulative_paid_cents": cumulative_paid_cents,
                "balance_after_purchase": balance,
                "recent_peak_coins": recent_balance_peak,
                "recent_peak_usd": recent_balance_peak / COINS_PER_USD,
                "peak_price_cents": peak_price_cents,
                "used_original_floor": price_cents == original_price_cents,
            }
        )
        control_events.append(
            {"spin": spin, "event": "进入调控", "round": 1, "source": payment["package"]}
        )
        recent_balance_peak = balance

    def grant_build_rewards(target: dict[str, Any], row: dict[str, int]) -> None:
        nonlocal honor_points, honor_level
        chapter = row["chapter"]
        build_chapter_done[chapter] += 1
        done = build_chapter_done[chapter]
        total = build["totals"][chapter]
        previous = (done - 1) / total * 100
        current = done / total * 100
        cents = 0.0
        # BuildBox 20%、40%、65%、完成节点；功能区数量未知，100%按每章一次保守估计。
        for threshold, box_id in ((20, 4), (40, 5), (65, 1), (100, 2)):
            if previous < threshold <= current:
                cents += integer(build["box"][box_id][10])
        if 55 <= current <= 75:
            cents += integer(build["box"][3][6]) / 100 * integer(build["box"][3][10])
        cents += integer(build["box"][6][6]) / 100 * integer(build["box"][6][10])
        honor_points += row["honor"]
        while honor_level < len(honor_rewards) and honor_points >= honor_rewards[honor_level]["need"]:
            honor_points -= honor_rewards[honor_level]["need"]
            cents += honor_rewards[honor_level]["reward_cents"]
            honor_level += 1
        coins = cents * COINS_PER_CENT
        balance_add[0] += coins
        target["returns"]["建造"] += coins

    # 用可变容器让嵌套函数向余额回写。
    balance_add = [0.0]
    while build_index < len(build["rows"]) and build_cash >= build["rows"][build_index]["cost"]:
        build_cash -= build["rows"][build_index]["cost"]
        grant_build_rewards(buckets[0], build["rows"][build_index])
        build_index += 1
    balance += balance_add[0]
    balance_add[0] = 0

    for spin in range(1, total_spins + 1):
        target = bucket(spin)
        paid_this_spin = False
        current_level = state.level
        while payments_by_level and current_level >= integer(payments_by_level[0]["level"]):
            apply_payment(payments_by_level.pop(0), spin)
            paid_this_spin = True
        if spin in payments_by_spin:
            apply_payment(payments_by_spin[spin], spin)
            paid_this_spin = True
        target_bet = policy_bet_level(
            config, current_level, balance, divisor, args.aggressive_until_level
        )
        if target_bet == 0 and pressure_payments:
            payment = pressure_payments.pop(0)
            payment["trigger"] = "余额不足最低Bet，触发下一档付费"
            apply_payment(payment, spin)
            paid_this_spin = True
            target_bet = policy_bet_level(
                config, current_level, balance, divisor, args.aggressive_until_level
            )
        if target_bet == 0:
            snapshots.append({"spin": spin, "bankrupt": True, "level": current_level, "balance": balance})
            break
        bet = config["bets"][target_bet]["bet"]
        rtp = effective_rtp(
            config, current_level, args.stable_rtp, args.stable_after_level
        )
        target["wager"] += bet
        chip_bet_ratio = balance / bet if bet else 0
        control_eligible = (
            integer(config["comm"].get(41, 0)) == 1
            and control_active_remaining > 0
            and not (
                chip_bet_ratio > integer(config["comm"].get(79, 200))
                and bet < integer(config["comm"].get(112, 500_000))
            )
        )
        control_loss_rate = 0.0
        if control_eligible:
            eligible_rates = [
                rate for threshold, rate in config["control_loss_rates"]
                if threshold <= bet
            ]
            control_loss_rate = eligible_rates[-1] if eligible_rates else 0.0
        slot_win = bet * rtp * (1 - control_loss_rate)
        target["returns"]["主玩法"] += slot_win
        balance += slot_win - bet
        plinko_return = bet * args.plinko_rtp
        balance += plinko_return
        target["returns"]["弹球"] += plinko_return
        level_reward = advance(config, state, target_bet)
        balance += level_reward
        target["returns"]["主玩法"] += level_reward

        day_spin = (spin - 1) % spins_per_day + 1
        drop = config["drops"].get(spin)
        probability = drop["probability"] if drop else 0.40
        base = drop["base"] if drop else 500
        # BuildCashCheatSheet为百分倍率整数，336表示3.36倍；此前漏除100导致过早翻完。
        build_cash += (
            probability * base
            * build_coefficient(config, target_bet, current_level) / 100
        )
        while build_index < len(build["rows"]) and build_cash >= build["rows"][build_index]["cost"]:
            build_cash -= build["rows"][build_index]["cost"]
            grant_build_rewards(target, build["rows"][build_index])
            build_index += 1
            if build_index == len(build["rows"]) and build_complete_spin is None:
                build_complete_spin = spin
                build_complete_level = state.level
        balance += balance_add[0]
        balance_add[0] = 0

        pick = plinko["pick"].get(target_bet)
        if pick:
            quest_points = pick["probability"] * nearest_cheat(
                plinko, pick["id"], current_level
            )
            plinko_ball_progress += quest_points / plinko["ball_threshold"]
        while plinko_ball_progress >= 1 and plinko_stage < len(plinko["stages"]):
            plinko_ball_progress -= 1
            plinko_balls_used += 1
            plinko_score += plinko["points"].get(min(plinko_stage, 7), plinko["points"][7])
            while (
                plinko_stage < len(plinko["stages"])
                and plinko_score >= plinko["stages"][plinko_stage]["points"]
            ):
                plinko_score -= plinko["stages"][plinko_stage]["points"]
                reward = plinko["stages"][plinko_stage]["reward_cents"] * COINS_PER_CENT
                plinko_config_reward_coins += reward
                plinko_stage += 1
                plinko_stages_cleared += 1

        if control_active_remaining > 0:
            control_active_remaining -= 1
            if control_active_remaining == 0:
                control_cooldown_remaining = args.control_cooldown_spins
                control_events.append(
                    {"spin": spin, "event": "退出调控进入冷却", "round": control_round}
                )
        elif control_cooldown_remaining > 0:
            control_cooldown_remaining -= 1
            if (
                control_cooldown_remaining == 0
                and control_round < integer(config["comm"].get(105, 3))
            ):
                control_round += 1
                control_active_remaining = args.control_active_spins
                control_events.append(
                    {"spin": spin, "event": "冷却结束再次进入调控", "round": control_round}
                )

        for mission in bp["missions"]:
            if mission["spin"] == day_spin:
                balance += mission["coins"]
                target["returns"]["每日任务"] += mission["coins"]
                bp_exp += mission["exp"]
                while bp_level < len(bp["levels"]) and bp_exp >= bp["levels"][bp_level]["need"]:
                    bp_exp -= bp["levels"][bp_level]["need"]
                    reward = bp["levels"][bp_level]["free_coins"]
                    balance += reward
                    target["returns"]["FunBP"] += reward
                    bp_level += 1

        if day_spin % 300 == 0:
            multiplier = max(
                value for need, value in free["multipliers"] if need <= day_spin
            )
            reward = (
                free["hourly_raw"] * free["wheel_multiplier"] * multiplier
                * COINS_PER_MILLI_USD
            )
            balance += reward
            target["returns"]["免费奖励"] += reward
        if day_spin in free["online"]:
            reward = free["online"][day_spin]
            balance += reward
            target["returns"]["免费奖励"] += reward

        # 每日重置后重新领取签到均摊与登录任务；首日已在Spin前计入。
        if day_spin == 1 and spin > 1:
            balance += start_free + start_daily
            target["returns"]["免费奖励"] += start_free
            target["returns"]["每日任务"] += start_daily

        recent_balance_peak = max(recent_balance_peak, balance)

        fixed_nodes = {
            20, 50, 100, 253, 300, 328, 578, 600, 653, 903, 1_000,
            1_200, 1_350, 1_800, 1_801, 2_050, 2_125, 2_375, 2_450,
            2_700, 3_600, 3_601, 3_850, 3_925, 4_175, 4_250, 4_500, 5_400,
        }
        if spin <= 10 or spin in fixed_nodes or spin == build_complete_spin or paid_this_spin:
            snapshots.append(
                {
                    "spin": spin, "level": state.level, "bet_level": target_bet,
                    "bet": bet, "balance": balance, "build_flips": build_index,
                    "plinko_balls": plinko_balls_used,
                    "plinko_stage": plinko_stage, "bp_level": bp_level,
                    "payment": next(
                        (
                            f"${event['price_cents']/100:.2f}"
                            for event in payment_events if event["spin"] == spin
                        ),
                        "—",
                    ),
                    "cumulative_paid_cents": cumulative_paid_cents,
                    "broken_control": control_eligible,
                    "control_window": control_active_remaining > 0,
                    "control_loss_rate": control_loss_rate,
                    "chip_bet_ratio": chip_bet_ratio,
                }
            )
        # 三天轨迹保留每一次Spin，便于观察短时波动和付费前后变化。
        chart_series.append(
            {
                "spin": spin,
                "day": (spin - 1) // spins_per_day + 1,
                "balance": balance,
                "bet": bet,
                "level": state.level,
                "broken_control": control_eligible,
                "payment": next(
                    (event["price_cents"] for event in payment_events if event["spin"] == spin),
                    None,
                ),
            }
        )

    stage_results = []
    for stage, values in zip(stages, buckets):
        total_return = sum(values["returns"].values())
        stage_results.append(
            {
                **stage,
                "wager": values["wager"],
                "total_return": total_return,
                "total_rtp": total_return / values["wager"] if values["wager"] else 0,
                "modules": {
                    name: {
                        "return": amount,
                        "rtp": amount / values["wager"] if values["wager"] else 0,
                        "share": amount / total_return if total_return else 0,
                    }
                    for name, amount in values["returns"].items()
                },
            }
        )
    return {
        "divisor": divisor,
        "days": args.days,
        "spins_per_day": spins_per_day,
        "total_spins": total_spins,
        "end_balance": balance,
        "end_level": state.level,
        "end_bet": snapshots[-1].get("bet") if snapshots else None,
        "build_flips": build_index,
        "build_total_flips": len(build["rows"]),
        "build_complete_spin": build_complete_spin,
        "build_complete_level": build_complete_level,
        "plinko_balls_used": plinko_balls_used,
        "plinko_stages_cleared": plinko_stages_cleared,
        "plinko_config_reward_coins": plinko_config_reward_coins,
        "bp_level": bp_level,
        "bp_exp_remainder": bp_exp,
        "stages": stage_results,
        "snapshots": snapshots,
        "premium_bp_incremental_coins": sum(
            level["paid_coins"] for level in bp["levels"][:bp_level]
        ),
        "payment_events": payment_events,
        "control_events": control_events,
        "chart_series": chart_series,
        "total_paid_cents": cumulative_paid_cents,
    }


def main() -> int:
    args = parse_args()
    root = args.config_root.resolve()
    scenarios = [simulate(root, divisor, args) for divisor in (100, 150, 200)]
    def payer_schedule(peak_ratio: float | None = None) -> list[dict[str, Any]]:
        return [
            {
                "level": 15, "package": "BagNoviceOffer2首充",
                "price_cents": 199, "coins": 50_000_000,
                "trigger": "达到15级后首充弹窗曝光并购买（体验假设，非破产）",
                # 首充固定配置，不参与峰值定价。
            },
            {
                "spin": 1_801, "package": "新手第二档主动加购情景",
                "price_cents": 499, "coins": 4_990_000,
                "trigger": "第2天回流主动加购（情景假设）",
                "peak_ratio": peak_ratio,
            },
            {
                "spin": 3_601, "package": "新手第三档主动加购情景",
                "price_cents": 699, "coins": 6_990_000,
                "trigger": "第3天回流主动加购（情景假设）",
                "peak_ratio": peak_ratio,
            },
        ]

    original_payer = simulate(root, 150, args, payer_schedule())
    peak_pricing_scenarios = [
        {"ratio": ratio, "result": simulate(root, 150, args, payer_schedule(ratio))}
        for ratio in (0.50, 0.75, 1.00)
    ]
    # 主体验轨始终使用原付费阶梯；峰值定价只作为敏感性试算保留。
    aggressive_payer = original_payer
    result = {
        "source": {"revision": args.revision},
        "assumptions": {
            "start_coins": args.start_coins,
            "days": args.days,
            "daily_minutes": args.daily_minutes,
            "spin_seconds": args.spin_seconds,
            "spins_per_day": args.daily_minutes * 60 // args.spin_seconds,
            "total_spins": args.days * args.daily_minutes * 60 // args.spin_seconds,
            "aggressive_until_level": args.aggressive_until_level,
            "stable_rtp": args.stable_rtp,
            "stable_after_level": args.stable_after_level,
            "plinko_rtp": args.plinko_rtp,
            "broken_control": {
                "open": 1,
                "chip_bet_ratio_valid": 200,
                "control_bet_limit": 500000,
                "round_limit": 3,
                "active_spins": args.control_active_spins,
                "cooldown_spins": args.control_cooldown_spins,
            },
            "stable_bet_policy": "持金/100、/150、/200三档，取不高于目标的最高已解锁Bet",
            "reward_type_17": "按美分解释，1单位=0.01 USD=10,000金币",
            "hourly_coins": "按千分之一USD解释",
            "funbp_daily_completion": "Group0/Level0四个每日任务在100/300/600/1000 Spin完成",
            "build_box": "功能区100%按每章1次保守估计",
            "build_cash_cheat_sheet": "百分倍率整数，336按3.36倍计算",
            "post_tutorial_build_drop": "账号前20 Spin读取配置；其后按40%概率、500基础建设币计算",
        },
        "scenarios": scenarios,
        "original_payer": original_payer,
        "peak_pricing_scenarios": peak_pricing_scenarios,
        "selected_peak_ratio": None,
        "aggressive_payer": aggressive_payer,
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
