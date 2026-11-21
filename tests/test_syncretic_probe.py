import unittest
import tempfile
import json
import io
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
                (Path(directory) / 'run' / 'uncertain.pending').write_text('{}')
                with self.assertRaisesRegex(ValueError, 'uncertain requests'):
                    run_case_probes()
                network.assert_not_called()
                marker = Path(directory) / 'run' / 'uncertain.pending'
                marker.unlink()
                pair = json.loads(Path('experiments/syncretic-one-clue-dev.json').read_text())['pairs'][0]
                (marker.parent / f'{pair[0]}-{pair[1]}-0.pending').write_text('{"reservation": 0.01}')
                with patch('sys.argv', arguments + ['--retry-uncertain']):
                    with self.assertRaisesRegex(ValueError, 'exceed budget'):
                        run_case_probes()
                self.assertEqual(len(list((marker.parent / 'uncertain').glob('*.json'))), 1)
                network.assert_not_called()

    def test_budgeted_batches_resume_with_same_manifest(self):
        result = {'model': 'gpt-6-luna', 'choices': [{'message': {'content': '["Ada"]'}, 'finish_reason': 'stop'}],
                  'usage': {'prompt_tokens': 20, 'completion_tokens': 10}}
        def response(*args, **kwargs):
            return io.BytesIO(json.dumps(result).encode())
        with tempfile.TemporaryDirectory() as directory:
            arguments = ['probe', '--manifest', 'experiments/syncretic-one-clue-dev.json',
                         '--out', directory, '--budget', '0.02', '--rates', '0.1', '0.5',
                         '--max-new-requests', '1']
            with patch('sys.argv', arguments), patch.dict('os.environ', {'OPENAI_API_KEY': 'test'}), \
                    patch('urllib.request.urlopen', side_effect=response) as network:
                run_case_probes()
                run_case_probes()
                self.assertEqual(network.call_count, 2)
            rows = [p for p in Path(directory).glob('*.json') if p.name != 'run.json']
            self.assertEqual(len(rows), 2)


if __name__ == '__main__':
    unittest.main()
