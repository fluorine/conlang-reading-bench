import unittest

from conlang.tier4_audit import decode_full
from conlang.tier4_baselines import last_disclosed_transfer
from conlang.tier4_checkpoint import suffix_blind_checkpoint
from conlang.tier4_dynamic import build_story


class Tier4CheckpointTest(unittest.TestCase):
    def test_checkpoint_answers_and_baseline_are_reconstructible(self):
        case = build_story(334440644, 1573348965, scheme='unique', observed_hints=True,
                           hint_levels=(10, 20, 30), min_observed_markers=20, query_after=15)
        self.assertEqual(decode_full(case['prompts'][2], query_after=15), case['answers'])
        self.assertEqual(last_disclosed_transfer(case['prompts'][2], 15), case['answers'])
        possibilities = suffix_blind_checkpoint(case['prompts'][0], 15)
        self.assertTrue(all(answer in possibilities[i] for i, answer in enumerate(case['answers'])))
        self.assertIn('after transfer 15', case['prompts'][0])
        self.assertIn('after transfer 15', case['english'])

    def test_invalid_checkpoint_rejected(self):
        with self.assertRaises(ValueError):
            build_story(334440644, 1573348965, scheme='unique', observed_hints=True,
                        hint_levels=(10, 20, 30), query_after=31)


if __name__ == '__main__':
    unittest.main()
