import unittest

from conlang.tier4_audit import decode_full
from conlang.tier4_baselines import last_disclosed_transfer
from conlang.tier4_dynamic import build_story


class Tier4RegularTest(unittest.TestCase):
    def test_regular_grammar_and_full_replay(self):
        case = build_story(123, 456, scheme='unique', observed_hints=True,
                           hint_levels=(1, 3, 10), context_free=True)
        self.assertEqual(decode_full(case['prompts'][2], context_free=True), case['answers'])
        self.assertEqual(last_disclosed_transfer(case['prompts'][2]), case['answers'])
        self.assertIn('middle field', case['prompts'][0])
        self.assertEqual(len(case['answers']), 4)

    def test_incompatible_context_free_syncretism(self):
        with self.assertRaises(ValueError):
            build_story(123, 456, scheme='shared', context_free=True)


if __name__ == '__main__':
    unittest.main()
