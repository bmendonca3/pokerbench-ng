"""Random legal baseline bot."""

from __future__ import annotations

import random
from typing import Sequence

from pokerbench_ng.agents.protocol import AgentRequest, AgentResponse, action_from_legal_choice
from pokerbench_ng.engine.legal_actions import LegalAction


class RandomLegalBot:
    name = "RandomLegalBot"

    def __init__(self, seed: int = 0) -> None:
        self._rng = random.Random(seed)

    def choose(self, legal_actions: Sequence[LegalAction]) -> LegalAction:
        if not legal_actions:
            raise ValueError("legal_actions cannot be empty")
        return self._rng.choice(list(legal_actions))

    def act(self, request: AgentRequest) -> AgentResponse:
        action = self.choose(request.legal_actions)
        return AgentResponse(
            schema_version=request.schema_version,
            request_id=request.request_id,
            action=action_from_legal_choice(action),
            metadata={"bot": self.name},
        )
