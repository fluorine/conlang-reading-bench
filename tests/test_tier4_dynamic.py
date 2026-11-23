import json
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from conlang.tier4_dynamic import OBJECTS, TARGETS, build_story, score
from conlang.verify_tier3_search import suffix_blind_answers
from experiments.run_tier4_probes import main as run_probes


class TestTier4Dynamic(unittest.TestCase):
    def test_story_hints_and_questions_remain_consistent(self):
        case = build_story(363756058, 1106497454)
        self.assertEqual(case['answers'], ['Dee', 'Bo', 'Cy', 'Cy'])
        self.assertEqual(len(case['prompts']), 3)
        self.assertEqual(score(json.dumps(case['answers']), case['answers']), [True] * 4)
        self.assertEqual(score('["Dee", "wrong"]', case['answers']), [True, False, False, False])
        self.assertEqual(score('not JSON', case['answers']), [False] * 4)
        for index, target in enumerate(TARGETS):
            possibilities = suffix_blind_answers(case['prompts'][0], OBJECTS, OBJECTS.index(target))
            self.assertIn(case['answers'][index], possibilities)
            self.assertGreater(len(possibilities), 1)
        self.assertEqual(case['prompts'][0].split('\n\n')[-1], case['prompts'][2].split('\n\n')[-1])
        self.assertIn(case['prompts'][0].split('\n\n')[-1], case['continuation'][0])

    def test_ambiguous_story_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'do not determine'):
            build_story(2059601839, 1504670080)

    def test_repeated_questions_use_saved_history_without_feedback(self):
        pair = [363756058, 1106497454]
        case = build_story(*pair)
        response = {'model': 'gpt-6-luna', 'choices': [{'message': {'content': json.dumps(case['answers'])},
                                                        'finish_reason': 'stop'}],
                    'usage': {'prompt_tokens': 20, 'completion_tokens': 10}}
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / 'manifest.json'
            manifest.write_text(json.dumps({'pairs': [pair], 'length': 30, 'question_count': 4,
                                            'hint_levels': [1, 5, 15]}))
            output = Path(directory) / 'run'
            args = ['probe', '--manifest', str(manifest), '--out', str(output), '--budget', '0.5', '--rates', '0.1', '0.5']
            with patch('sys.argv', args), patch.dict('os.environ', {'OPENAI_API_KEY': 'test'}), \
                    patch('urllib.request.urlopen', side_effect=lambda *a, **k: io.BytesIO(json.dumps(response).encode())) as network, \
                    patch('builtins.print'):
                run_probes()
                run_probes()
                self.assertEqual(network.call_count, 15)
            record = json.loads((output / f'{pair[0]}-{pair[1]}-continued_hints-1.json').read_text())
            self.assertEqual([message['role'] for message in record['messages']], ['user', 'assistant', 'user'])
            self.assertEqual(record['messages'][1]['content'], json.dumps(case['answers']))
            self.assertEqual(record['messages'][2]['content'], case['continuation'][0])
            control = json.loads((output / f'{pair[0]}-{pair[1]}-continued_nohint-1.json').read_text())
            self.assertEqual(control['messages'][2]['content'], case['repeat'])
            self.assertEqual(record['marks'], [True] * 4)

    def test_budget_prevents_model_request(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / 'manifest.json'
            manifest.write_text(json.dumps({'pairs': [[363756058, 1106497454]], 'length': 30,
                                            'question_count': 4, 'hint_levels': [1, 5, 15]}))
            args = ['probe', '--manifest', str(manifest), '--out', str(Path(directory) / 'run'),
                    '--budget', '0', '--rates', '0.1', '0.5']
            with patch('sys.argv', args), patch('urllib.request.urlopen') as network:
                with self.assertRaisesRegex(ValueError, 'budget cannot cover'):
                    run_probes()
                network.assert_not_called()


if __name__ == '__main__':
    unittest.main()
