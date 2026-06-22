"""In-process Python agent adapter boundary."""

from __future__ import annotations

import importlib
from types import ModuleType
from typing import Any, Callable, Union

from pokerbench_ng.agents.protocol import AgentRequest, AgentResponse


PythonAgentTarget = Union[str, ModuleType, Callable[[dict], Any], object]


class PythonAgentAdapter:
    """Call an in-process Python object, function, or module-level act()."""

    def __init__(self, target: PythonAgentTarget) -> None:
        if isinstance(target, str):
            target = importlib.import_module(target)
        self.target = target

    def act(self, request: AgentRequest) -> AgentResponse:
        callable_target = self._resolve_callable()
        result = callable_target(request.to_dict())
        if isinstance(result, AgentResponse):
            return result
        return AgentResponse.from_dict(result)

    def _resolve_callable(self) -> Callable[[dict], Any]:
        if isinstance(self.target, ModuleType):
            candidate = getattr(self.target, "act", None)
        elif callable(self.target) and not hasattr(self.target, "act"):
            candidate = self.target
        else:
            candidate = getattr(self.target, "act", None)
        if not callable(candidate):
            raise TypeError("python agent target must be callable or expose act(request_dict)")
        return candidate


def adapter_status() -> str:
    return "python agent adapter scaffolded"
