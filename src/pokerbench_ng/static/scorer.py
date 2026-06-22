"""Starter static EV-loss scoring helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Tuple

from pokerbench_ng.agents.protocol import AgentAction, AgentLegalAction, AgentRequest, AgentResponse
from pokerbench_ng.agents.validation import validate_agent_response


@dataclass(frozen=True)
class EvaluatedResponse:
    response: AgentResponse
    classification: str | None = None


def ev_loss(best_ev_bb: float, chosen_ev_bb: float) -> float:
    return max(0.0, best_ev_bb - chosen_ev_bb)


def is_blunder(loss_bb: float, pot_bb: float) -> bool:
    return loss_bb >= max(0.25, 0.05 * pot_bb)


def evaluate_static_spots(
    spots: Iterable[Dict[str, Any]],
    responses: Iterable[AgentResponse | EvaluatedResponse | Dict[str, Any]],
) -> Dict[str, Any]:
    spot_list = list(spots)
    response_list = [_coerce_evaluated_response(response) for response in responses]
    if len(spot_list) != len(response_list):
        raise ValueError("spots and responses must have the same length")

    details: List[Dict[str, Any]] = []
    totals = {
        "ev_loss": 0.0,
        "exact": 0,
        "near_best": 0,
        "blunders": 0,
        "illegal": 0,
        "malformed": 0,
        "timeout": 0,
        "process_error": 0,
    }
    for spot, evaluated in zip(spot_list, response_list):
        detail = score_static_response(spot, evaluated.response, evaluated.classification)
        details.append(detail)
        totals["ev_loss"] += detail["ev_loss_bb"]
        totals["exact"] += int(detail["exact_action_agreement"])
        totals["near_best"] += int(detail["near_best_agreement"])
        totals["blunders"] += int(detail["blunder"])
        totals["illegal"] += int(detail["illegal"])
        totals["malformed"] += int(detail["malformed"])
        totals["timeout"] += int(detail["timeout"])
        totals["process_error"] += int(detail["process_error"])

    n = len(details)
    mean_loss = totals["ev_loss"] / n if n else 0.0
    return {
        "schema_version": "1.0",
        "benchmark_version": "0.1.0",
        "track": "static_hunl_dev",
        "summary": {
            "static_spots": n,
            "static_ev_loss_bb_per_decision": round(mean_loss, 6),
            "exact_action_agreement": _rate(totals["exact"], n),
            "near_best_agreement": _rate(totals["near_best"], n),
            "blunder_rate": _rate(totals["blunders"], n),
            "illegal_action_rate": _rate(totals["illegal"], n),
            "malformed_rate": _rate(totals["malformed"], n),
            "timeout_rate": _rate(totals["timeout"], n),
            "process_error_rate": _rate(totals["process_error"], n),
        },
        "details": details,
    }


def score_static_response(spot: Dict[str, Any], response: AgentResponse, classification: str | None = None) -> Dict[str, Any]:
    legal_types = {action["type"] for action in spot.get("legal_actions", [])}
    validation_errors = _validation_errors(spot, response)
    malformed = classification == "malformed" or any(
        error.startswith("response schema_version") or error.startswith("response request_id")
        for error in validation_errors
    )
    timeout = classification == "timeout"
    process_error = classification == "process_error"
    illegal = classification == "illegal" or response.action.type not in legal_types or any(
        not (
            error.startswith("response schema_version")
            or error.startswith("response request_id")
        )
        for error in validation_errors
    )
    best_ev = float(spot.get("best_ev_bb", _best_policy(spot)[1]))
    best_action = _normalize_action(spot.get("best_action", _best_policy(spot)[0]))
    chosen_ev = _chosen_ev(spot, response.action)
    loss = ev_loss(best_ev, chosen_ev)
    exact = _normalize_action(response.action.to_dict()) == best_action
    near_best = loss <= 0.02
    if illegal:
        loss = max(loss, max(1.0, 0.25 * float(spot.get("pot_bb", 1.0))))
    return {
        "spot_id": spot.get("spot_id", ""),
        "chosen_action": response.action.to_dict(),
        "best_action": best_action,
        "chosen_ev_bb": round(chosen_ev, 6),
        "best_ev_bb": round(best_ev, 6),
        "ev_loss_bb": round(loss, 6),
        "exact_action_agreement": exact,
        "near_best_agreement": near_best,
        "blunder": is_blunder(loss, float(spot.get("pot_bb", 1.0))),
        "illegal": illegal,
        "malformed": malformed,
        "timeout": timeout,
        "process_error": process_error,
        "classification": classification or ("illegal" if illegal else "ok"),
    }


def _coerce_evaluated_response(response: AgentResponse | EvaluatedResponse | Dict[str, Any]) -> EvaluatedResponse:
    if isinstance(response, EvaluatedResponse):
        return response
    if isinstance(response, AgentResponse):
        return EvaluatedResponse(response)
    if "response" in response:
        nested = response["response"]
        agent_response = nested if isinstance(nested, AgentResponse) else AgentResponse.from_dict(nested)
        return EvaluatedResponse(agent_response, response.get("classification"))
    return EvaluatedResponse(AgentResponse.from_dict(response))


def _validation_errors(spot: Dict[str, Any], response: AgentResponse) -> List[str]:
    request = AgentRequest(
        schema_version="1.0",
        request_id=str(spot.get("spot_id", "")),
        legal_actions=[AgentLegalAction.from_dict(action) for action in spot.get("legal_actions", [])],
    )
    return validate_agent_response(request, response)


def _best_policy(spot: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
    policy = spot.get("policy", [])
    if not policy:
        return {"type": "fold"}, 0.0
    best = max(policy, key=lambda row: float(row.get("ev_bb", 0.0)))
    return dict(best.get("action", {"type": "fold"})), float(best.get("ev_bb", 0.0))


def _chosen_ev(spot: Dict[str, Any], action: AgentAction) -> float:
    normalized = _normalize_action(action.to_dict())
    for row in spot.get("policy", []):
        if _normalize_action(row.get("action", {})) == normalized:
            return float(row.get("ev_bb", 0.0))
    # Match action type as a conservative fallback for toy policies.
    for row in spot.get("policy", []):
        if row.get("action", {}).get("type") == action.type:
            return float(row.get("ev_bb", 0.0))
    return 0.0


def _normalize_action(action: Dict[str, Any]) -> Dict[str, Any]:
    data = {"type": str(action.get("type", "")).lower()}
    amount = action.get("amount_to_bb", action.get("amount_bb"))
    if amount is not None:
        try:
            data["amount_to_bb"] = round(float(amount), 6)
        except (TypeError, ValueError):
            data["amount_to_bb"] = str(amount)
    return data


def _rate(count: int, total: int) -> float:
    return round(count / total, 6) if total else 0.0
