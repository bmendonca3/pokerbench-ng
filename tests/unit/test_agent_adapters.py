import sys
import tempfile
import textwrap
import types
import unittest
from pathlib import Path

from pokerbench_ng.agents.protocol import AgentAction, AgentRequest, AgentResponse
from pokerbench_ng.agents.python_agent import PythonAgentAdapter
from pokerbench_ng.agents.subprocess_agent import SubprocessAgentAdapter, SubprocessAgentError


def make_request():
    return AgentRequest.from_dict(
        {
            "schema_version": "1.0",
            "request_id": "adapter-req",
            "legal_actions": [{"type": "check"}, {"type": "bet", "min_to_bb": 2, "max_to_bb": 8}],
        }
    )


class PythonAgentAdapterTests(unittest.TestCase):
    def test_calls_function_target(self):
        def act(request_dict):
            return {
                "schema_version": request_dict["schema_version"],
                "request_id": request_dict["request_id"],
                "action": {"type": "check"},
            }

        response = PythonAgentAdapter(act).act(make_request())
        self.assertEqual(response, AgentResponse("1.0", "adapter-req", AgentAction("check")))

    def test_calls_object_act(self):
        class Agent:
            def act(self, request_dict):
                return {
                    "schema_version": request_dict["schema_version"],
                    "request_id": request_dict["request_id"],
                    "action": {"type": "check"},
                }

        response = PythonAgentAdapter(Agent()).act(make_request())
        self.assertEqual(response.action.type, "check")

    def test_calls_module_level_act(self):
        module = types.ModuleType("test_agent_module")

        def act(request_dict):
            return {
                "schema_version": request_dict["schema_version"],
                "request_id": request_dict["request_id"],
                "action": {"type": "check"},
            }

        module.act = act
        response = PythonAgentAdapter(module).act(make_request())
        self.assertEqual(response.action.type, "check")


class SubprocessAgentAdapterTests(unittest.TestCase):
    def test_parses_stdout_response(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            script = Path(tmpdir) / "agent.py"
            script.write_text(
                textwrap.dedent(
                    """
                    import json
                    import sys

                    request = json.loads(sys.stdin.read())
                    print(json.dumps({
                        "schema_version": request["schema_version"],
                        "request_id": request["request_id"],
                        "action": {"type": "check"},
                    }))
                    """
                ),
                encoding="utf-8",
            )
            response = SubprocessAgentAdapter([sys.executable, str(script)]).act(make_request())
        self.assertEqual(response.action.type, "check")

    def test_classifies_malformed_stdout(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            script = Path(tmpdir) / "agent.py"
            script.write_text("print('not-json')\n", encoding="utf-8")
            with self.assertRaises(SubprocessAgentError) as caught:
                SubprocessAgentAdapter([sys.executable, str(script)]).act(make_request())
        self.assertEqual(caught.exception.classification, "malformed")

    def test_classifies_timeout(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            script = Path(tmpdir) / "agent.py"
            script.write_text("import time; time.sleep(1)\n", encoding="utf-8")
            with self.assertRaises(SubprocessAgentError) as caught:
                SubprocessAgentAdapter([sys.executable, str(script)], timeout_seconds=0.01).act(make_request())
        self.assertEqual(caught.exception.classification, "timeout")


if __name__ == "__main__":
    unittest.main()
