import unittest

from pokerbench_ng.agents.protocol import AgentAction, AgentResponse
from pokerbench_ng.bots.call_check import CallCheckBot
from pokerbench_ng.rollout.match import run_hand, run_match


class OverraiseAgent:
    def act(self, request):
        return AgentResponse(request.schema_version, request.request_id, AgentAction("raise", 1000.0))


class ClassifiedError(RuntimeError):
    classification = "timeout"


class TimeoutAgent:
    def act(self, request):
        raise ClassifiedError("simulated timeout")


class RolloutMatchTests(unittest.TestCase):
    def test_invalid_raise_amount_is_classified_and_falls_back(self):
        hand = run_hand(7, OverraiseAgent(), CallCheckBot())

        self.assertEqual(hand["events"][0]["classification"], "illegal")
        self.assertEqual(hand["events"][0]["action"]["type"], "fold")
        self.assertEqual(hand["terminal_reason"], "fold")

    def test_adapter_classification_is_preserved(self):
        hand = run_hand(8, TimeoutAgent(), CallCheckBot())

        self.assertEqual(hand["events"][0]["classification"], "timeout")
        self.assertEqual(hand["events"][0]["action"]["type"], "fold")

    def test_agent_can_play_big_blind(self):
        hand = run_hand(9, CallCheckBot(), CallCheckBot(), agent_seat="BB")

        self.assertEqual(hand["seat_assignment"], {"agent": "BB", "opponent": "SB"})
        self.assertIn("agent", hand["net_bb"])
        self.assertEqual(hand["net_bb"]["agent"], hand["net_bb_by_seat"]["BB"])
        self.assertTrue(any(event["actor_role"] == "agent" and event["seat"] == "BB" for event in hand["events"]))

    def test_match_alternates_agent_seats(self):
        metrics = run_match(CallCheckBot(), CallCheckBot(), [1, 2, 3, 4])
        seats = [hand["seat_assignment"]["agent"] for hand in metrics["hands_detail"]]

        self.assertEqual(seats, ["SB", "BB", "SB", "BB"])

    def test_rejects_invalid_agent_seat(self):
        with self.assertRaises(ValueError):
            run_hand(10, CallCheckBot(), CallCheckBot(), agent_seat="button")


if __name__ == "__main__":
    unittest.main()
