"""Validation helpers for agent manifests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from pokerbench_ng.agents.protocol import VALID_TRACK_CLASSES, AgentRequest, AgentResponse, validate_action


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
    legal_types = {action.type for action in request.legal_actions}
    if response.action.type not in legal_types:
        errors.append("response action must be legal for request")
    return errors
