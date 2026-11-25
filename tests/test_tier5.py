import json
import unittest
from collections import Counter

from conlang.scoring import parse_final_answer
from conlang.tier5 import build_story, score
from conlang.tier5_grammar import LEVELS, card_orders, level, sample_language
from conlang.tier5_verify import answer_sets
from conlang.tier5_world import MAX_SAME_ANSWER


class TestTier5(unittest.TestCase):
    def test_every_level_builds_a_verified_story(self):
        for name in LEVELS:
            item = build_story(101, 202, name, 0, answerability=True)
            cards = [c for c in item["cards"]]
            self.assertEqual(len(item["prompts"]), len(cards) + 1)
            self.assertEqual(len(item["answers"]), 6)
            self.assertTrue(all(item["answerable"][-1]), name)
            self.assertLessEqual(max(Counter(item["answers"]).values()), MAX_SAME_ANSWER)

    def test_build_is_deterministic(self):
        self.assertEqual(build_story(7, 8, "L3", 1), build_story(7, 8, "L3", 1))

    def test_stages_share_story_and_add_one_rule_each(self):
        item = build_story(101, 202, "L4", 2)
        blocks = [prompt.split("\n\n") for prompt in item["prompts"]]
        for block in blocks[1:]:
            self.assertEqual(block[4:], blocks[0][4:])
        rules = [block[3].splitlines()[1:] for block in blocks]
        self.assertEqual(rules[0], ["None yet."])
        for stage in range(2, len(rules)):
            self.assertEqual(rules[stage][:-1], rules[stage - 1])

    def test_card_orders_form_rotations(self):
        orders = card_orders(level("L5"), 5)
        self.assertEqual(len(orders), 4)
        self.assertEqual(len({tuple(o) for o in orders}), 4)
        self.assertTrue(all(sorted(o) == sorted(orders[0]) for o in orders))

    def test_verifier_reports_ambiguity_until_the_card(self):
        lvl = level("L1")
        lang = sample_language(1, lvl)
        roots = lang["roots"]
        neg = next(w for w, m in lang["particles"].items() if m == "neg")
        other = next(s for s in lang["suffixes"] if s != lang["case"])
        lines = [f"Ada {roots['coin']} {roots['hold']}", f"Bo {roots['key']} {roots['hold']}",
                 f"Cy {roots['book']} {roots['hold']}",
                 f"{neg} Ada-{lang['case']} Bo-{other} {roots['coin']} "
                 f"{roots['give']}-{lang['tense']['past']}"]
        spec = [("final", "coin")]
        self.assertEqual(answer_sets(lvl, lang, {}, lines, spec, set()), [{"Ada", "Bo"}])
        self.assertEqual(answer_sets(lvl, lang, {}, lines, spec, {"negation"}), [{"Ada"}])

    def test_score_accepts_reasoning_before_final_array(self):
        answers = ["Ada", "Bo", "Cy", "Dee", "Eli", "Fay"]
        self.assertEqual(score("Work...\n" + json.dumps(answers), answers), [True] * 6)
        self.assertEqual(score('["Ada", "x"]', answers), [True] + [False] * 5)
        self.assertEqual(score("no array", answers), [False] * 6)

    def test_final_answer_limit_default_is_unchanged(self):
        self.assertEqual(parse_final_answer(json.dumps(["a"] * 5)), [])
        self.assertEqual(parse_final_answer(json.dumps(["a"] * 5), max_items=6), ["a"] * 5)


if __name__ == "__main__":
    unittest.main()
