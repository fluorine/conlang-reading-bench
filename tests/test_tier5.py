import io
import json
import tempfile
import unittest
from collections import Counter
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from conlang.scoring import parse_final_answer
from conlang.suite import read, write
from conlang.tier5 import build_story, load_manifest, score
from conlang.tier5_report import report
from experiments.make_tier5_dev import manifest as make_manifest
from experiments.run_tier5_probes import main as run_probes
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


class TestTier5Runner(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.manifest = self.root / "m.json"
        write(self.manifest, make_manifest("tier5-test", "L1", 2, "tier5-test"))

    def tearDown(self):
        self.tmp.cleanup()

    def fake(self, conf, messages, timeout=75):
        prompt = messages[0]["content"]
        answers = next(a for a in self.gold if a[0] == prompt)[1]
        late = "Rules revealed so far:\nNone yet." not in prompt
        raw = "Reasoning.\n" + json.dumps(answers if late else ["nobody"] * 6)
        return dict(raw=raw, model=conf["model"], finish_reason="end_turn",
                    usage=dict(prompt_tokens=1000, completion_tokens=500))

    def run_probe(self, *extra):
        args = ["--manifest", str(self.manifest), "--out", str(self.root / "run"),
                "--budget", "1", "--model", "fake", "--provider", "Anthropic",
                "--rates", "0.1", "0.5", "--workers", "1", *extra]
        with patch("experiments.run_tier5_probes.provider_request", self.fake), \
                redirect_stdout(io.StringIO()) as out:
            run_probes(args)
        return out.getvalue()

    def test_run_resume_and_report(self):
        _, items = load_manifest(self.manifest)
        self.gold = [(p, i["answers"]) for i in items for p in [*i["prompts"], i["english"]]]
        estimate = json.loads(self.run_probe("--estimate"))
        self.assertEqual(estimate["remaining"], 2 * 6)
        self.run_probe()
        self.assertEqual(len(list((self.root / "run").glob("*-*.json"))), 12)
        self.assertEqual(json.loads(self.run_probe("--estimate"))["remaining"], 0)
        self.run_probe()
        result = report(self.manifest, self.root / "run")
        self.assertTrue(result["complete"])
        self.assertEqual(result["stage_curve"][0], 0)
        self.assertEqual(result["stage_curve"][1:], [100.0] * 4)
        self.assertEqual(result["english"], 100.0)
        self.assertEqual(result["dcs"], 80.0)
        self.assertEqual(result["rules_to_solve"], [1, 1])
        self.assertAlmostEqual(result["cost_usd"], 12 * (1000 * 0.1 + 500 * 0.5) / 1e6)

    def test_budget_stops_before_overspending(self):
        _, items = load_manifest(self.manifest)
        self.gold = [(p, i["answers"]) for i in items for p in [*i["prompts"], i["english"]]]
        args = ["--manifest", str(self.manifest), "--out", str(self.root / "run"),
                "--budget", "0.001", "--model", "fake", "--provider", "Anthropic",
                "--rates", "0.1", "0.5", "--workers", "1"]
        with patch("experiments.run_tier5_probes.provider_request", self.fake), \
                redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(ValueError, "budget"):
                run_probes(args)

    def test_manifest_drift_is_detected(self):
        manifest = read(self.manifest)
        manifest["prompts_sha256"] = "0" * 64
        write(self.manifest, manifest)
        with self.assertRaisesRegex(ValueError, "differs"):
            load_manifest(self.manifest)


if __name__ == "__main__":
    unittest.main()
