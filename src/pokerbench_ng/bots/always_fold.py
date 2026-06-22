"""Always-fold baseline bot."""

from __future__ import annotations

from typing import Sequence

from pokerbench_ng.agents.protocol import AgentRequest, AgentResponse, action_from_legal_choice
from pokerbench_ng.engine.legal_actions import LegalAction


class AlwaysFoldBot:
    name = "AlwaysFoldBot"
    version = "0.1.0"

    def choose(self, legal_actions: Sequence[LegalAction]) -> LegalAction:
        for action in legal_actions:
            if action.type == "fold":
                return action
        for action in legal_actions:
            if action.type == "check":
                return action
        raise ValueError("no fold or check action available")

    def act(self, request: AgentRequest) -> AgentResponse:
        action = self.choose(request.legal_actions)
        return AgentResponse(
            schema_version=request.schema_version,
            request_id=request.request_id,
            action=action_from_legal_choice(action),
            metadata={"bot": self.name},
        )
