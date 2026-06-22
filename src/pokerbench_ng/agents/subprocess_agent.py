"""Subprocess agent adapter boundary."""

from __future__ import annotations

import json
import subprocess
from typing import Sequence

from pokerbench_ng.agents.protocol import AgentRequest, AgentResponse


class SubprocessAgentError(RuntimeError):
    def __init__(self, classification: str, message: str) -> None:
        super().__init__(message)
        self.classification = classification


class SubprocessAgentAdapter:
    """Send AgentRequest JSON on stdin and parse AgentResponse JSON from stdout."""

    def __init__(self, command: Sequence[str], timeout_seconds: float = 5.0) -> None:
        if not command:
            raise ValueError("command cannot be empty")
        self.command = list(command)
        self.timeout_seconds = timeout_seconds

    def act(self, request: AgentRequest) -> AgentResponse:
        try:
            completed = subprocess.run(
                self.command,
                input=request.to_json(),
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise SubprocessAgentError("timeout", "agent subprocess timed out") from exc
        if completed.returncode != 0:
            raise SubprocessAgentError(
                "process_error",
                f"agent subprocess exited with code {completed.returncode}: {completed.stderr.strip()}",
            )
        try:
            return AgentResponse.from_json(completed.stdout)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise SubprocessAgentError("malformed", "agent subprocess returned malformed JSON") from exc


def adapter_status() -> str:
    return "subprocess agent adapter scaffolded"
