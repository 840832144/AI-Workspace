"""只验证TASK-0036新增条件模型；不重跑Accepted盘点或活动规则验收。"""
from fractions import Fraction
import unittest

from build_producer_experience import binomial, experience, regular_rtp


class ProducerExperienceTests(unittest.TestCase):
    def test_distribution_degenerate_inputs(self) -> None:
        self.assertEqual(binomial(0, 0.3), [1.0])
        self.assertEqual(binomial(3, 0), [1.0, 0.0, 0.0, 0.0])
        self.assertEqual(binomial(3, 1), [0.0, 0.0, 0.0, 1.0])

    def test_small_distribution_matches_enumerated_outcomes(self) -> None:
        # 三次独立二择的8个等可能结果：命中数频数1/3/3/1。
        for actual, expected in zip(binomial(3, .5), [.125, .375, .375, .125]):
            self.assertAlmostEqual(actual, expected)

    def test_large_n_probability_and_first_moment(self) -> None:
        for p in (.15, .2, .99):
            pmf = binomial(1000, p)
            self.assertAlmostEqual(sum(pmf), 1.0, places=9)
            self.assertAlmostEqual(sum(k * v for k, v in enumerate(pmf)), 1000 * p, places=7)

    def test_expected_reward_is_not_reward_at_expected_points(self) -> None:
        # 0/1/2次命中时产物为0/2/5，概率为1/4、1/2、1/4。
        result = experience(2, .5, 5, [{'LevelUpPoints': 3, 'num': 2},
                                     {'LevelUpPoints': 3, 'num': 3}, {'LevelUpPoints': 100, 'num': 0}])
        self.assertAlmostEqual(result['expected_items'], 2.25)
        self.assertAlmostEqual(result['p_any_earned_item'], .75)
        self.assertEqual(result['items_at_mean_points_not_expectation'], 2)

    def test_no_impossible_first_reward_below_hit_requirement(self) -> None:
        result = experience(2, .2, 10, [{'LevelUpPoints': 30, 'num': 1}, {'LevelUpPoints': 1, 'num': 0}])
        self.assertEqual(result['expected_items'], 0)
        self.assertEqual(result['p_any_earned_item'], 0)

    def test_rtp_exact_one_and_both_sides(self) -> None:
        self.assertEqual(regular_rtp(Fraction(99, 100)), Fraction(95, 100))
        self.assertEqual(regular_rtp(Fraction(1)), Fraction(95, 100))
        self.assertEqual(regular_rtp(Fraction(101, 100)), Fraction(85, 100))


if __name__ == '__main__':
    unittest.main()
