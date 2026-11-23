import unittest

from conlang.tier4_audit import decode_full
from conlang.tier4_baselines import last_disclosed_transfer, last_role_recipient
from conlang.tier4_compact import OBJECTS, build_story


class Tier4CompactTest(unittest.TestCase):
    def test_gold_and_direct_tracker(self):
        case = build_story(123, 456, hint_levels=(1, 3, 18))
        self.assertEqual(len(case['answers']), 3)
        self.assertEqual(decode_full(case['prompts'][2], objects=OBJECTS, targets=OBJECTS), case['answers'])
        self.assertEqual(last_disclosed_transfer(case['prompts'][2], targets=OBJECTS), case['answers'])
        self.assertIn('3 names', case['english'])

    def test_focused_question(self):
        base = build_story(123, 456, hint_levels=(1, 3, 18))
        focused = build_story(123, 456, hint_levels=(1, 3, 18), focus_index=1)
        self.assertEqual(focused['answers'], [base['answers'][1]])
        self.assertIn('1 name', focused['english'])
        self.assertEqual(focused['english'].split('\n\n')[-1].count('\n'), 0)

    def test_role_inventory_and_full_replay(self):
        case = build_story(123, 456, role_hints=True)
        self.assertEqual(decode_full(case['prompts'][2], objects=OBJECTS, targets=OBJECTS), case['answers'])
        name = last_role_recipient(case['prompts'][0])
        self.assertIn(name, ('Ada', 'Bo', 'Cy', 'Dee', 'Eli', 'Fay'))
        with self.assertRaises(ValueError):
            decode_full(case['prompts'][2].replace('giver suffixes -', 'giver suffixes -bad, -', 1),
                        objects=OBJECTS, targets=OBJECTS)


if __name__ == '__main__':
    unittest.main()
