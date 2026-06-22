import unittest
from pathlib import Path

from pokerbench_ng.agents.protocol import AgentAction, AgentResponse
from pokerbench_ng.static.scorer import ev_loss, is_blunder
from pokerbench_ng.static.scorer import EvaluatedResponse, evaluate_static_spots
from pokerbench_ng.static.spots import load_jsonl


DEV_SPOTS_PATH = Path("src/pokerbench_ng/data/public_spots/dev.example.jsonl")


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

    def test_evaluate_static_spots_preserves_timeout_classification(self):
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
        responses = [EvaluatedResponse(AgentResponse("1.0", "s1", AgentAction("fold")), "timeout")]

        metrics = evaluate_static_spots(spots, responses)

        self.assertEqual(metrics["summary"]["timeout_rate"], 1.0)
        self.assertEqual(metrics["summary"]["malformed_rate"], 0.0)
        self.assertEqual(metrics["details"][0]["classification"], "timeout")

    def test_evaluate_static_spots_counts_validation_illegal(self):
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
        responses = [{"schema_version": "1.0", "request_id": "s1", "action": {"type": "call", "amount_to_bb": 2}}]

        metrics = evaluate_static_spots(spots, responses)

        self.assertEqual(metrics["summary"]["illegal_action_rate"], 1.0)
        self.assertEqual(metrics["details"][0]["classification"], "illegal")

    def test_public_dev_spots_are_expanded_and_toy_labeled(self):
        spots = list(load_jsonl(DEV_SPOTS_PATH))

        self.assertGreaterEqual(len(spots), 20)
        self.assertTrue(all(spot.get("tags", {}).get("toy") is True for spot in spots))
        self.assertGreaterEqual(len({spot["street"] for spot in spots}), 4)


if __name__ == "__main__":
    unittest.main()
