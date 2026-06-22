"""Duplicate-hand protocol boundary."""

from __future__ import annotations


def duplicate_group_id(seed: int) -> str:
    return f"dup_{seed:012d}"

