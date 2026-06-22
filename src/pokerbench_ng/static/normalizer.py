"""Action normalization boundary for static evaluation."""

from __future__ import annotations


def normalize_action_type(action_type: str) -> str:
    return action_type.strip().lower()

