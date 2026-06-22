"""Agent protocol dataclasses for PokerBench-NG."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class AgentAction:
    type: str
    amount_to_bb: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentAction":
        return cls(type=str(data["type"]), amount_to_bb=data.get("amount_to_bb"))

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {"type": self.type}
        if self.amount_to_bb is not None:
            data["amount_to_bb"] = self.amount_to_bb
        return data


@dataclass(frozen=True)
class AgentLegalAction:
    type: str
    amount_bb: Optional[float] = None
    min_to_bb: Optional[float] = None
    max_to_bb: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentLegalAction":
        return cls(
            type=str(data["type"]),
            amount_bb=data.get("amount_bb"),
            min_to_bb=data.get("min_to_bb"),
            max_to_bb=data.get("max_to_bb"),
        )

    @classmethod
    def from_legal_action(cls, action: Any) -> "AgentLegalAction":
        return cls(
            type=str(action.type),
            amount_bb=getattr(action, "amount_bb", None),
            min_to_bb=getattr(action, "min_to_bb", None),
            max_to_bb=getattr(action, "max_to_bb", None),
        )

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {"type": self.type}
        if self.amount_bb is not None:
            data["amount_bb"] = self.amount_bb
        if self.min_to_bb is not None:
            data["min_to_bb"] = self.min_to_bb
        if self.max_to_bb is not None:
            data["max_to_bb"] = self.max_to_bb
        return data


def action_from_legal_choice(action: AgentLegalAction) -> AgentAction:
    """Convert an evaluator-provided legal action into an agent response action."""
    if action.type in {"call"}:
        return AgentAction(action.type, action.amount_bb)
    if action.type in {"bet", "raise"}:
        amount = action.min_to_bb if action.min_to_bb is not None else action.max_to_bb
        return AgentAction(action.type, amount)
    return AgentAction(action.type)


@dataclass(frozen=True)
class AgentRequest:
    schema_version: str
    request_id: str
    legal_actions: List[AgentLegalAction]
    state: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentRequest":
        legal_actions = [
            action
            if isinstance(action, AgentLegalAction)
            else AgentLegalAction.from_dict(action)
            for action in data.get("legal_actions", [])
        ]
        return cls(
            schema_version=str(data["schema_version"]),
            request_id=str(data["request_id"]),
            legal_actions=legal_actions,
            state=dict(data.get("state", {})),
            metadata=dict(data.get("metadata", {})),
        )

    @classmethod
    def from_json(cls, text: str) -> "AgentRequest":
        return cls.from_dict(json.loads(text))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "legal_actions": [action.to_dict() for action in self.legal_actions],
            "state": dict(self.state),
            "metadata": dict(self.metadata),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"), sort_keys=True)


@dataclass(frozen=True)
class AgentResponse:
    schema_version: str
    request_id: str
    action: AgentAction
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentResponse":
        action = data["action"]
        if not isinstance(action, AgentAction):
            action = AgentAction.from_dict(action)
        return cls(
            schema_version=str(data["schema_version"]),
            request_id=str(data["request_id"]),
            action=action,
            confidence=data.get("confidence"),
            metadata=dict(data.get("metadata", {})),
        )

    @classmethod
    def from_json(cls, text: str) -> "AgentResponse":
        return cls.from_dict(json.loads(text))

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "schema_version": self.schema_version,
            "request_id": self.request_id,
            "action": self.action.to_dict(),
            "metadata": dict(self.metadata),
        }
        if self.confidence is not None:
            data["confidence"] = self.confidence
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"), sort_keys=True)


@dataclass(frozen=True)
class AgentManifest:
    name: str
    version: str
    track_class: str
    entrypoint: str


VALID_TRACK_CLASSES = {"model_only", "agent", "tool_assisted"}
VALID_ACTION_TYPES = {"fold", "check", "call", "bet", "raise", "all_in"}


def validate_action(action: AgentAction) -> List[str]:
    errors: List[str] = []
    if action.type not in VALID_ACTION_TYPES:
        errors.append(f"unknown action type: {action.type}")
    if action.type in {"bet", "raise"} and action.amount_to_bb is None:
        errors.append(f"{action.type} requires amount_to_bb")
    if action.amount_to_bb is not None and not _is_number(action.amount_to_bb):
        errors.append("amount_to_bb must be numeric")
    if _is_number(action.amount_to_bb) and action.amount_to_bb < 0:
        errors.append("amount_to_bb cannot be negative")
    return errors


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)
