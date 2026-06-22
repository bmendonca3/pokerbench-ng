"""Card and deck primitives for clean-room poker evaluation."""

from __future__ import annotations

from dataclasses import dataclass
import random


RANKS = "23456789TJQKA"
SUITS = "cdhs"


@dataclass(frozen=True, order=True)
class Card:
    rank: str
    suit: str

    def __post_init__(self) -> None:
        if self.rank not in RANKS:
            raise ValueError(f"invalid rank: {self.rank}")
        if self.suit not in SUITS:
            raise ValueError(f"invalid suit: {self.suit}")

    @classmethod
    def parse(cls, text: str) -> "Card":
        if len(text) != 2:
            raise ValueError(f"card must use two characters: {text!r}")
        return cls(text[0], text[1])

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"


def full_deck() -> list[Card]:
    return [Card(rank, suit) for rank in RANKS for suit in SUITS]


def shuffled_deck(seed: int) -> list[Card]:
    deck = full_deck()
    rng = random.Random(seed)
    rng.shuffle(deck)
    return deck

