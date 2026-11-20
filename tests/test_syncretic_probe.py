import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from conlang.three_object_probe import build
from conlang.verify_tier3_search import suffix_blind_answers
from experiments.run_case_probes import main as run_case_probes


class TestSyncreticProbe(unittest.TestCase):
    def test_matched_control_and_known_answer(self):
        prompt, answer = build(1, 2, syncretism=True)
        english, control_answer = build(1, 2, english=True, syncretism=True)
        self.assertEqual(answer, 'Eli')
        self.assertEqual(answer, control_answer)
        self.assertIn('Each suffix represents exactly two', prompt)
        self.assertIn('Who holds the coin at the end?', english)
        blind_answers = suffix_blind_answers(prompt, ('coin', 'key', 'book'))
        self.assertIn(answer, blind_answers)
        self.assertGreater(len(blind_answers), 1)

    def test_ambiguous_story_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'do not determine'):
            build(3, 4, syncretism=True)

    def test_revealed_suffixes_preserve_answer(self):
        prompt, answer = build(1, 2, syncretism=True, revealed=3)
        _, control_answer = build(1, 2, english=True, syncretism=True, revealed=3)
        self.assertEqual(answer, control_answer)
        self.assertIn('Known suffix meanings', prompt)
        disclosed = prompt.split('Known suffix meanings', 1)[1].split('\n\n', 1)[0]
        self.assertEqual(disclosed.count(' or '), 3)

    def test_probe_budget_stops_before_network(self):
        with tempfile.TemporaryDirectory() as directory:
            arguments = ['probe', '--manifest', 'experiments/syncretic-one-clue-dev.json',
                         '--out', str(Path(directory) / 'run'), '--budget', '0', '--rates', '0.1', '0.5']
            with patch('sys.argv', arguments), patch('urllib.request.urlopen') as network:
                with self.assertRaisesRegex(ValueError, 'exceed budget'):
                    run_case_probes()
                network.assert_not_called()


if __name__ == '__main__':
    unittest.main()
