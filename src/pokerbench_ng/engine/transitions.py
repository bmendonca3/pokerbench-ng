"""Starter HUNL state transitions.

This is intentionally compact: it supports the first controlled-rollout slice
without pulling in a full poker framework. The invariants are explicit and
tested so later work can replace pieces safely.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from pokerbench_ng.engine.cards import shuffled_deck
from pokerbench_ng.engine.hand_eval import compare_hands
from pokerbench_ng.engine.legal_actions import LegalAction
from pokerbench_ng.engine.rules import HUNL_100BB, Ruleset
from pokerbench_ng.engine.state import GameState, PlayerState, Street


SEAT_ORDER = ("SB", "BB")
POSTFLOP_ORDER = ("BB", "SB")
STREET_SEQUENCE = (Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER)


def new_hunl_hand(seed: int, ruleset: Ruleset = HUNL_100BB) -> GameState:
    if ruleset.players != 2:
        raise ValueError("starter engine only supports heads-up play")
    deck = tuple(str(card) for card in shuffled_deck(seed))
    sb = PlayerState(
        player_id="agent_sb",
        seat="SB",
        stack_bb=ruleset.starting_stack_bb - ruleset.small_blind_bb,
        hole_cards=(deck[0], deck[2]),
        street_contribution_bb=ruleset.small_blind_bb,
        hand_contribution_bb=ruleset.small_blind_bb,
    )
    bb = PlayerState(
        player_id="agent_bb",
        seat="BB",
        stack_bb=ruleset.starting_stack_bb - ruleset.big_blind_bb,
        hole_cards=(deck[1], deck[3]),
        street_contribution_bb=ruleset.big_blind_bb,
        hand_contribution_bb=ruleset.big_blind_bb,
    )
    return GameState(
        hand_id=f"h_{seed:012d}",
        street=Street.PREFLOP,
        pot_bb=ruleset.small_blind_bb + ruleset.big_blind_bb,
        actor_seat="SB",
        players=(sb, bb),
        board=(),
        button_seat="SB",
        current_bet_to_bb=ruleset.big_blind_bb,
        min_raise_increment_bb=ruleset.big_blind_bb,
        pending_seats=("SB", "BB"),
    )


def total_chips(state: GameState) -> float:
    return round(state.pot_bb + sum(player.stack_bb for player in state.players), 6)


def legal_actions(state: GameState) -> list[LegalAction]:
    if state.terminal:
        return []
    actor = state.player(state.actor_seat)
    to_call = round(max(0.0, state.current_bet_to_bb - actor.street_contribution_bb), 6)
    max_to = round(actor.stack_bb + actor.street_contribution_bb, 6)
    actions: list[LegalAction] = []
    if to_call == 0:
        actions.append(LegalAction("check"))
        if actor.stack_bb > 0 and not _any_active_player_all_in(state):
            min_bet = state.current_bet_to_bb + state.min_raise_increment_bb
            actions.append(LegalAction("bet", min_to_bb=round(min_bet, 6), max_to_bb=max_to))
    else:
        actions.append(LegalAction("fold"))
        actions.append(LegalAction("call", amount_bb=min(to_call, actor.stack_bb)))
        min_raise_to = round(state.current_bet_to_bb + state.min_raise_increment_bb, 6)
        if max_to >= min_raise_to:
            actions.append(LegalAction("raise", min_to_bb=min_raise_to, max_to_bb=max_to))
    return actions


def apply_action(state: GameState, action: LegalAction) -> GameState:
    if state.terminal:
        raise ValueError("cannot act on terminal state")
    _assert_legal(state, action)
    if action.type == "fold":
        return _fold(state)
    if action.type == "check":
        return _passive_action(state)
    if action.type == "call":
        actor = state.player(state.actor_seat)
        to_call = max(0.0, state.current_bet_to_bb - actor.street_contribution_bb)
        call_delta = min(to_call, actor.stack_bb)
        return _commit_to(state, round(actor.street_contribution_bb + call_delta, 6), aggressive=False)
    if action.type in {"bet", "raise"}:
        amount_to = action.min_to_bb if action.amount_bb is None else action.amount_bb
        if amount_to is None:
            raise ValueError(f"{action.type} requires an amount")
        return _commit_to(state, amount_to, aggressive=True)
    raise ValueError(f"unsupported action type: {action.type}")


def _assert_legal(state: GameState, action: LegalAction) -> None:
    legal = legal_actions(state)
    for candidate in legal:
        if candidate.type != action.type:
            continue
        if action.type in {"bet", "raise"}:
            amount_to = action.min_to_bb if action.amount_bb is None else action.amount_bb
            if amount_to is None:
                continue
            if candidate.min_to_bb is not None and amount_to < candidate.min_to_bb:
                continue
            if candidate.max_to_bb is not None and amount_to > candidate.max_to_bb:
                continue
        return
    raise ValueError(f"illegal action for state: {action}")


def _fold(state: GameState) -> GameState:
    winner = _other_active_seat(state, state.actor_seat)
    players = []
    for player in state.players:
        if player.seat == state.actor_seat:
            players.append(replace(player, status="folded"))
        elif player.seat == winner:
            players.append(replace(player, stack_bb=round(player.stack_bb + state.pot_bb, 6)))
        else:
            players.append(player)
    return replace(
        state,
        pot_bb=0.0,
        players=tuple(players),
        pending_seats=(),
        terminal=True,
        terminal_reason="fold",
    )


def _passive_action(state: GameState) -> GameState:
    pending = tuple(seat for seat in state.pending_seats if seat != state.actor_seat)
    if not pending and _street_balanced(state):
        return _advance_street(state)
    return replace(state, actor_seat=_next_actor(state, pending), pending_seats=pending)


def _commit_to(state: GameState, amount_to_bb: float, aggressive: bool) -> GameState:
    actor = state.player(state.actor_seat)
    delta = round(amount_to_bb - actor.street_contribution_bb, 6)
    if delta < 0:
        raise ValueError("cannot reduce contribution")
    if delta > actor.stack_bb:
        raise ValueError("cannot commit more than stack")
    previous_bet = state.current_bet_to_bb
    updated_actor = replace(
        actor,
        stack_bb=round(actor.stack_bb - delta, 6),
        street_contribution_bb=round(actor.street_contribution_bb + delta, 6),
        hand_contribution_bb=round(actor.hand_contribution_bb + delta, 6),
    )
    players = tuple(updated_actor if player.seat == actor.seat else player for player in state.players)
    current_bet = round(max(state.current_bet_to_bb, updated_actor.street_contribution_bb), 6)
    min_raise_increment = state.min_raise_increment_bb
    pending = tuple(seat for seat in state.pending_seats if seat != actor.seat)
    if aggressive and current_bet > previous_bet:
        min_raise_increment = round(current_bet - previous_bet, 6)
        pending = tuple(player.seat for player in players if player.status == "active" and player.seat != actor.seat)
    next_state = replace(
        state,
        pot_bb=round(state.pot_bb + delta, 6),
        players=players,
        current_bet_to_bb=current_bet,
        min_raise_increment_bb=min_raise_increment,
        pending_seats=pending,
    )
    if not pending and _street_balanced(next_state):
        return _advance_street(next_state)
    return replace(next_state, actor_seat=_next_actor(next_state, pending))


def _advance_street(state: GameState) -> GameState:
    if state.street == Street.RIVER:
        return _showdown(state)
    next_street = STREET_SEQUENCE[STREET_SEQUENCE.index(state.street) + 1]
    board_cards = {Street.FLOP: 3, Street.TURN: 4, Street.RIVER: 5}[next_street]
    reset_players = tuple(
        replace(player, street_contribution_bb=0.0)
        for player in state.players
    )
    return replace(
        state,
        street=next_street,
        board=tuple(_deck_without_holes(state))[:board_cards],
        players=reset_players,
        actor_seat="BB",
        current_bet_to_bb=0.0,
        min_raise_increment_bb=HUNL_100BB.big_blind_bb,
        pending_seats=POSTFLOP_ORDER,
    )


def _street_balanced(state: GameState) -> bool:
    active = [player for player in state.players if player.status == "active"]
    if not active:
        return True
    if _any_active_player_all_in(state):
        return True
    contributions = {round(player.street_contribution_bb, 6) for player in active}
    return len(contributions) == 1


def _any_active_player_all_in(state: GameState) -> bool:
    return any(player.status == "active" and player.stack_bb == 0 for player in state.players)


def _next_actor(state: GameState, pending: Iterable[str]) -> str:
    pending_tuple = tuple(pending)
    if pending_tuple:
        return pending_tuple[0]
    return _other_active_seat(state, state.actor_seat)


def _other_active_seat(state: GameState, seat: str) -> str:
    for player in state.players:
        if player.seat != seat and player.status == "active":
            return player.seat
    raise ValueError("no other active player")


def _deck_without_holes(state: GameState) -> tuple[str, ...]:
    seed = int(state.hand_id.split("_", 1)[1])
    deck = tuple(str(card) for card in shuffled_deck(seed))
    return deck[4:]


def _showdown(state: GameState) -> GameState:
    active = [player for player in state.players if player.status == "active"]
    if len(active) != 2:
        return replace(state, terminal=True, terminal_reason="showdown", pending_seats=())
    board = tuple(state.board)
    comparison = compare_hands(active[0].hole_cards + board, active[1].hole_cards + board)
    if comparison == 0:
        share = round(state.pot_bb / 2.0, 6)
        players = tuple(
            replace(player, stack_bb=round(player.stack_bb + share, 6))
            if player.status == "active"
            else player
            for player in state.players
        )
    else:
        winner = active[0] if comparison > 0 else active[1]
        players = tuple(
            replace(player, stack_bb=round(player.stack_bb + state.pot_bb, 6))
            if player.seat == winner.seat
            else player
            for player in state.players
        )
    return replace(
        state,
        pot_bb=0.0,
        players=players,
        terminal=True,
        terminal_reason="showdown",
        pending_seats=(),
    )
