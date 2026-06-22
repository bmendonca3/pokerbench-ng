"""Markdown report helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def heading(title: str) -> str:
    return f"# {title}\n"


def render_markdown_report(metrics: Dict[str, Any]) -> str:
    summary = metrics.get("summary", {})
    lines = [heading("PokerBench-NG Report").strip(), "", f"Track: `{metrics.get('track', 'unknown')}`", ""]
    lines.append("## Summary")
    for key in sorted(summary):
        lines.append(f"- `{key}`: {summary[key]}")
    return "\n".join(lines) + "\n"


def write_markdown_report(path: Path, metrics: Dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown_report(metrics), encoding="utf-8")
    return path
