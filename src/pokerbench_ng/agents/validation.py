"""Validation helpers for agent manifests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from pokerbench_ng.agents.protocol import (
    VALID_TRACK_CLASSES,
    AgentAction,
    AgentLegalAction,
    AgentRequest,
    AgentResponse,
    validate_action,
)


def load_agent_manifest(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return _load_minimal_yaml(text)


def _load_minimal_yaml(text: str) -> Dict[str, Any]:
    """Parse the tiny YAML subset used by starter manifests.

    This avoids adding PyYAML before the bootstrap is useful. It supports nested
    dictionaries via two-space indentation and string scalar values.
    """
    root: Dict[str, Any] = {}
    stack = [(0, root)]
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, sep, value = line.strip().partition(":")
        if not sep:
            raise ValueError(f"invalid manifest line: {raw_line}")
        while stack and indent < stack[-1][0]:
            stack.pop()
        current = stack[-1][1]
        if value.strip() == "":
            child: Dict[str, Any] = {}
            current[key] = child
            stack.append((indent + 2, child))
        else:
            current[key] = value.strip().strip('"').strip("'")
    return root


def validate_agent_manifest(manifest: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if manifest.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    agent = manifest.get("agent")
    if not isinstance(agent, dict):
        return errors + ["agent must be an object"]
    for field in ("name", "version", "track_class", "entrypoint"):
        if not agent.get(field):
            errors.append(f"agent.{field} is required")
    if agent.get("track_class") not in VALID_TRACK_CLASSES:
        errors.append("agent.track_class must be model_only, agent, or tool_assisted")
    return errors


def validate_agent_request(request: AgentRequest) -> List[str]:
    errors: List[str] = []
    if request.schema_version != "1.0":
        errors.append("schema_version must be 1.0")
    if not request.request_id:
        errors.append("request_id is required")
    if not request.legal_actions:
        errors.append("legal_actions must not be empty")
    return errors


def validate_agent_response(request: AgentRequest, response: AgentResponse) -> List[str]:
    errors: List[str] = []
    if response.schema_version != request.schema_version:
        errors.append("response schema_version must match request")
    if response.request_id != request.request_id:
        errors.append("response request_id must match request")
    errors.extend(validate_action(response.action))
    matching_actions = [action for action in request.legal_actions if action.type == response.action.type]
    if not matching_actions:
        errors.append("response action must be legal for request")
    else:
        errors.extend(_validate_action_amount(response.action, matching_actions))
    return errors


def _validate_action_amount(action: AgentAction, legal_actions: List[AgentLegalAction]) -> List[str]:
    errors: List[str] = []
    amount = action.amount_to_bb
    if action.type in {"fold", "check"}:
        if amount is not None:
            errors.append(f"{action.type} must not include amount_to_bb")
        return errors

    if action.type == "call":
        if amount is None:
            return errors
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            return errors
        expected_amounts = [legal.amount_bb for legal in legal_actions if legal.amount_bb is not None]
        if expected_amounts and not any(_same_amount(amount, expected) for expected in expected_amounts):
            errors.append("call amount_to_bb must match legal call amount")
        return errors

    if action.type in {"bet", "raise"}:
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            return errors
        in_range = False
        for legal in legal_actions:
            if legal.min_to_bb is None or legal.max_to_bb is None:
                continue
            if amount + 1e-9 >= legal.min_to_bb and amount - 1e-9 <= legal.max_to_bb:
                in_range = True
                break
        if not in_range:
            errors.append(f"{action.type} amount_to_bb must be within legal bounds")
    return errors


def _same_amount(left: float, right: float) -> bool:
    return abs(float(left) - float(right)) <= 1e-9
