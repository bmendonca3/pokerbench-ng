"""Rollout scoring helpers."""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List


def bb_per_100(total_net_bb: float, hands: int) -> float:
    if hands <= 0:
        raise ValueError("hands must be positive")
    return 100.0 * total_net_bb / hands


def aggregate_rollout(hand_summaries: Iterable[Dict[str, Any]], agent_key: str = "agent") -> Dict[str, Any]:
    hands = list(hand_summaries)
    nets: List[float] = [float(hand.get("net_bb", {}).get(agent_key, 0.0)) for hand in hands]
    total = sum(nets)
    mean = total / len(nets) if nets else 0.0
    ci_half = _normal_ci_half_width(nets)
    return {
        "schema_version": "1.0",
        "benchmark_version": "0.1.0",
        "track": "controlled_rollout_hunl_dev",
        "summary": {
            "hands": len(nets),
            "total_net_bb": round(total, 6),
            "controlled_bb_per_100": round(bb_per_100(total, len(nets)), 6) if nets else 0.0,
            "controlled_bb_per_100_ci95": [
                round(bb_per_100((mean - ci_half) * len(nets), len(nets)), 6) if nets else 0.0,
                round(bb_per_100((mean + ci_half) * len(nets), len(nets)), 6) if nets else 0.0,
            ],
        },
        "hands_detail": hands,
    }


def _normal_ci_half_width(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return 1.96 * math.sqrt(variance / len(values))
