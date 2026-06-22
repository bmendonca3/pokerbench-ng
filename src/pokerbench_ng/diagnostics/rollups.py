"""Diagnostic rollup helpers."""

from __future__ import annotations


def mean(values: list[float]) -> float:
    if not values:
        raise ValueError("values cannot be empty")
    return sum(values) / len(values)

