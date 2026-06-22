import unittest

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


if __name__ == "__main__":
    unittest.main()
