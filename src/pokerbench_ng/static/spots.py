"""Static spot loading boundary."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterator


def load_jsonl(path: Path) -> Iterator[Dict[str, Any]]:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            yield json.loads(line)

