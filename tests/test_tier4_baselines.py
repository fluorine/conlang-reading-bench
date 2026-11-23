import unittest

from conlang.tier4_baselines import last_disclosed_transfer
from conlang.tier4_dynamic import build_story


class Tier4BaselinesTest(unittest.TestCase):
    def test_uses_only_disclosed_hints_and_full_disclosure_decodes(self):
        case = build_story(1907078801, 1406322485, scheme='unique',
                           observed_hints=True, hint_levels=(10, 20, 30))
        self.assertEqual(last_disclosed_transfer(case['prompts'][2]), case['answers'])
        self.assertEqual(len(last_disclosed_transfer(case['prompts'][0])), 4)

    def test_handcrafted_known_giver_and_recipient(self):
        prompt = ('Instructions\n\nInitial words: lu = coin, zo = key, mi = book, '
                  've = ring, ka = cup. Known suffix meanings (object/reference holder/role): '
                  '-pa: coin/other/giver; -ta: key/other/recipient.\n\nStory:\n'
                  'Ada holds lu\nBo holds zo\nCy holds mi\nDee holds ve\nEli holds ka\n'
                  'Fay-xx Ada-pa\nCy-ta Bo-xx\nDee-xx Fay-xx\n\nQuestions')
        self.assertEqual(last_disclosed_transfer(prompt), ['Fay', 'Cy', 'Cy', 'Dee'])

    def test_deferred_design_remains_unambiguous_and_fully_decodable(self):
        case = build_story(1538297922, 86143699, scheme='unique', observed_hints=True,
                           hint_levels=(10, 20, 30), min_observed_markers=20,
                           defer_target_final=True)
        self.assertEqual(last_disclosed_transfer(case['prompts'][2]), case['answers'])
        self.assertLess(sum(a == b for a, b in zip(
            last_disclosed_transfer(case['prompts'][0]), case['answers'])), 4)


if __name__ == '__main__':
    unittest.main()
