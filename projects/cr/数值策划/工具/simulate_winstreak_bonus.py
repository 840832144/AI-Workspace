"""老虎机连胜奖励期望贡献复算脚本。

口径与配置表一致：
- 单次 Spin 结算金币 > 0 视为中奖（免费局/Jacpot 是否计入由全局规则开关控制，本脚本默认不计入）；
- 中奖 -> 连胜计数 +1；未中奖 -> 连胜计数清零；
- 达到档位门槛时发放：bonus = min(Bet * bonusMulti/100, Bet * bonusMaxMulti/100, bonusMaxCoins)；
- resetMode=1（推荐，多档位）：发奖后继续累计，3/5/8/12 依次触发，最高档位后每再达到最高档门槛循环发放；
- resetMode=0：发奖后清零重新累计（多档位同时配置时，低档位触发后本段连胜不再触发高档位）。

运行示例（仓库根目录）：
python .\\数值策划\\工具\\simulate_winstreak_bonus.py
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class StreakTier:
    """连胜档位配置，字段与 SlotsCasinoWinStreakBonus.xlsx Sheet1 对齐。"""

    streak: int
    bonus_multi: int  # 放大100倍，150 = 1.5 倍 Bet
    bonus_max_multi: int  # 放大100倍，0 = 不限制
    bonus_max_coins: int  # 金币，0 = 不限制
    reset_mode: int  # 0=发奖后清零重新累计；1=继续累计+最高档循环

    def bonus(self, bet: int) -> int:
        """按当前 Bet 计算单次发奖金额（金币）。"""
        value = bet * self.bonus_multi // 100
        if self.bonus_max_multi > 0:
            value = min(value, bet * self.bonus_max_multi // 100)
        if self.bonus_max_coins > 0:
            value = min(value, self.bonus_max_coins)
        return value


TIERS = (
    StreakTier(3, 50, 0, 2_000_000, 1),
    StreakTier(5, 100, 0, 4_000_000, 1),
    StreakTier(8, 200, 0, 8_000_000, 1),
    StreakTier(12, 400, 0, 16_000_000, 1),
)


def simulate_once(
    tiers: tuple[StreakTier, ...],
    win_prob: float,
    spins: int,
    bet: int,
    seed: int,
) -> dict:
    """模拟单次会话，返回发奖次数、发奖金币与按档位拆分。"""
    rng = random.Random(seed)
    thresholds = sorted(t.streak for t in tiers)
    max_threshold = thresholds[-1]
    tier_by_threshold = {t.streak: t for t in tiers}

    streak = 0
    payouts = {t.streak: 0 for t in tiers}
    coins = 0

    for _ in range(spins):
        if rng.random() >= win_prob:
            streak = 0
            continue
        streak += 1
        tier = None
        if streak in tier_by_threshold and tier_by_threshold[streak].reset_mode == 0:
            # 发奖后清零：只有 streak 恰好等于某档门槛时才发（先到低档先发）
            tier = tier_by_threshold[streak]
            streak = 0
        else:
            # 继续累计：每跨过一个门槛发一次；最高档后每再达到最高档门槛循环发
            if streak in tier_by_threshold:
                tier = tier_by_threshold[streak]
            elif streak > max_threshold and streak % max_threshold == 0:
                tier = tier_by_threshold[max_threshold]
        if tier is not None:
            payouts[tier.streak] += 1
            coins += tier.bonus(bet)

    return {
        "spins": spins,
        "win_prob": win_prob,
        "bet": bet,
        "bonus_coins": coins,
        "payouts": payouts,
        "bonus_per_spin": coins / spins,
        "rtp_contribution_pct": coins / spins / bet * 100,  # 对投注额的 RTP 百分点
    }


def main() -> None:
    print("连胜奖励期望贡献（Bet=100,000 金币；caps 在本 Bet 下不生效）")
    print(f"{'p_win':>6} {'mode':>4} {'E[bonus]/spin':>14} {'RTP+':>8} {'3连':>6} {'5连':>6} {'8连':>6} {'12连':>6}")
    for win_prob in (0.30, 0.45, 0.60):
        for mode in (1, 0):
            tiers = tuple(
                StreakTier(t.streak, t.bonus_multi, t.bonus_max_multi, t.bonus_max_coins, mode)
                for t in TIERS
            )
            r = simulate_once(tiers, win_prob, spins=5_400_000, bet=100_000, seed=20260811)
            p = r["payouts"]
            print(
                f"{win_prob:>6.2f} {mode:>4} {r['bonus_per_spin']:>14,.0f} "
                f"{r['rtp_contribution_pct']:>7.2f}% {p[3]:>6} {p[5]:>6} {p[8]:>6} {p[12]:>6}"
            )

    print("\n示例会话：p_win=0.45、Bet=100,000、5,400 Spin（3天*1800），resetMode=1")
    r = simulate_once(TIERS, win_prob=0.45, spins=5_400, bet=100_000, seed=20260811)
    print(
        f"发奖次数={r['payouts']}，连胜奖励金币={r['bonus_coins']:,}，"
        f"占投注额 RTP={r['rtp_contribution_pct']:.2f} 个百分点"
    )


if __name__ == "__main__":
    main()
