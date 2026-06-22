"""Small seven-card poker hand evaluator.

This evaluator is deliberately straightforward and dependency-free. It is good
enough for MVP rollouts and has tests for representative hand classes. A future
v1 can swap in a vetted high-performance adapter behind this boundary.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Iterable, Tuple


RANK_VALUE = {rank: index for index, rank in enumerate("23456789TJQKA", start=2)}


def best_five_rank(cards: Iterable[str]) -> Tuple[int, Tuple[int, ...]]:
    parsed = tuple(cards)
    if len(parsed) < 5:
        raise ValueError("at least five cards are required")
    return max(_five_card_rank(combo) for combo in combinations(parsed, 5))


def compare_hands(first: Iterable[str], second: Iterable[str]) -> int:
    first_rank = best_five_rank(first)
    second_rank = best_five_rank(second)
    return (first_rank > second_rank) - (first_rank < second_rank)


def _five_card_rank(cards: Iterable[str]) -> Tuple[int, Tuple[int, ...]]:
    ranks = sorted((RANK_VALUE[card[0]] for card in cards), reverse=True)
    suits = [card[1] for card in cards]
    counts = Counter(ranks)
    count_groups = sorted(((count, rank) for rank, count in counts.items()), reverse=True)
    is_flush = len(set(suits)) == 1
    straight_high = _straight_high(ranks)

    if is_flush and straight_high:
        return (8, (straight_high,))
    if count_groups[0][0] == 4:
        quad = count_groups[0][1]
        kicker = max(rank for rank in ranks if rank != quad)
        return (7, (quad, kicker))
    if count_groups[0][0] == 3 and count_groups[1][0] == 2:
        return (6, (count_groups[0][1], count_groups[1][1]))
    if is_flush:
        return (5, tuple(ranks))
    if straight_high:
        return (4, (straight_high,))
    if count_groups[0][0] == 3:
        trips = count_groups[0][1]
        kickers = tuple(rank for rank in ranks if rank != trips)
        return (3, (trips,) + kickers)
    if count_groups[0][0] == 2 and count_groups[1][0] == 2:
        high_pair = max(count_groups[0][1], count_groups[1][1])
        low_pair = min(count_groups[0][1], count_groups[1][1])
        kicker = max(rank for rank in ranks if rank not in {high_pair, low_pair})
        return (2, (high_pair, low_pair, kicker))
    if count_groups[0][0] == 2:
        pair = count_groups[0][1]
        kickers = tuple(rank for rank in ranks if rank != pair)
        return (1, (pair,) + kickers)
    return (0, tuple(ranks))


def _straight_high(ranks: Iterable[int]) -> int | None:
    unique = sorted(set(ranks), reverse=True)
    if 14 in unique:
        unique.append(1)
    for window in zip(unique, unique[1:], unique[2:], unique[3:], unique[4:]):
        if window[0] - window[4] == 4 and len(set(window)) == 5:
            return 5 if window[0] == 14 and window[1] == 5 else window[0]
    return None
