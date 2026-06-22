import unittest
from dataclasses import replace

from pokerbench_ng.engine.legal_actions import LegalAction
from pokerbench_ng.engine.state import Street
from pokerbench_ng.engine.transitions import apply_action, legal_actions, new_hunl_hand, total_chips


class TransitionTests(unittest.TestCase):
    def test_postflop_checks_advance_streets(self):
        state = new_hunl_hand(seed=5)
        state = apply_action(state, LegalAction("call", amount_bb=0.5))
        state = apply_action(state, LegalAction("check"))
        self.assertEqual(state.street, Street.FLOP)
        state = apply_action(state, LegalAction("check"))
        state = apply_action(state, LegalAction("check"))
        self.assertEqual(state.street, Street.TURN)
        self.assertEqual(len(state.board), 4)
        state = apply_action(state, LegalAction("check"))
        state = apply_action(state, LegalAction("check"))
        self.assertEqual(state.street, Street.RIVER)
        self.assertEqual(len(state.board), 5)
        state = apply_action(state, LegalAction("check"))
        state = apply_action(state, LegalAction("check"))
        self.assertTrue(state.terminal)
        self.assertEqual(state.terminal_reason, "showdown")
        self.assertEqual(state.pot_bb, 0.0)
        self.assertEqual(total_chips(state), 200.0)

    def test_illegal_action_rejected(self):
        state = new_hunl_hand(seed=6)
        with self.assertRaises(ValueError):
            apply_action(state, LegalAction("check"))

    def test_postflop_bet_then_fold_awards_pot(self):
        state = new_hunl_hand(seed=7)
        state = apply_action(state, LegalAction("call", amount_bb=0.5))
        state = apply_action(state, LegalAction("check"))
        self.assertEqual([action.type for action in legal_actions(state)], ["check", "bet"])
        state = apply_action(state, LegalAction("bet", amount_bb=2.0))
        self.assertEqual(state.actor_seat, "SB")
        state = apply_action(state, LegalAction("fold"))
        self.assertTrue(state.terminal)
        self.assertEqual(total_chips(state), 200.0)

    def test_min_raise_and_max_raise_are_accepted(self):
        state = new_hunl_hand(seed=11)
        actions = {action.type: action for action in legal_actions(state)}

        min_raised = apply_action(state, LegalAction("raise", amount_bb=actions["raise"].min_to_bb))
        self.assertEqual(min_raised.current_bet_to_bb, actions["raise"].min_to_bb)

        max_raised = apply_action(state, LegalAction("raise", amount_bb=actions["raise"].max_to_bb))
        self.assertEqual(max_raised.current_bet_to_bb, actions["raise"].max_to_bb)
        self.assertEqual(max_raised.player("SB").stack_bb, 0.0)
        self.assertEqual(total_chips(max_raised), 200.0)

    def test_illegal_under_raise_rejected(self):
        state = new_hunl_hand(seed=12)
        with self.assertRaises(ValueError):
            apply_action(state, LegalAction("raise", amount_bb=1.5))

    def test_bet_call_closes_street(self):
        state = new_hunl_hand(seed=13)
        state = apply_action(state, LegalAction("call", amount_bb=0.5))
        state = apply_action(state, LegalAction("check"))
        state = apply_action(state, LegalAction("bet", amount_bb=3.0))
        state = apply_action(state, LegalAction("call", amount_bb=3.0))

        self.assertEqual(state.street, Street.TURN)
        self.assertEqual(total_chips(state), 200.0)

    def test_short_stack_call_all_in_reaches_showdown(self):
        state = new_hunl_hand(seed=14)
        sb, bb = state.players
        state = replace(
            state,
            pot_bb=101.5,
            current_bet_to_bb=100.0,
            min_raise_increment_bb=99.0,
            pending_seats=("BB",),
            actor_seat="BB",
            players=(
                replace(sb, stack_bb=0.0, street_contribution_bb=100.0, hand_contribution_bb=100.0),
                replace(bb, stack_bb=4.0, street_contribution_bb=1.0, hand_contribution_bb=1.0),
            ),
        )
        call = [action for action in legal_actions(state) if action.type == "call"][0]

        state = apply_action(state, LegalAction("call", amount_bb=call.amount_bb))
        while not state.terminal:
            state = apply_action(state, LegalAction("check"))

        self.assertEqual(state.terminal_reason, "showdown")
        self.assertEqual(total_chips(state), 105.5)

    def test_river_all_in_call_goes_to_showdown(self):
        state = new_hunl_hand(seed=15)
        state = apply_action(state, LegalAction("call", amount_bb=0.5))
        state = apply_action(state, LegalAction("check"))
        state = apply_action(state, LegalAction("check"))
        state = apply_action(state, LegalAction("check"))
        state = apply_action(state, LegalAction("check"))
        state = apply_action(state, LegalAction("check"))
        self.assertEqual(state.street, Street.RIVER)
        max_bet = [action for action in legal_actions(state) if action.type == "bet"][0].max_to_bb
        state = apply_action(state, LegalAction("bet", amount_bb=max_bet))
        state = apply_action(state, LegalAction("call", amount_bb=max_bet))

        self.assertTrue(state.terminal)
        self.assertEqual(state.terminal_reason, "showdown")
        self.assertEqual(total_chips(state), 200.0)


if __name__ == "__main__":
    unittest.main()
