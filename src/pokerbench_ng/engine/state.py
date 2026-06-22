"""Typed game-state primitives for the HUNL engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class Street(str, Enum):
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"


@dataclass(frozen=True)
class PlayerState:
    player_id: str
    seat: str
    stack_bb: float
    hole_cards: tuple[str, str] = ("", "")
    street_contribution_bb: float = 0.0
    hand_contribution_bb: float = 0.0
    status: str = "active"


@dataclass(frozen=True)
class GameState:
    hand_id: str
    street: Street
    pot_bb: float
    actor_seat: str
    players: tuple[PlayerState, ...]
    board: tuple[str, ...] = ()
    button_seat: str = "SB"
    current_bet_to_bb: float = 0.0
    min_raise_increment_bb: float = 1.0
    pending_seats: tuple[str, ...] = ()
    terminal: bool = False
    terminal_reason: str | None = None

    def to_jsonable(self) -> dict[str, Any]:
        data = asdict(self)
        data["street"] = self.street.value
        return data

    def player(self, seat: str) -> PlayerState:
        for player in self.players:
            if player.seat == seat:
                return player
        raise KeyError(f"unknown seat: {seat}")
