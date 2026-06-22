import unittest
from pathlib import Path

from pokerbench_ng.agents.protocol import AgentAction, AgentRequest, AgentResponse, validate_action
from pokerbench_ng.agents.validation import (
    load_agent_manifest,
    validate_agent_manifest,
    validate_agent_response,
)


ROOT = Path(__file__).resolve().parents[2]


class ProtocolTests(unittest.TestCase):
    def test_valid_manifest(self):
        manifest = load_agent_manifest(ROOT / "examples/agents/python_random_agent/agent.yaml")
        self.assertEqual(validate_agent_manifest(manifest), [])

    def test_invalid_track_class(self):
        manifest = {
            "schema_version": "1.0",
            "agent": {
                "name": "BadAgent",
                "version": "0",
                "track_class": "mixed",
                "entrypoint": "python agent.py",
            },
        }
        self.assertIn(
            "agent.track_class must be model_only, agent, or tool_assisted",
            validate_agent_manifest(manifest),
        )

    def test_raise_requires_amount(self):
        self.assertEqual(validate_action(AgentAction("raise")), ["raise requires amount_to_bb"])

    def test_request_json_round_trip(self):
        request = AgentRequest.from_dict(
            {
                "schema_version": "1.0",
                "request_id": "req-1",
                "legal_actions": [{"type": "call", "amount_bb": 2.5}, {"type": "fold"}],
                "state": {"street": "flop"},
                "metadata": {"seat": 0},
            }
        )
        self.assertEqual(AgentRequest.from_json(request.to_json()), request)

    def test_response_json_round_trip(self):
        response = AgentResponse("1.0", "req-1", AgentAction("call", 2.5), confidence=0.75)
        self.assertEqual(AgentResponse.from_json(response.to_json()), response)

    def test_response_validation_rejects_illegal_action(self):
        request = AgentRequest.from_dict(
            {"schema_version": "1.0", "request_id": "req-1", "legal_actions": [{"type": "fold"}]}
        )
        response = AgentResponse("1.0", "req-1", AgentAction("call", 1))
        self.assertIn("response action must be legal for request", validate_agent_response(request, response))


if __name__ == "__main__":
    unittest.main()
