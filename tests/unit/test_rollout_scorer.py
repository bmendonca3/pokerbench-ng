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
            {"net_bb": {"agent": 1}, "events": [{"actor_role": "agent", "classification": "ok"}]},
            {"net_bb": {"agent": -0.5}, "events": [{"actor_role": "agent", "classification": "ok"}]},
        ])
        self.assertEqual(metrics["summary"]["hands"], 2)
        self.assertEqual(metrics["summary"]["controlled_bb_per_100"], 25.0)
        self.assertEqual(metrics["summary"]["decisions"], 2)
        self.assertEqual(metrics["summary"]["illegal_action_rate"], 0.0)

    def test_aggregate_rollout_reliability_rates(self):
        metrics = aggregate_rollout(
            [
                {
                    "net_bb": {"agent": 1},
                    "events": [
                        {"actor_role": "agent", "classification": "ok"},
                        {"actor_role": "agent", "classification": "illegal"},
                        {"actor_role": "agent", "classification": "timeout"},
                    ],
                },
                {
                    "net_bb": {"agent": -1},
                    "events": [
                        {"actor_role": "agent", "classification": "malformed"},
                        {"actor_role": "agent", "classification": "process_error"},
                    ],
                },
            ]
        )
        self.assertEqual(metrics["summary"]["decisions"], 5)
        self.assertEqual(metrics["summary"]["illegal_action_rate"], 0.2)
        self.assertEqual(metrics["summary"]["timeout_rate"], 0.2)
        self.assertEqual(metrics["summary"]["malformed_rate"], 0.2)
        self.assertEqual(metrics["summary"]["process_error_rate"], 0.2)

    def test_aggregate_rollout_ignores_opponent_reliability_events(self):
        metrics = aggregate_rollout(
            [
                {
                    "net_bb": {"agent": 1},
                    "events": [
                        {"actor_role": "agent", "classification": "ok"},
                        {"actor_role": "opponent", "classification": "illegal"},
                    ],
                }
            ]
        )
        self.assertEqual(metrics["summary"]["decisions"], 1)
        self.assertEqual(metrics["summary"]["illegal_action_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
