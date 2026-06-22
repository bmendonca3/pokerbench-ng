import unittest

from pokerbench_ng.engine.legal_actions import starter_legal_actions


class LegalActionTests(unittest.TestCase):
    def test_check_and_bet_when_no_call_required(self):
        actions = starter_legal_actions(0, 2, 100)
        self.assertEqual([action.type for action in actions], ["check", "bet"])
        self.assertEqual(actions[1].min_to_bb, 2)
        self.assertEqual(actions[1].max_to_bb, 100)

    def test_fold_call_raise_when_facing_bet(self):
        actions = starter_legal_actions(3, 9, 100)
        self.assertEqual([action.type for action in actions], ["fold", "call", "raise"])
        self.assertEqual(actions[1].amount_bb, 3)

    def test_negative_call_rejected(self):
        with self.assertRaises(ValueError):
            starter_legal_actions(-1, 2, 100)


if __name__ == "__main__":
    unittest.main()
