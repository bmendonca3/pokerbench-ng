"""Rollout scheduler boundary."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def scheduler_status() -> str:
    return "scheduler scaffolded"


def seed_schedule(count: int, start_seed: int = 1) -> List[int]:
    if count <= 0:
        raise ValueError("count must be positive")
    return list(range(start_seed, start_seed + count))


def load_seed_manifest(path: Path) -> List[int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [int(seed) for seed in data.get("seeds", [])]


def load_rollout_config(path: Path) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if sep:
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data
