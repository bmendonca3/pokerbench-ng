import unittest

from pokerbench_ng.agents.protocol import AgentRequest
from pokerbench_ng.bots.always_fold import AlwaysFoldBot
from pokerbench_ng.bots.call_check import CallCheckBot
from pokerbench_ng.bots.random_legal import RandomLegalBot
from pokerbench_ng.engine.legal_actions import LegalAction


class BotTests(unittest.TestCase):
    def test_always_fold_prefers_fold(self):
        action = AlwaysFoldBot().choose([LegalAction("call", amount_bb=1), LegalAction("fold")])
        self.assertEqual(action.type, "fold")

    def test_call_check_prefers_check_then_call(self):
        self.assertEqual(CallCheckBot().choose([LegalAction("check")]).type, "check")
        self.assertEqual(CallCheckBot().choose([LegalAction("fold"), LegalAction("call", amount_bb=1)]).type, "call")

    def test_random_bot_is_seeded(self):
        actions = [LegalAction("fold"), LegalAction("call", amount_bb=1), LegalAction("raise", min_to_bb=3, max_to_bb=10)]
        first = [RandomLegalBot(seed=7).choose(actions) for _ in range(3)]
        second = [RandomLegalBot(seed=7).choose(actions) for _ in range(3)]
        self.assertEqual(first, second)

    def test_bots_return_agent_response(self):
        request = AgentRequest.from_dict(
            {
                "schema_version": "1.0",
                "request_id": "bot-req",
                "legal_actions": [{"type": "fold"}, {"type": "call", "amount_bb": 1}],
            }
        )
        response = AlwaysFoldBot().act(request)
        self.assertEqual(response.request_id, "bot-req")
        self.assertEqual(response.action.type, "fold")

    def test_call_check_response_uses_call_amount(self):
        request = AgentRequest.from_dict(
            {
                "schema_version": "1.0",
                "request_id": "bot-req",
                "legal_actions": [{"type": "fold"}, {"type": "call", "amount_bb": 1.5}],
            }
        )
        response = CallCheckBot().act(request)
        self.assertEqual(response.action.type, "call")
        self.assertEqual(response.action.amount_to_bb, 1.5)


if __name__ == "__main__":
    unittest.main()
