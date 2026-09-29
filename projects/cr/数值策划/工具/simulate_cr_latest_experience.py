"""按 CR 配置复算新用户 Spin、等级、建造和付费压力体验。"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from simulate_new_user_spin import data_rows, integer


RTP_BY_TIER = {1: 0.95, 2: 0.85, 3: 2.50, 4: 1.30}
COINS_PER_USD = 1_000_000
COINS_PER_CENT = COINS_PER_USD // 100
# 用财神机台对应策略表的一级 NON_HIT 权重近似命中率；只用于压力模拟。
NON_HIT_BY_TIER = {
    1: 121_063 / 200_000,
    2: 127_063 / 266_628,
    3: 10_000 / 30_575,
    4: 18_014 / 72_631,
}


@dataclass
class LevelState:
    """等级与当前级内进度。"""

    level: int = 1
    progress: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config-root",
        type=Path,
        required=True,
        help="目标 dev 或 trunk 的 ExcelConfigExport/Excel 目录。",
    )
    parser.add_argument("--source-label", required=True, help="例如 dev 或 trunk")
    parser.add_argument("--revision", default="未记录")
    parser.add_argument("--start-coins", type=int, default=33_600)
    parser.add_argument("--spin-seconds", type=int, default=3)
    parser.add_argument("--users", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20_260_804)
    parser.add_argument("--max-spins", type=int, default=1_000)
    parser.add_argument("--bankroll-bet-divisor", type=int, default=150)
    parser.add_argument("--aggressive-until-level", type=int, default=10)
    parser.add_argument("--stable-rtp", type=float, default=0.90)
    parser.add_argument("--stable-after-level", type=int, default=50)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def load_config(root: Path) -> dict[str, Any]:
    levels = {
        integer(row[0]): (integer(row[1]), integer(row[2]))
        for row in data_rows(root / "LevelCfg.xlsx", "Sheet1")
        if row and isinstance(row[0], (int, float))
    }
    bets = {
        integer(row[0]): {"exp": integer(row[4]), "bet": integer(row[5])}
        for row in data_rows(root / "SlotsCasinoBetList.xlsx", "Sheet1")
        if len(row) >= 6 and isinstance(row[0], (int, float))
    }
    awards = {
        integer(row[0]): integer(row[3])
        for row in data_rows(root / "LevelAward.xlsx", "Sheet1")
        if len(row) >= 4 and isinstance(row[0], (int, float))
    }
    unlocks: dict[int, int] = {}
    for row in data_rows(root / "SlotsCasinoBetUnlock.xlsx", "Sheet2"):
        if len(row) >= 3 and isinstance(row[0], (int, float)) and integer(row[1]) == 0:
            gate = integer(row[0])
            unlocks[gate] = max(unlocks.get(gate, 0), integer(row[2]))
    rtp_ranges = [
        (integer(row[1]), integer(row[2]), integer(row[3]))
        for row in data_rows(root / "SlotsCasinoNewbieConfig.xlsx", "Sheet1")
        if len(row) >= 4 and isinstance(row[0], (int, float))
    ]
    drops = {
        integer(row[0]): {"probability": integer(row[1]) / 100, "base": integer(row[4])}
        for row in data_rows(root / "SpinDropBuildingCoins.xlsx", "Sheet1")
        if len(row) >= 5 and isinstance(row[0], (int, float))
    }
    coefficients: dict[tuple[int, int], int] = {}
    for row in data_rows(root / "BuildCashCheatSheet.xlsx", "Sheet1"):
        if len(row) >= 3 and isinstance(row[0], (int, float)):
            coefficients[(integer(row[0]), integer(row[1]))] = integer(row[2])
    build_rows = [
        (integer(row[0]), integer(row[1]), integer(row[2]), integer(row[4]))
        for row in data_rows(root / "BuildLevelCfg.xlsx", "Sheet1")
        if len(row) >= 5 and isinstance(row[0], (int, float))
    ]
    comm = {
        integer(row[0]): integer(row[1])
        for row in data_rows(root / "CommCfg.xlsx", "Sheet1")
        if len(row) >= 2 and isinstance(row[0], (int, float))
    }
    control_row = next(
        (
            row for row in data_rows(root / "ChipAndBetLimitControl.xlsx", "Sheet1")
            if len(row) >= 8 and integer(row[0]) == 0
        ),
        None,
    )
    control_loss_rates: list[tuple[int, float]] = []
    if control_row:
        for offset in range(6, len(control_row) - 1, 2):
            if control_row[offset] is None or control_row[offset + 1] is None:
                continue
            control_loss_rates.append(
                (integer(control_row[offset]), integer(control_row[offset + 1]) / 100)
            )
    novice_rows = data_rows(root / "BagNoviceOffer2.xlsx", "Sheet1")
    novice_header = next(
        (row for row in novice_rows if len(row) >= 11 and integer(row[0]) == 1), None
    )
    novice_reward = next(
        (
            row for row in novice_rows
            if len(row) >= 7 and integer(row[4]) == 17 and integer(row[6]) > 0
        ),
        None,
    )
    first_pay = None
    if novice_header and novice_reward:
        first_pay = {
            "name": "BagNoviceOffer2首充",
            "price_cents": integer(novice_header[10]),
            "coins": integer(novice_reward[6]) * COINS_PER_CENT,
            "source": "BagNoviceOffer2.xlsx",
        }
    bbk_rows_raw = [
        {
            "name": f"BBK礼包{integer(row[0])}",
            "price_cents": int(round(float(row[3] or 0))),
            "vip_level": integer(row[4]),
            "coins": integer(row[5]) + integer(row[6]),
        }
        for row in data_rows(root / "PayNewBbkBag.xlsx", "Sheet1")
        if len(row) >= 7 and isinstance(row[0], (int, float))
    ]
    # 同价位存在多个VIP版本；体验深度表每个价格只取金币最多的一档，并按价格递增。
    bbk_by_price: dict[int, dict[str, Any]] = {}
    for package in bbk_rows_raw:
        price = integer(package["price_cents"])
        if price not in bbk_by_price or integer(package["coins"]) > integer(
            bbk_by_price[price]["coins"]
        ):
            bbk_by_price[price] = package
    bbk_rows = [bbk_by_price[price] for price in sorted(bbk_by_price)]
    # $4.99/$6.99为用户指定的新手激进付费情景；金币按基础汇率1 USD=1M暂估。
    scenario_packages = [
        {"name": "新手加购情景$4.99", "price_cents": 499, "coins": 4_990_000, "assumption": True},
        {"name": "新手加购情景$6.99", "price_cents": 699, "coins": 6_990_000, "assumption": True},
    ]
    later_bbk = [row for row in bbk_rows if integer(row["price_cents"]) > 699]
    purchase_ladder = ([first_pay] if first_pay else []) + scenario_packages + later_bbk
    return {
        "levels": levels,
        "bets": bets,
        "awards": awards,
        "unlocks": unlocks,
        "rtp_ranges": rtp_ranges,
        "drops": drops,
        "coefficients": coefficients,
        "build_rows": build_rows,
        "initial_build_cash": comm.get(293, 0),
        "comm": comm,
        "control_loss_rates": control_loss_rates,
        "purchase_ladder": purchase_ladder,
    }


def bet_level(config: dict[str, Any], level: int) -> int:
    return max((value for gate, value in config["unlocks"].items() if gate <= level), default=1)


def policy_bet_level(
    config: dict[str, Any], level: int, balance: float, divisor: int, aggressive_until: int
) -> int:
    """新手期取最高可用Bet，稳定期取不高于持金/divisor的最高Bet。"""

    unlocked = bet_level(config, level)
    affordable = [
        level_id
        for level_id in range(1, unlocked + 1)
        if config["bets"][level_id]["bet"] <= balance
    ]
    if not affordable:
        return 0
    if level <= aggressive_until:
        return max(affordable)
    target = balance / max(1, divisor)
    sustainable = [
        level_id for level_id in affordable if config["bets"][level_id]["bet"] <= target
    ]
    return max(sustainable, default=min(affordable))


def rtp_tier(config: dict[str, Any], level: int) -> int:
    for minimum, maximum, tier in config["rtp_ranges"]:
        if minimum <= level <= maximum:
            return tier
    return 1


def effective_rtp(config: dict[str, Any], level: int, stable_rtp: float, stable_after: int) -> float:
    """新手分段沿用配置；超过新手期后使用报告指定的稳定期RTP。"""

    if level > stable_after:
        return stable_rtp
    return RTP_BY_TIER[rtp_tier(config, level)]


def build_coefficient(config: dict[str, Any], target_bet: int, level: int) -> int:
    values = [
        (gate, value)
        for (configured_bet, gate), value in config["coefficients"].items()
        if configured_bet == target_bet and gate <= level
    ]
    return max(values, default=(0, 0))[1]


def advance(config: dict[str, Any], state: LevelState, target_bet: int) -> int:
    level_type, requirement = config["levels"][state.level]
    state.progress += 1 if level_type == 1 else config["bets"][target_bet]["exp"]
    reward = 0
    while state.level in config["levels"] and state.progress >= config["levels"][state.level][1]:
        state.progress -= config["levels"][state.level][1]
        state.level += 1
        reward += config["awards"].get(state.level, 0)
    return reward


def expectation_ledger(
    config: dict[str, Any], start_coins: int, spin_seconds: int, divisor: int,
    aggressive_until: int, max_spins: int, stable_rtp: float, stable_after: int,
) -> list[dict[str, Any]]:
    snapshots = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 50, 100, 300, 600, 1_000, 1_350, 1_800, 3_600, 5_400}
    state = LevelState()
    balance = float(start_coins)
    build_cash = float(config["initial_build_cash"])
    build_index = 0
    cost = 0
    slot_return = 0.0
    build_gain_total = 0.0
    build_rows = config["build_rows"]
    while build_index < len(build_rows) and build_cash >= build_rows[build_index][2]:
        build_cash -= build_rows[build_index][2]
        build_index += 1
    result = [{
        "spin": 0, "minutes": 0, "level": 1, "display_level": 0, "bet_level": 1,
        "bet": config["bets"][1]["bet"], "cost": 0, "slot_return": 0, "balance": balance,
        "build_gain": 0, "build_cash": build_cash, "flips": build_index,
    }]
    for spin in range(1, max_spins + 1):
        current_level = state.level
        target_bet = policy_bet_level(
            config, current_level, balance, divisor, aggressive_until
        )
        if target_bet == 0:
            break
        bet = config["bets"][target_bet]["bet"]
        current_rtp = effective_rtp(config, current_level, stable_rtp, stable_after)
        cost += bet
        slot_return += bet * current_rtp
        balance += bet * (current_rtp - 1)
        balance += advance(config, state, target_bet)
        drop = config["drops"].get(spin)
        probability = drop["probability"] if drop else 0.40
        base = drop["base"] if drop else 500
        # BuildCashCheatSheet为百分倍率整数：336表示3.36倍。
        build_gain = probability * base * build_coefficient(config, target_bet, current_level) / 100
        build_cash += build_gain
        build_gain_total += build_gain
        while build_index < len(build_rows) and build_cash >= build_rows[build_index][2]:
            build_cash -= build_rows[build_index][2]
            build_index += 1
        if spin in snapshots:
            result.append({
                "spin": spin, "minutes": spin * spin_seconds / 60, "level": state.level,
                "display_level": state.level - 1, "bet_level": target_bet, "bet": bet,
                "cost": cost, "slot_return": slot_return, "balance": balance,
                "build_gain": build_gain_total, "build_cash": build_cash, "flips": build_index,
            })
    return result


def simulate_user(config: dict[str, Any], start_coins: int, seed: int, max_spins: int, rescue: int, divisor: int, aggressive_until: int, stable_rtp: float, stable_after: int) -> dict[str, int | float | None]:
    rng = random.Random(seed)
    state = LevelState()
    balance = float(start_coins)
    first_pressure_spin: int | None = None
    first_pressure_level: int | None = None
    used_rescue = False
    spin = 0
    while spin < max_spins:
        target_bet = policy_bet_level(config, state.level, balance, divisor, aggressive_until)
        if target_bet == 0:
            break
        bet = config["bets"][target_bet]["bet"]
        if balance < bet:
            if first_pressure_spin is None:
                first_pressure_spin = spin + 1
                first_pressure_level = state.level
            if rescue and not used_rescue:
                balance += rescue
                used_rescue = True
            if balance < bet:
                break
        spin += 1
        tier = rtp_tier(config, state.level)
        hit_rate = 1 - NON_HIT_BY_TIER[tier]
        balance -= bet
        if rng.random() < hit_rate:
            balance += bet * effective_rtp(config, state.level, stable_rtp, stable_after) / hit_rate
        balance += advance(config, state, target_bet)
    return {
        "spins": spin, "level": state.level, "balance": balance,
        "first_pressure_spin": first_pressure_spin, "first_pressure_level": first_pressure_level,
    }


def cohort(config: dict[str, Any], args: argparse.Namespace, rescue: int, label: str) -> dict[str, Any]:
    samples = [simulate_user(config, args.start_coins, args.seed + n, args.max_spins, rescue, args.bankroll_bet_divisor, args.aggressive_until_level, args.stable_rtp, args.stable_after_level) for n in range(args.users)]
    pressure = [x for x in samples if x["first_pressure_spin"] is not None]
    spins = sorted(integer(x["spins"]) for x in samples)
    levels = sorted(integer(x["level"]) for x in samples)
    pressure_spins = sorted(integer(x["first_pressure_spin"]) for x in pressure)
    pressure_levels = sorted(integer(x["first_pressure_level"]) for x in pressure)
    return {
        "label": label, "rescue_coins": rescue,
        "pressure_rate": len(pressure) / len(samples),
        "pressure_spin_p50_conditional": pressure_spins[len(pressure_spins) // 2] if pressure else None,
        "pressure_level_p50_conditional": pressure_levels[len(pressure_levels) // 2] if pressure else None,
        "spins_p10": spins[len(spins) // 10], "spins_p50": spins[len(spins) // 2],
        "level_p50": levels[len(levels) // 2],
        "reach_max_spins_rate": sum(integer(x["spins"]) == args.max_spins for x in samples) / len(samples),
    }


def simulate_lifecycle(
    config: dict[str, Any], start_coins: int, seed: int, max_spins: int,
    divisor: int, aggressive_until: int, stable_rtp: float, stable_after: int,
) -> dict[str, Any]:
    """同一账号每次余额不足时依次购买更深一档礼包。"""

    rng = random.Random(seed)
    state = LevelState()
    balance = float(start_coins)
    spin = 0
    purchases: list[dict[str, Any]] = []
    ladder = config["purchase_ladder"]
    while spin < max_spins:
        target_bet = policy_bet_level(
            config, state.level, balance, divisor, aggressive_until
        )
        if target_bet == 0 and len(purchases) < len(ladder):
            package = ladder[len(purchases)]
            before = balance
            balance += package["coins"]
            target_bet = policy_bet_level(
                config, state.level, balance, divisor, aggressive_until
            )
            purchases.append(
                {
                    "depth": len(purchases) + 1,
                    "spin": spin + 1,
                    "level": state.level,
                    "bet_level_after_purchase": target_bet,
                    "bet_after_purchase": (
                        config["bets"][target_bet]["bet"] if target_bet else None
                    ),
                    "balance_before": before,
                    "package": package["name"],
                    "price_cents": package["price_cents"],
                    "coins": package["coins"],
                    "balance_after": balance,
                }
            )
        if target_bet == 0:
            break
        bet = config["bets"][target_bet]["bet"]
        spin += 1
        tier = rtp_tier(config, state.level)
        hit_rate = 1 - NON_HIT_BY_TIER[tier]
        balance -= bet
        if rng.random() < hit_rate:
            balance += bet * effective_rtp(config, state.level, stable_rtp, stable_after) / hit_rate
        balance += advance(config, state, target_bet)
    return {"spins": spin, "level": state.level, "balance": balance, "purchases": purchases}


def lifecycle_cohort(config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    samples = [
        simulate_lifecycle(
            config, args.start_coins, args.seed + index, args.max_spins,
            args.bankroll_bet_divisor, args.aggressive_until_level,
            args.stable_rtp, args.stable_after_level,
        )
        for index in range(args.users)
    ]
    ladder = config["purchase_ladder"]
    depths: list[dict[str, Any]] = []
    cumulative_price = 0
    for index, package in enumerate(ladder):
        cumulative_price += package["price_cents"]
        reached = [sample for sample in samples if len(sample["purchases"]) > index]
        if not reached:
            break
        events = [sample["purchases"][index] for sample in reached]
        spins = sorted(integer(event["spin"]) for event in events)
        levels = sorted(integer(event["level"]) for event in events)
        bets = sorted(integer(event["bet_after_purchase"]) for event in events)
        next_intervals = sorted(
            integer(sample["purchases"][index + 1]["spin"])
            - integer(sample["purchases"][index]["spin"])
            for sample in samples
            if len(sample["purchases"]) > index + 1
        )
        depths.append(
            {
                "depth": index + 1,
                "package": package["name"],
                "price_cents": package["price_cents"],
                "coins": package["coins"],
                "vip_gate": package.get("vip_level"),
                "cumulative_price_cents": cumulative_price,
                "reach_rate": len(reached) / len(samples),
                "purchase_spin_p50": spins[len(spins) // 2],
                "purchase_level_p50": levels[len(levels) // 2],
                "post_purchase_bet_p50": bets[len(bets) // 2],
                "spins_to_next_purchase_p50": (
                    next_intervals[len(next_intervals) // 2] if next_intervals else None
                ),
            }
        )
    end_spins = sorted(integer(sample["spins"]) for sample in samples)
    end_levels = sorted(integer(sample["level"]) for sample in samples)
    return {
        "description": "同一账号余额不足最低Bet时破产；购买后按余额选择最高可承受Bet继续，礼包价格逐档提高",
        "depths": depths,
        "end_spins_p50": end_spins[len(end_spins) // 2],
        "end_level_p50": end_levels[len(end_levels) // 2],
        "reach_max_spins_rate": sum(
            integer(sample["spins"]) == args.max_spins for sample in samples
        )
        / len(samples),
    }


def main() -> int:
    args = parse_args()
    config = load_config(args.config_root.resolve())
    build_rows = config["build_rows"]
    result = {
        "source": {"label": args.source_label, "revision": args.revision},
        "assumptions": {
            "start_coins": args.start_coins, "initial_build_cash": config["initial_build_cash"],
            "spin_seconds": args.spin_seconds, "vip": 0,
            "bet_policy": (
                f"配置等级≤{args.aggressive_until_level}取最高可承受已解锁Bet；"
                f"之后按持金/{args.bankroll_bet_divisor}取不高于目标的最高已解锁Bet"
            ),
            "users": args.users, "seed": args.seed, "max_spins": args.max_spins,
            "bankroll_bet_divisor": args.bankroll_bet_divisor,
            "aggressive_until_level": args.aggressive_until_level,
            "stable_rtp": args.stable_rtp,
            "stable_after_level": args.stable_after_level,
        },
        "checks": {
            "build_rows": len(build_rows),
            "build_exp_nonzero": sum(1 for row in build_rows if row[3] != 0),
        },
        "ledger": expectation_ledger(
            config, args.start_coins, args.spin_seconds,
            args.bankroll_bet_divisor, args.aggressive_until_level,
            args.max_spins, args.stable_rtp, args.stable_after_level,
        ),
        "sequential_purchase": lifecycle_cohort(config, args),
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
