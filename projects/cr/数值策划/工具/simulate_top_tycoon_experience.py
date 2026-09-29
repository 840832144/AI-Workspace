"""Top Tycoon 录屏口径的可复算体验模拟。

本脚本不会把录屏观察值包装成服务端配置。RTP 与跨资源汇率均为具名场景
假设；录像证据、模型假设和模拟结果在 JSON 中分区保存。
"""

from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MODULES = ("Slot基础盘", "Attack/Credit Grab", "建造被动", "任务/Pass", "日历/免费", "小游戏/活动")


@dataclass(frozen=True)
class Stage:
    name: str
    start_spin: int
    end_spin: int
    points: tuple[float, float, float, float, float, float]


OBSERVED_TASK_COSTS = [
    5, 10, 30, 60, 80, 140, 160, 170, 200, 210, 240, 500, 1_000, 3_200,
    10_400, 13_400, 15_800, 22_200, 37_200, 43_000, 92_600, 121_400,
    136_200, 144_400, 152_600, 192_800, 233_000, 273_200, 275_200, 361_600,
    405_800, 425, 2_763, 4_039, 4_931, 19_556, 40_425, 46_591, 75_168,
    97_107, 114_287, 131_466, 164_325, 207_267, 275_950,
]


EVIDENCE = [
    {"account": "A/tycoon228", "video": "tycoon1_day1_1.mp4", "time": "00:01:00", "observation": "Ticket Gate 1/3，任务价 30 金币"},
    {"account": "A/tycoon228", "video": "tycoon1_day1_1.mp4", "time": "00:03:40", "observation": "Slot 已开启；50 格进度条与 +500 金币奖励可见"},
    {"account": "A/tycoon228", "video": "tycoon1_day1_1.mp4", "time": "00:05:30", "observation": "Freefall 20,999/54,000；下一任务 10 金币"},
    {"account": "A/tycoon228", "video": "tycoon1_day1_1.mp4", "time": "00:08:10", "observation": "Sky Plunge 3,000/57,000；下一任务 200 金币"},
    {"account": "A/tycoon228", "video": "tycoon1_day1_1.mp4", "time": "00:18:20", "observation": "BET x2 解锁；随后出现 x3/x5"},
    {"account": "A/tycoon228", "video": "tycoon1_day1_1.mp4", "time": "00:25:20", "observation": "商店曝光 USD $7.49/$9.99/$28.99/$56.99/$98.99，无购买"},
    {"account": "A/tycoon228", "video": "tycoon1_day2_1.mp4", "time": "00:06:40", "observation": "Sky Plunge 下一任务价 273,200 金币；出现 Insufficient coins"},
    {"account": "B/tycoon261", "video": "tycoon2_day2_1.mp4", "time": "00:01:30", "observation": "Thermal Soar 建造枯竭；下一任务价 40,425 金币"},
    {"account": "B/tycoon261", "video": "tycoon2_day2_1.mp4", "time": "00:05:30", "observation": "BET x10 解锁"},
    {"account": "B/tycoon261", "video": "tycoon2_day2_1.mp4", "time": "00:08:50", "observation": "Snack Time / Dice Drive 小游戏入口与局内消耗可见"},
    {"account": "B/tycoon261", "video": "tycoon2_day2_2.mp4", "time": "00:05:50", "observation": "Credit Grab 大额结算 215,000 金币"},
    {"account": "B/tycoon261", "video": "tycoon2_day2_2.mp4", "time": "00:10:40", "observation": "TRY 商店曝光 Chapter/Mission Pass 与资源包，无购买"},
    {"account": "B/tycoon261", "video": "tycoon2_day2_3 .mp4", "time": "00:01:30", "observation": "Credit Grab 结算 230,000 金币"},
    {"account": "B/tycoon261", "video": "tycoon2_day2_3 .mp4", "time": "00:06:40", "observation": "Fable Haven 下一任务价 275,950 金币"},
]


OFFERS = [
    {"pay_segment": "低付费曝光", "offer": "Chapter Prize", "price": "$7.49", "visible_value": "Up to 2.06K 能量", "purchased": False, "account": "A"},
    {"pay_segment": "低付费曝光", "offer": "Mission Pass", "price": "$9.99", "visible_value": "Up to 4K 能量", "purchased": False, "account": "A"},
    {"pay_segment": "中付费曝光", "offer": "Super Pack", "price": "$28.99", "visible_value": "590 能量 + 280K 金币", "purchased": False, "account": "A"},
    {"pay_segment": "中付费曝光", "offer": "Mega Pack", "price": "$56.99", "visible_value": "1.3K 能量 + 610K 金币", "purchased": False, "account": "A"},
    {"pay_segment": "高付费曝光", "offer": "Ultra Pack", "price": "$98.99", "visible_value": "2.4K 能量 + 1.2M 金币", "purchased": False, "account": "A"},
    {"pay_segment": "地区价曝光", "offer": "Chapter Prize", "price": "TRY 259.99", "visible_value": "Up to 2.06K 能量", "purchased": False, "account": "B"},
    {"pay_segment": "地区价曝光", "offer": "Mission Pass", "price": "TRY 559.99", "visible_value": "Up to 4K 能量", "purchased": False, "account": "B"},
    {"pay_segment": "地区价曝光", "offer": "Beginner/Architect/Super", "price": "TRY 259.99/509.99/839.99", "visible_value": "混合能量、金币与活动道具", "purchased": False, "account": "B"},
]


def build_stages(total_spins: int, stable_rtp: float) -> list[Stage]:
    stable_points = tuple(value * stable_rtp / 0.95 for value in (68, 10, 5, 5, 4, 3))
    return [
        Stage("教程强扶持", 1, min(100, total_spins), (85, 15, 20, 20, 15, 5)),
        Stage("首日成长", 101, min(600, total_spins), (75, 15, 10, 10, 10, 5)),
        Stage("次日过渡", 601, min(1_800, total_spins), (72, 12, 8, 6, 6, 4)),
        Stage("稳定期", 1_801, total_spins, stable_points),
    ]


def bet_multiplier(spin: int) -> int:
    if spin <= 200:
        return 1
    if spin <= 600:
        return 3
    if spin <= 1_800:
        return 5
    return 10


def weighted_returns(
    rng: random.Random,
    count: int,
    expected_total: float,
    hit_rate: float,
    sigma: float,
) -> list[float]:
    weights: list[float] = []
    for _ in range(count):
        if rng.random() <= hit_rate:
            weights.append(rng.lognormvariate(-0.5 * sigma * sigma, sigma))
        else:
            weights.append(0.0)
    if not any(weights):
        weights[rng.randrange(count)] = 1.0
    scale = expected_total / sum(weights)
    return [round(value * scale, 4) for value in weights]


def task_cost(index: int) -> int:
    if index < len(OBSERVED_TASK_COSTS):
        return OBSERVED_TASK_COSTS[index]
    extra = index - len(OBSERVED_TASK_COSTS) + 1
    return round(OBSERVED_TASK_COSTS[-1] * (1.035**extra))


def simulate(
    *,
    days: int,
    daily_minutes: int,
    action_seconds: int,
    stable_rtp: float,
    seed: int,
    coin_per_energy: int,
) -> dict[str, Any]:
    spins_per_day = daily_minutes * 60 // action_seconds
    total_spins = spins_per_day * days
    stages = [stage for stage in build_stages(total_spins, stable_rtp) if stage.start_spin <= stage.end_spin]
    rng = random.Random(seed)
    returns: dict[str, list[float]] = {module: [0.0] * total_spins for module in MODULES}
    hit_rates = (1.0, 0.07, 0.18, 0.025, 0.005, 0.04)
    sigmas = (0.9, 1.3, 0.7, 0.5, 0.3, 1.1)

    for stage in stages:
        count = stage.end_spin - stage.start_spin + 1
        wagers = [bet_multiplier(spin) * coin_per_energy for spin in range(stage.start_spin, stage.end_spin + 1)]
        stage_wager = float(sum(wagers))
        for module_index, module in enumerate(MODULES):
            expected = stage_wager * stage.points[module_index] / 100.0
            values = weighted_returns(rng, count, expected, hit_rates[module_index], sigmas[module_index])
            returns[module][stage.start_spin - 1 : stage.end_spin] = values

    exposure_by_spin = {
        230: "付费曝光：Chapter Prize $7.49",
        600: "付费曝光：Mission Pass $9.99",
        1_200: "付费曝光：Super Pack $28.99",
        1_800: "付费曝光：Mega Pack $56.99",
        2_400: "付费曝光：Ultra Pack $98.99",
    }
    area_names = ("Freefall", "Sky Plunge", "Thermal Soar", "Fable Haven", "稳定循环")
    trajectory: list[dict[str, Any]] = []
    balance = 0.0
    task_index = 0
    pending_cost = task_cost(task_index)

    for spin in range(1, total_spins + 1):
        day = (spin - 1) // spins_per_day + 1
        second_in_day = ((spin - 1) % spins_per_day) * action_seconds
        minute = second_in_day // 60
        second = second_in_day % 60
        stage = next(item for item in stages if item.start_spin <= spin <= item.end_spin)
        module_values = {module: round(returns[module][spin - 1]) for module in MODULES}
        total_return = sum(module_values.values())
        balance += total_return
        build_cost = 0
        event_parts: list[str] = []
        if spin % 15 == 0:
            if balance >= pending_cost:
                build_cost = pending_cost
                balance -= build_cost
                task_index += 1
                pending_cost = task_cost(task_index)
                event_parts.append("完成建造任务")
            else:
                event_parts.append("金币不足→回 Slot")
        pay_event = exposure_by_spin.get(spin, "")
        if pay_event:
            event_parts.append(pay_event + "（未购买）")
        trajectory.append(
            {
                "spin": spin,
                "day": day,
                "time_in_day": f"{minute:02d}:{second:02d}",
                "stage": stage.name,
                "bet_x": bet_multiplier(spin),
                "energy_cost": bet_multiplier(spin),
                "shadow_wager_coin": bet_multiplier(spin) * coin_per_energy,
                "module_returns": module_values,
                "total_return_coin": total_return,
                "build_cost_coin": build_cost,
                "coin_balance": round(balance),
                "build_task": task_index,
                "area": area_names[min(task_index // 35, len(area_names) - 1)],
                "pay_exposure": pay_event,
                "purchase_amount": 0,
                "event": "；".join(event_parts),
            }
        )

    stage_results: list[dict[str, Any]] = []
    for stage in stages:
        rows = trajectory[stage.start_spin - 1 : stage.end_spin]
        wager = sum(row["shadow_wager_coin"] for row in rows)
        module_points = {
            module: 100.0 * sum(row["module_returns"][module] for row in rows) / wager
            for module in MODULES
        }
        stage_results.append(
            {
                "stage": stage.name,
                "spin_range": f"{stage.start_spin}-{stage.end_spin}",
                "target_module_points": dict(zip(MODULES, stage.points)),
                "target_total_rtp": sum(stage.points),
                "realized_module_points": module_points,
                "realized_total_rtp": sum(module_points.values()),
                "shadow_wager_coin": wager,
            }
        )

    node_spins = {
        1, 100, 200, 230, 600, 1_200, 1_800, 2_400, total_spins,
        *[spins_per_day * day for day in range(1, days + 1)],
    }
    nodes = [trajectory[index - 1] for index in sorted(value for value in node_spins if 1 <= value <= total_spins)]
    module_totals = {
        module: sum(row["module_returns"][module] for row in trajectory)
        for module in MODULES
    }
    total_wager = sum(row["shadow_wager_coin"] for row in trajectory)

    return {
        "metadata": {
            "version": "v0.3",
            "seed": seed,
            "warning": "录像观察与场景模型分离；稳定期 RTP、1 能量=金币等价值均为可调假设。",
        },
        "observed_scope": {
            "videos": 5,
            "duration_seconds": 4_881.12,
            "accounts": ["A/tycoon228（Day1+Day2）", "B/tycoon261（Day2 三段）"],
            "purchase_events": 0,
            "source_path": r"D:\HuaweiMoveData\Users\wk\Desktop\tycoon2",
        },
        "assumptions": {
            "persona": "新注册、VIP/累计付费未知，主模型按 0 付费 F2P",
            "initial_coin": 0,
            "initial_energy_after_slot_unlock": 50,
            "exchange_rate": "待确认；场景仅用 1 能量 = 5,000 金币等价值",
            "startup_funds": "教程首个设施与游客门票/被动收益提供第一次建造资金",
            "days": days,
            "daily_minutes": daily_minutes,
            "action_seconds": action_seconds,
            "spins_per_day": spins_per_day,
            "total_spins": total_spins,
            "stable_rtp": stable_rtp,
            "coin_per_energy": coin_per_energy,
            "purchase_policy": "录像无购买；主轨迹不注入礼包资源，红点仅表示付费曝光",
        },
        "stage_results": stage_results,
        "nodes": nodes,
        "trajectory": trajectory,
        "module_summary": {
            module: {
                "return_coin": round(total),
                "rtp_points": 100.0 * total / total_wager,
            }
            for module, total in module_totals.items()
        },
        "offers": OFFERS,
        "evidence": EVIDENCE,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Top Tycoon 体验模拟")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--daily-minutes", type=int, default=30)
    parser.add_argument("--action-seconds", type=int, default=3)
    parser.add_argument("--stable-rtp", type=float, default=0.95)
    parser.add_argument("--coin-per-energy", type=int, default=5_000)
    parser.add_argument("--seed", type=int, default=20260804)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = simulate(
        days=args.days,
        daily_minutes=args.daily_minutes,
        action_seconds=args.action_seconds,
        stable_rtp=args.stable_rtp,
        seed=args.seed,
        coin_per_energy=args.coin_per_energy,
    )
    sensitivities = {}
    for stable_rtp in (0.90, 0.95, 1.00):
        case = simulate(
            days=args.days,
            daily_minutes=args.daily_minutes,
            action_seconds=args.action_seconds,
            stable_rtp=stable_rtp,
            seed=args.seed,
            coin_per_energy=args.coin_per_energy,
        )
        sensitivities[f"{stable_rtp:.0%}"] = {
            "ending_coin_balance": case["trajectory"][-1]["coin_balance"],
            "build_tasks": case["trajectory"][-1]["build_task"],
            "stable_realized_rtp": case["stage_results"][-1]["realized_total_rtp"],
        }
    result["sensitivity"] = sensitivities
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
