import unittest

from pokerbench_ng.static.scorer import ev_loss, is_blunder
from pokerbench_ng.static.scorer import evaluate_static_spots


class StaticScorerTests(unittest.TestCase):
    def test_ev_loss_never_negative(self):
        self.assertEqual(ev_loss(1.0, 1.5), 0.0)
        self.assertAlmostEqual(ev_loss(1.5, 1.0), 0.5)

    def test_blunder_threshold(self):
        self.assertTrue(is_blunder(0.5, 5.0))
        self.assertFalse(is_blunder(0.1, 5.0))

    def test_evaluate_static_spots(self):
        spots = [
            {
                "spot_id": "s1",
                "pot_bb": 10,
                "legal_actions": [{"type": "fold"}, {"type": "call", "amount_bb": 1}],
                "policy": [
                    {"action": {"type": "fold"}, "ev_bb": 0},
                    {"action": {"type": "call"}, "ev_bb": 1},
                ],
                "best_action": {"type": "call"},
                "best_ev_bb": 1,
            }
        ]
        responses = [{"schema_version": "1.0", "request_id": "s1", "action": {"type": "call", "amount_to_bb": 1}}]
        metrics = evaluate_static_spots(spots, responses)
        self.assertEqual(metrics["summary"]["static_spots"], 1)
        self.assertEqual(metrics["summary"]["static_ev_loss_bb_per_decision"], 0)


if __name__ == "__main__":
    unittest.main()
