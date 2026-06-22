"""Rollout match boundary."""

from __future__ import annotations

from typing import Any, Dict, List

from pokerbench_ng.agents.protocol import AgentAction, AgentLegalAction, AgentRequest, AgentResponse
from pokerbench_ng.agents.validation import validate_agent_response
from pokerbench_ng.engine.legal_actions import LegalAction
from pokerbench_ng.engine.transitions import apply_action, legal_actions, new_hunl_hand
from pokerbench_ng.rollout.scorer import aggregate_rollout


def match_runner_status() -> str:
    return "match runner scaffolded"


def run_hand(seed: int, agent: Any, opponent: Any, max_actions: int = 128) -> Dict[str, Any]:
    state = new_hunl_hand(seed)
    actors = {"SB": agent, "BB": opponent}
    starting = {player.seat: player.stack_bb + player.hand_contribution_bb for player in state.players}
    events: List[Dict[str, Any]] = []
    for action_index in range(max_actions):
        if state.terminal:
            break
        request = _request_from_state(state, action_index)
        actor = actors[state.actor_seat]
        response, classification = _safe_act(actor, request)
        if classification or validate_agent_response(request, response):
            classification = classification or "illegal"
            response = _fallback_response(request)
        engine_action = _engine_action(response)
        before_seat = state.actor_seat
        state = apply_action(state, engine_action)
        events.append(
            {
                "index": action_index,
                "seat": before_seat,
                "action": response.action.to_dict(),
                "classification": classification or "ok",
                "street": request.state.get("street"),
            }
        )
    if not state.terminal:
        raise RuntimeError("hand did not terminate within max_actions")
    ending = {player.seat: player.stack_bb for player in state.players}
    net_by_seat = {seat: round(ending[seat] - starting[seat], 6) for seat in starting}
    return {
        "hand_id": state.hand_id,
        "seed": seed,
        "terminal_reason": state.terminal_reason,
        "board": list(state.board),
        "action_count": len(events),
        "events": events,
        "net_bb": {"agent": net_by_seat["SB"], "opponent": net_by_seat["BB"]},
    }


def run_match(agent: Any, opponent: Any, seeds: List[int]) -> Dict[str, Any]:
    hands = [run_hand(seed, agent, opponent) for seed in seeds]
    return aggregate_rollout(hands)


def _request_from_state(state: Any, action_index: int) -> AgentRequest:
    return AgentRequest(
        schema_version="1.0",
        request_id=f"{state.hand_id}:{action_index}",
        legal_actions=[AgentLegalAction.from_legal_action(action) for action in legal_actions(state)],
        state={
            "hand_id": state.hand_id,
            "street": state.street.value,
            "actor_seat": state.actor_seat,
            "pot_bb": state.pot_bb,
            "board": list(state.board),
        },
        metadata={"seed": state.hand_id, "action_index": action_index},
    )


def _safe_act(actor: Any, request: AgentRequest) -> tuple[AgentResponse, str | None]:
    try:
        response = actor.act(request)
        if not isinstance(response, AgentResponse):
            response = AgentResponse.from_dict(response)
        return response, None
    except Exception:
        return _fallback_response(request), "malformed"


def _fallback_response(request: AgentRequest) -> AgentResponse:
    for preferred in ("check", "fold", "call"):
        for action in request.legal_actions:
            if action.type == preferred:
                amount = action.amount_bb if preferred == "call" else None
                return AgentResponse("1.0", request.request_id, AgentAction(preferred, amount))
    first = request.legal_actions[0]
    amount = first.amount_bb or first.min_to_bb
    return AgentResponse("1.0", request.request_id, AgentAction(first.type, amount))


def _engine_action(response: AgentResponse) -> LegalAction:
    return LegalAction(response.action.type, amount_bb=response.action.amount_to_bb)
