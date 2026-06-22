"""Starter static EV-loss scoring helpers."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple

from pokerbench_ng.agents.protocol import AgentAction, AgentResponse


def ev_loss(best_ev_bb: float, chosen_ev_bb: float) -> float:
    return max(0.0, best_ev_bb - chosen_ev_bb)


def is_blunder(loss_bb: float, pot_bb: float) -> bool:
    return loss_bb >= max(0.25, 0.05 * pot_bb)


def evaluate_static_spots(spots: Iterable[Dict[str, Any]], responses: Iterable[AgentResponse | Dict[str, Any]]) -> Dict[str, Any]:
    spot_list = list(spots)
    response_list = [response if isinstance(response, AgentResponse) else AgentResponse.from_dict(response) for response in responses]
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
    }
    for spot, response in zip(spot_list, response_list):
        detail = score_static_response(spot, response)
        details.append(detail)
        totals["ev_loss"] += detail["ev_loss_bb"]
        totals["exact"] += int(detail["exact_action_agreement"])
        totals["near_best"] += int(detail["near_best_agreement"])
        totals["blunders"] += int(detail["blunder"])
        totals["illegal"] += int(detail["illegal"])
        totals["malformed"] += int(detail["malformed"])

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
        },
        "details": details,
    }


def score_static_response(spot: Dict[str, Any], response: AgentResponse) -> Dict[str, Any]:
    legal_types = {action["type"] for action in spot.get("legal_actions", [])}
    malformed = bool(response.request_id and response.schema_version != "1.0")
    illegal = response.action.type not in legal_types
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
    }


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
        data["amount_to_bb"] = round(float(amount), 6)
    return data


def _rate(count: int, total: int) -> float:
    return round(count / total, 6) if total else 0.0
