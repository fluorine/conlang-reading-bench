"""Rebuild and regrade the archived exploratory Tier 3 probes offline."""
import json
from itertools import permutations, product
from pathlib import Path

from conlang import abstract_probe, context_case_probe, fused_case_probe, sparse_case_probe, three_object_probe, single_probe
from conlang.scoring import parse

DATASETS = {
    'abstract-dev': (abstract_probe, {}),
    'context-case-dev': (context_case_probe, {}),
    'fused-case-dev': (fused_case_probe, {}),
    'sparse-case-dev': (sparse_case_probe, {'examples': 0}),
    'sparse-case-long-dev': (sparse_case_probe, {'examples': 0, 'length': 24}),
    'sparse-case-48-dev': (sparse_case_probe, {'examples': 0, 'length': 48}),
    'three-object-dev': (three_object_probe, {}),
    'four-object-dev': (three_object_probe, {'objects': ('coin', 'key', 'book', 'ring')}),
    'five-object-dev': (three_object_probe, {'objects': ('coin', 'key', 'book', 'ring', 'cup')}),
    'syncretic-case-dev': (three_object_probe, {'syncretism': True}),
    'syncretic-short-dev': (three_object_probe, {'syncretism': True, 'length': 12}),
    'syncretic-clues-dev': (three_object_probe, {'syncretism': True, 'length': 12, 'revealed': 3}),
    'syncretic-long-clues-dev': (three_object_probe, {'syncretism': True, 'length': 18, 'revealed': 3}),
    'syncretic-one-clue-dev': (three_object_probe, {'syncretism': True, 'length': 18, 'revealed': 1}),
    'syncretic-24-one-clue-dev': (three_object_probe, {'syncretism': True, 'length': 24, 'revealed': 1}),
    'syncretic-24-one-clue-holdout': (three_object_probe, {'syncretism': True, 'length': 24, 'revealed': 1}),
    'syncretic-five-object-dev': (three_object_probe, {'syncretism': True, 'length': 18, 'revealed': 1,
                                                        'objects': ('coin', 'key', 'book', 'ring', 'cup')}),
}

def suffix_blind_answers(prompt, objects):
    """Possible coin holders if suffixes are erased but transfers remain legal."""
    story = prompt.split('\n\n')[2].splitlines()[1:]
    states = {tuple(line.split()[0] for line in story[:len(objects)])}
    for line in story[len(objects):]:
        names = [word.split('-')[0] for word in line.split()]
        updated = set()
        for state in states:
            for index, (giver, receiver) in product(range(len(objects)), permutations(names)):
                if state[index] == giver:
                    next_state = list(state)
                    next_state[index] = receiver
                    updated.add(tuple(next_state))
        states = updated
    return {state[0] for state in states}

def main():
    archive = json.loads(Path('reports/tier3-search-responses.json').read_text(encoding='utf-8'))
    if set(archive['datasets']) != set(DATASETS):
        raise ValueError('Unexpected dataset list')
    for name, (module, options) in DATASETS.items():
        rows = archive['datasets'][name]
        manifest = json.loads(Path(f'experiments/{name}.json').read_text(encoding='utf-8'))
        pairs = {tuple(pair) for pair in manifest['pairs']}
        observed = {(r['world'], r['language'], r['english']) for r in rows}
        expected = {(world, language, english) for world, language in pairs for english in (False, True)}
        if observed != expected or len(rows) != len(expected):
            raise ValueError(f'{name}: incomplete or repeated responses')
        for row in rows:
            prompt, gold = module.build(row['world'], row['language'], english=row['english'], **options)
            if (row['prompt'] != prompt or row['gold'] != gold or
                    row['correct'] != (parse(row['raw']) == [gold.casefold()])):
                raise ValueError(f'{name}: response or generator mismatch')
        print(name, *(f'{sum(row["correct"] for row in rows if row["english"] == english)}/{len(pairs)}' for english in (False, True)))
        if module is three_object_probe:
            objects = options.get('objects', three_object_probe.OBJECTS)
            conlang_rows = [row for row in rows if not row['english']]
            possible = [suffix_blind_answers(row['prompt'], objects) for row in conlang_rows]
            assert all(row['gold'] in answers and len(answers) > 1
                       for row, answers in zip(conlang_rows, possible))
            random_baseline = sum(1 / len(answers) for answers in possible) / len(possible)
            print(f'  suffix-blind uniform baseline (expected): {random_baseline:.1%}')
            alphabetical = sum(min(answers) == row['gold'] for row, answers in zip(conlang_rows, possible))
            last_mentioned = sum(row['prompt'].split('\n\n')[2].splitlines()[-1].split()[-1].split('-')[0]
                                 == row['gold'] for row in conlang_rows)
            print(f'  suffix-blind alphabetical: {alphabetical}/{len(possible)}; '
                  f'last mentioned: {last_mentioned}/{len(possible)}')
    evolution = archive['evolution']
    for generation in range(2):
        candidates = evolution['manifests'][generation]
        rows = [row for row in evolution['responses'] if row['generation'] == generation]
        if len(candidates) != 6 or len(rows) != 6:
            raise ValueError('Evolution generation is incomplete')
        for candidate in candidates:
            matches = [row for row in rows if row['candidate'] == candidate['candidate']]
            if len(matches) != 1 or any(matches[0][k] != v for k, v in candidate.items()):
                raise ValueError('Evolution response does not match candidate')
            row = matches[0]
            prompt, gold = single_probe.build(len(row['rules']), divisors=row['rules'])
            if (row['prompt'] != prompt or row['gold'] != gold or
                    row['correct'] != (parse(row['raw']) == [gold.casefold()])):
                raise ValueError('Evolution response or generator mismatch')
        print(f'evolution-{generation}', f'{sum(row["correct"] for row in rows)}/{len(rows)}')

if __name__ == '__main__':
    main()
