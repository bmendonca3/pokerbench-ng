import unittest

from pokerbench_ng.rollout.duplicate_hands import duplicate_group_id
from pokerbench_ng.rollout.scorer import bb_per_100
from pokerbench_ng.rollout.scorer import aggregate_rollout


class RolloutScorerTests(unittest.TestCase):
    def test_bb_per_100(self):
        self.assertEqual(bb_per_100(10, 100), 10)

    def test_hands_must_be_positive(self):
        with self.assertRaises(ValueError):
            bb_per_100(0, 0)

    def test_duplicate_group_id_is_stable(self):
        self.assertEqual(duplicate_group_id(42), "dup_000000000042")

    def test_aggregate_rollout(self):
        metrics = aggregate_rollout([
            {"net_bb": {"agent": 1}},
            {"net_bb": {"agent": -0.5}},
        ])
        self.assertEqual(metrics["summary"]["hands"], 2)
        self.assertEqual(metrics["summary"]["controlled_bb_per_100"], 25.0)


if __name__ == "__main__":
    unittest.main()
