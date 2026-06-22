import unittest

from pokerbench_ng.engine.cards import full_deck
from pokerbench_ng.engine.legal_actions import LegalAction
from pokerbench_ng.engine.state import Street
from pokerbench_ng.engine.transitions import apply_action, legal_actions, new_hunl_hand, total_chips


class EngineInvariantTests(unittest.TestCase):
    def test_deck_invariant(self):
        deck = full_deck()
        self.assertEqual(len(deck), len(set(deck)))

    def test_new_hand_posts_blinds_and_conserves_chips(self):
        state = new_hunl_hand(seed=1)
        self.assertEqual(state.street, Street.PREFLOP)
        self.assertEqual(state.pot_bb, 1.5)
        self.assertEqual(state.actor_seat, "SB")
        self.assertEqual(total_chips(state), 200.0)
        self.assertEqual([action.type for action in legal_actions(state)], ["fold", "call", "raise"])

    def test_call_then_check_advances_to_flop(self):
        state = new_hunl_hand(seed=2)
        state = apply_action(state, LegalAction("call", amount_bb=0.5))
        self.assertEqual(state.actor_seat, "BB")
        self.assertEqual(total_chips(state), 200.0)
        state = apply_action(state, LegalAction("check"))
        self.assertEqual(state.street, Street.FLOP)
        self.assertEqual(state.actor_seat, "BB")
        self.assertEqual(len(state.board), 3)
        self.assertEqual(total_chips(state), 200.0)

    def test_fold_awards_pot_and_terminates(self):
        state = new_hunl_hand(seed=3)
        state = apply_action(state, LegalAction("fold"))
        self.assertTrue(state.terminal)
        self.assertEqual(state.terminal_reason, "fold")
        self.assertEqual(state.pot_bb, 0.0)
        self.assertEqual(total_chips(state), 200.0)

    def test_raise_then_call_advances_to_flop(self):
        state = new_hunl_hand(seed=4)
        state = apply_action(state, LegalAction("raise", amount_bb=3.0))
        self.assertEqual(state.actor_seat, "BB")
        self.assertEqual(total_chips(state), 200.0)
        state = apply_action(state, LegalAction("call", amount_bb=2.0))
        self.assertEqual(state.street, Street.FLOP)
        self.assertEqual(total_chips(state), 200.0)


if __name__ == "__main__":
    unittest.main()
