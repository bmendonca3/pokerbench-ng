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

    def test_response_validation_rejects_raise_outside_bounds(self):
        request = AgentRequest.from_dict(
            {
                "schema_version": "1.0",
                "request_id": "req-1",
                "legal_actions": [{"type": "raise", "min_to_bb": 4.0, "max_to_bb": 12.0}],
            }
        )
        too_small = AgentResponse("1.0", "req-1", AgentAction("raise", 3.5))
        too_large = AgentResponse("1.0", "req-1", AgentAction("raise", 20.0))
        self.assertIn(
            "raise amount_to_bb must be within legal bounds",
            validate_agent_response(request, too_small),
        )
        self.assertIn(
            "raise amount_to_bb must be within legal bounds",
            validate_agent_response(request, too_large),
        )

    def test_response_validation_accepts_raise_on_bounds(self):
        request = AgentRequest.from_dict(
            {
                "schema_version": "1.0",
                "request_id": "req-1",
                "legal_actions": [{"type": "raise", "min_to_bb": 4.0, "max_to_bb": 12.0}],
            }
        )
        self.assertEqual(validate_agent_response(request, AgentResponse("1.0", "req-1", AgentAction("raise", 4.0))), [])
        self.assertEqual(validate_agent_response(request, AgentResponse("1.0", "req-1", AgentAction("raise", 12.0))), [])

    def test_response_validation_rejects_mismatched_call_amount(self):
        request = AgentRequest.from_dict(
            {
                "schema_version": "1.0",
                "request_id": "req-1",
                "legal_actions": [{"type": "fold"}, {"type": "call", "amount_bb": 2.5}],
            }
        )
        response = AgentResponse("1.0", "req-1", AgentAction("call", 3.0))
        self.assertIn(
            "call amount_to_bb must match legal call amount",
            validate_agent_response(request, response),
        )

    def test_response_validation_rejects_non_numeric_amount(self):
        request = AgentRequest.from_dict(
            {
                "schema_version": "1.0",
                "request_id": "req-1",
                "legal_actions": [{"type": "raise", "min_to_bb": 4.0, "max_to_bb": 12.0}],
            }
        )
        response = AgentResponse("1.0", "req-1", AgentAction("raise", "big"))
        self.assertIn("amount_to_bb must be numeric", validate_agent_response(request, response))


if __name__ == "__main__":
    unittest.main()
