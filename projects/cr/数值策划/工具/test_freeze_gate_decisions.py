"""只验证新增积分连续结算规则，不重复 Accepted 盘点验收。"""
import unittest
from fractions import Fraction

from apply_freeze_gate_decisions import cumulative_spins, settle


class ContinuousSettlementTests(unittest.TestCase):
    def test_one_hit_can_cross_multiple_stages(self) -> None:
        stages = [{'LevelUpPoints': t, 'num': n} for t, n in [(5, 1), (7, 2), (4, 3)]]
        self.assertEqual(settle(17, 0, stages), (1, 2, 6))

    def test_final_stage_repeats_with_remainder(self) -> None:
        self.assertEqual(settle(23, 0, [{'LevelUpPoints': 7, 'num': 2}]), (2, 0, 6))

    def test_zero_reward_terminal_stops_production(self) -> None:
        stages = [{'LevelUpPoints': 5, 'num': 1}, {'LevelUpPoints': 7, 'num': 0}]
        self.assertEqual(settle(17, 0, stages), (5, 1, 1))
        self.assertEqual(settle(70, 1, stages), (0, 1, 0))

    def test_cumulative_first_passage_agrees_with_point_simulation(self) -> None:
        # 合成门槛5+5、每次命中给3分：第四次命中到达第二档。
        stages = [{'LevelUpPoints': 5, 'num': 1}, {'LevelUpPoints': 5, 'num': 1}]
        points = index = rewards = hits = 0
        while rewards < 2:
            points, index, delivered = settle(points + 3, index, stages)
            rewards += delivered
            hits += 1
        self.assertEqual(hits, 4)
        self.assertEqual(cumulative_spins(10, 3, Fraction(1, 2)), hits * 2)
        # 第三档累计只需5次命中；逐档清零会算成6次。
        self.assertEqual(cumulative_spins(15, 3, Fraction(1, 2)), 10)


if __name__ == '__main__':
    unittest.main()
