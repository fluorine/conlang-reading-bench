import unittest
import json
from pathlib import Path

from conlang.scoring import parse, parse_final_answer


class FinalAnswerTest(unittest.TestCase):
    def test_extracts_only_the_final_json_array(self):
        self.assertEqual(parse_final_answer('Reasoning with [example].\n["Ada", " Bo "]'), ['ada', 'bo'])
        self.assertEqual(parse_final_answer('Reasoning\n```json\n["Ada"]\n```'), ['ada'])
        self.assertEqual(parse_final_answer('Reasoning\n**["Ada"]**'), ['ada'])
        self.assertEqual(parse_final_answer('["Ada"]'), parse('["Ada"]'))

    def test_rejects_trailing_text_malformed_and_non_answer_arrays(self):
        self.assertEqual(parse_final_answer('["Ada"] followed by text'), [])
        self.assertEqual(parse_final_answer('["Ada"]**'), [])
        self.assertEqual(parse_final_answer('["Ada"]```'), [])
        self.assertEqual(parse_final_answer('Reasoning ["Ada"'), [])
        self.assertEqual(parse_final_answer('[["Ada"]]'), [])
        self.assertEqual(parse_final_answer('["Ada", 42]'), [])
        self.assertEqual(parse_final_answer('["a", "b", "c", "d", "e"]'), [])
        self.assertEqual(parse_final_answer(None), [])

    def test_saved_sonnet_tier3_and_capped_high_results(self):
        archive = json.loads(Path('reports/tier3-sonnet-low-responses.json').read_text(encoding='utf-8'))
        rows = [row for run in archive['runs'].values() for row in run['responses']]
        for english, expected in ((False, 21), (True, 48)):
            selected = [row for row in rows if row['english'] is english]
            self.assertEqual(len(selected), 48)
            self.assertEqual(sum(parse_final_answer(row['raw']) == [row['gold'].casefold()]
                                 for row in selected), expected)
        high = json.loads(Path('reports/tier3-sonnet-high-responses.json').read_text(encoding='utf-8'))
        capped = [row for run in high['runs'].values() for row in run['responses']
                  if not row['english'] and row.get('finish_reason') in ('length', 'max_tokens')]
        self.assertEqual(len(capped), 30)
        self.assertTrue(all(not parse_final_answer(row['raw']) for row in capped))

    def test_saved_sonnet_tier4_answers(self):
        rows = [row for i in range(4) for row in json.loads(
            Path(f'reports/tier4-zero-sonnet-low-{i}-responses.json').read_text(encoding='utf-8'))['responses']]
        for stage, expected in enumerate((128, 157, 192)):
            selected = [row for row in rows if row['mode'] == 'fresh_conlang' and row['stage'] == stage]
            self.assertEqual(len(selected), 48)
            correct = sum(sum(i < len(parsed) and parsed[i] == answer.casefold()
                              for i, answer in enumerate(row['answers']))
                          for row in selected for parsed in [parse_final_answer(row['raw'])])
            self.assertEqual(correct, expected)


if __name__ == '__main__':
    unittest.main()
