"""Example random subprocess agent."""

from __future__ import annotations

import random
import sys

from pokerbench_ng.agents.protocol import AgentRequest, AgentResponse, action_from_legal_choice


def act(request_dict):
    request = AgentRequest.from_dict(request_dict)
    if not request.legal_actions:
        raise ValueError("legal_actions cannot be empty")
    seed = request.metadata.get("seed", request.request_id)
    action = random.Random(str(seed)).choice(request.legal_actions)
    return AgentResponse(
        schema_version=request.schema_version,
        request_id=request.request_id,
        action=action_from_legal_choice(action),
        metadata={"agent": "python_random_agent"},
    ).to_dict()


def main() -> int:
    request = AgentRequest.from_json(sys.stdin.read())
    response = AgentResponse.from_dict(act(request.to_dict()))
    sys.stdout.write(response.to_json())
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
