"""JSON report helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def to_pretty_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def write_json_report(path: Path, data: Dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_pretty_json(data) + "\n", encoding="utf-8")
    return path
