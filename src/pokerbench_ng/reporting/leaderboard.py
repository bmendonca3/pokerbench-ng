"""Leaderboard artifact boundary."""

from __future__ import annotations

from typing import Any, Dict


def leaderboard_status() -> str:
    return "leaderboard builder scaffolded"


def leaderboard_entry(metrics: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
    summary = metrics.get("summary", {})
    entry = {
        "schema_version": "1.0",
        "benchmark_version": metrics.get("benchmark_version", "0.1.0"),
        "track_id": metrics.get("track", "unknown"),
        "agent_name": agent_name,
        "primary_score": _primary_score(summary),
        "summary": summary,
    }
    if "reproducibility" in metrics:
        entry["reproducibility"] = metrics["reproducibility"]
    return entry


def _primary_score(summary: Dict[str, Any]) -> float:
    if "static_ev_loss_bb_per_decision" in summary:
        loss = float(summary["static_ev_loss_bb_per_decision"])
        return round(max(0.0, 100.0 * (2.718281828 ** (-loss / 0.20))), 6)
    if "controlled_bb_per_100" in summary:
        return round(max(0.0, min(100.0, 50.0 + float(summary["controlled_bb_per_100"]) / 2.0)), 6)
    return 0.0
