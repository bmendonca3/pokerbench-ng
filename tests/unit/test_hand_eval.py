import unittest

from pokerbench_ng.engine.hand_eval import best_five_rank, compare_hands


class HandEvalTests(unittest.TestCase):
    def test_straight_flush_beats_quads(self):
        straight_flush = ["As", "Ks", "Qs", "Js", "Ts", "2c", "3d"]
        quads = ["Ah", "Ad", "Ac", "As", "9d", "2c", "3h"]
        self.assertGreater(compare_hands(straight_flush, quads), 0)

    def test_wheel_straight(self):
        wheel = best_five_rank(["As", "2d", "3c", "4h", "5s", "9d", "Td"])
        six_high = best_five_rank(["2s", "3d", "4c", "5h", "6s", "9d", "Td"])
        self.assertLess(wheel, six_high)

    def test_pair_kicker_breaks_tie(self):
        first = ["As", "Ad", "Kc", "7h", "5s", "3d", "2c"]
        second = ["Ah", "Ac", "Qc", "7d", "5d", "3s", "2h"]
        self.assertGreater(compare_hands(first, second), 0)


if __name__ == "__main__":
    unittest.main()
