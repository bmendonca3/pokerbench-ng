"""Diagnostic tag helpers."""

from __future__ import annotations


def normalize_tag(tag: str) -> str:
    return tag.strip().lower().replace(" ", "_")

