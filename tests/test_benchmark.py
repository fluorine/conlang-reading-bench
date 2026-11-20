import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from conlang.__main__ import main
from conlang.language import evidence, interpretations, language, render
from conlang.runner import MODELS, new_bundle, run, settings
from conlang.scoring import compare, grade, parse
from conlang.suite import ROOT, certified, digest, load_suite, read
from conlang.transfer_diagnostics import summarize
from conlang.world import answers, english, simulate


def fixture():
    m = load_suite("smoke")
    prompts, keys = certified(m)
    b = new_bundle(m, prompts, settings(next(iter(MODELS)), "default", 64))
    for i, p in prompts.items():
        b["responses"][i] = dict(prompt_hash=digest(p), raw=json.dumps(keys[i.split("/")[0]]["answers"]))
    return m, b


class TestProtocol(unittest.TestCase):
    def test_matched_grammar_variants(self):
        suites = [load_suite("grammar" + name) for name in
                  ("fused", "sound", "irregular", "combined", "english")]
        self.assertTrue(all(suite["pairs"] == suites[0]["pairs"] for suite in suites))
        generated = [certified(suite) for suite in suites]
        for _, keys in generated[1:]:
            self.assertEqual(keys, generated[0][1])
        for prompts, _ in generated[:-1]:
            for item, prompt in prompts.items():
                self.assertEqual(prompt.split("\n\n")[-1],
                                 generated[-1][0][item.replace("/minimal", "/english")].split("\n\n")[-1])

    def test_diagnostics_count_capped_blanks_as_unanswered(self):
        bundle = read(ROOT / "results/transfer4/gpt-6-luna-low.json")
        report = summarize(load_suite("transfer4"), [bundle])
        minimal = report["results"][0]["conditions"]["minimal"]
        self.assertEqual(minimal, dict(correct=82, answered=84, wrong=2, full_responses=21,
                                      empty_responses=3, empty_at_cap=3))
        self.assertEqual(report["last_person_correct"], {"minimal": 28, "english": 47})

    def test_four_transfer_history_and_rendering(self):
        manifest = load_suite("transfer4")
        prompts, keys = certified(manifest)
        self.assertEqual(len(prompts), 48)
        self.assertEqual({next(iter(k["initial"])) for k in keys.values()}, {"coin", "key"})
        for story, key in keys.items():
            first, second, third, fourth = key["events"]
            self.assertEqual(first[0], third[0])
            self.assertEqual(second[0], fourth[0])
            self.assertNotEqual(third[0], fourth[0])
            self.assertEqual(key["answers"][1], third[2])
            self.assertIn(f"before the {fourth[0]} was given away for the second time",
                          prompts[story + "/minimal"])
            self.assertEqual(prompts[story + "/minimal"].split("\n\n")[-1],
                             prompts[story + "/english"].split("\n\n")[-1])

    def test_frozen_suites(self):
        for path in sorted((ROOT / "suites").glob("*.json")):
            m = read(path)
            prompts, keys = certified(m)
            self.assertEqual(certified(m), (prompts, keys))
            self.assertEqual(len(prompts), len(keys) * len(m["conditions"]))
        self.assertTrue(set(map(tuple, load_suite("dev2")["pairs"])).isdisjoint(
            map(tuple, load_suite("holdout2")["pairs"])))

    def test_hand_worked_and_ambiguous(self):
        initial = {"coin": "Ada", "key": "Bo"}
        events = [("coin", "Ada", "Cy"), ("coin", "Cy", "Bo"), ("key", "Bo", "Ada")]
        query = (0, "key", "coin", "key")
        expected = ("Cy", "Bo", "Bo", "Ada")
        self.assertEqual(answers(initial, events, query), expected)
        self.assertEqual(english(initial, events)[-1], "Bo gives the key to Ada.")
        for seed in range(30):
            lang = language(seed)
            roots, gs, rs, order = lang
            lines = render(lang, initial, events)
            example = f"Ivy {roots['holds']} {roots['coin']}"
            self.assertIn(example, evidence(lang)[0])
            self.assertEqual(interpretations(lines, example, roots["gives"], query), {expected})
            self.assertGreater(len(interpretations(lines, None, roots["gives"], query)), 1)
            for line, (obj, giver, recipient) in zip(lines[2:], events):
                slots = dict(zip(order, line.split()))
                self.assertEqual(slots["giver"], f"{giver}-{gs}")
                self.assertEqual(slots["recipient"], f"{recipient}-{rs}")
        with self.assertRaises(ValueError):
            simulate(initial, [("coin", "Bo", "Ada")])

    def test_fractional_score_and_completeness(self):
        m, b = fixture()
        self.assertEqual(grade(m, b)["headline"], 100)
        for item, row in b["responses"].items():
            tier = item.split("/")[1]
            if tier in ("minimal", "glossary"):
                row["raw"] = json.dumps(json.loads(row["raw"])[:2 if tier == "minimal" else 3])
        self.assertEqual(grade(m, b)["headline"], 75)
        item = next(iter(b["responses"]))
        b["responses"][item]["raw"] = "bad json"
        self.assertTrue(grade(m, b)["complete"])
        del b["responses"][item]
        self.assertFalse(grade(m, b)["complete"])
        with self.assertRaises(ValueError):
            compare(m, b, b)

    def test_normalization_and_protocol_mismatch(self):
        self.assertEqual(parse('```json\n["  CY ", null]\n```'), ["cy", ""])
        self.assertEqual(parse('```json\n["Ada"]\n```', strict=True), [])
        self.assertEqual(parse('answer: ["Ada"]'), [])
        self.assertEqual(parse('["a","b","c","d","e"]'), [])
        m, b = fixture()
        self.assertEqual(compare(m, b, b)["interval95"], [0, 0])
        next(iter(b["responses"].values()))["prompt_hash"] = "wrong"
        with self.assertRaises(ValueError):
            grade(m, b)

    def test_budget_stops_before_network(self):
        m, b = fixture()
        with tempfile.TemporaryDirectory() as temp, patch.dict("os.environ", OPENAI_API_KEY="test"):
            with patch("urllib.request.urlopen") as network, self.assertRaisesRegex(ValueError, "spending"):
                run(m, b["settings"], Path(temp) / "b.json", 0.000000001)
            network.assert_not_called()

    def test_cli_export_and_saved_response_import(self):
        m, b = fixture()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            main(["generate", "--out", str(path)])
            self.assertEqual(list((path / "public").iterdir()), [path / "public/prompts.json"])
            (path / "saved.json").write_text(json.dumps(b))
            out = path / "other.json"
            main(["run", "--out", str(out), "--import", str(path / "saved.json")])
            main(["score", str(out), "--out", str(path / "graded.json")])
            self.assertEqual(read(path / "graded.json")["headline"], 100)


if __name__ == "__main__":
    unittest.main()
