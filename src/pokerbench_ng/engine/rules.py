"""Ruleset definitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Ruleset:
    game: str = "NLHE"
    players: int = 2
    small_blind_bb: float = 0.5
    big_blind_bb: float = 1.0
    starting_stack_bb: float = 100.0
    ante_bb: float = 0.0


HUNL_100BB = Ruleset()

