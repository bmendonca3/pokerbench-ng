"""Legal action model and starter generator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LegalAction:
    type: str
    amount_bb: Optional[float] = None
    min_to_bb: Optional[float] = None
    max_to_bb: Optional[float] = None


def starter_legal_actions(to_call_bb: float, min_raise_to_bb: float, max_raise_to_bb: float) -> list[LegalAction]:
    if to_call_bb < 0:
        raise ValueError("to_call_bb cannot be negative")
    actions: list[LegalAction] = []
    if to_call_bb == 0:
        actions.append(LegalAction("check"))
        actions.append(LegalAction("bet", min_to_bb=min_raise_to_bb, max_to_bb=max_raise_to_bb))
    else:
        actions.append(LegalAction("fold"))
        actions.append(LegalAction("call", amount_bb=to_call_bb))
        if max_raise_to_bb >= min_raise_to_bb:
            actions.append(LegalAction("raise", min_to_bb=min_raise_to_bb, max_to_bb=max_raise_to_bb))
    return actions
