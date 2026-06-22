import unittest

from pokerbench_ng.engine.cards import Card, full_deck, shuffled_deck


class CardTests(unittest.TestCase):
    def test_full_deck_has_52_unique_cards(self):
        deck = full_deck()
        self.assertEqual(len(deck), 52)
        self.assertEqual(len({str(card) for card in deck}), 52)

    def test_parse_valid_card(self):
        self.assertEqual(str(Card.parse("As")), "As")

    def test_parse_invalid_card_rejected(self):
        with self.assertRaises(ValueError):
            Card.parse("1s")

    def test_shuffle_is_deterministic_by_seed(self):
        self.assertEqual(shuffled_deck(42), shuffled_deck(42))
        self.assertNotEqual(shuffled_deck(42), shuffled_deck(43))


if __name__ == "__main__":
    unittest.main()

