"""Rebuild and compare matched five-object research responses offline."""
import json
import random
from pathlib import Path

from conlang.scoring import parse
from conlang.three_object_probe import build
from conlang.verify_tier3_search import suffix_blind_answers

ARCHIVE = Path('reports/tier3-comparison-responses.json')
CONFIGS = {'luna': 'gpt-6-luna', 'terra': 'gpt-6.1-terra'}
SUITES = {'holdout': 'syncretic-five-object-holdout',
          'fresh2': 'syncretic-five-object-fresh2'}


def main():
    archive = json.loads(ARCHIVE.read_text(encoding='utf-8'))
    if set(archive['runs']) != {f'{model}-{suite}' for model in CONFIGS for suite in SUITES}:
        raise ValueError('comparison is missing a required run')
    paired = []
    strata = []
    seen_pairs = set()
    for suite, manifest_name in SUITES.items():
        manifest = json.loads(Path(f'experiments/{manifest_name}.json').read_text(encoding='utf-8'))
        pairs = {tuple(pair) for pair in manifest['pairs']}
        if len(pairs) != len(manifest['pairs']) or seen_pairs & pairs:
            raise ValueError('suite seed pairs are duplicated')
        seen_pairs.update(pairs)
        outcomes = {}
        for model, identifier in CONFIGS.items():
            rows = archive['runs'][f'{model}-{suite}']['responses']
            expected = {(world, language, english) for world, language in pairs for english in (False, True)}
            actual = {(row['world'], row['language'], row['english']) for row in rows}
            if actual != expected or len(rows) != len(expected):
                raise ValueError(f'{model}-{suite}: incomplete or repeated items')
            for row in rows:
                prompt, gold = build(row['world'], row['language'], length=manifest['length'],
                                     english=row['english'], syncretism=True,
                                     revealed=manifest['revealed'], objects=tuple(manifest['objects']))
                if (row['prompt'] != prompt or row['gold'] != gold or
                    row['correct'] != (parse(row['raw']) == [gold.casefold()])):
                    raise ValueError(f'{model}-{suite}: prompt or answer mismatch')
                if (row.get('requested_model') != identifier or row.get('effort') != 'medium'
                        or row.get('max_output') != 16384):
                    raise ValueError(f'{model}-{suite}: unexpected configuration')
                outcomes[(model, row['world'], row['language'], row['english'])] = row['correct']
            print(f'{model}-{suite}:', *(f'{sum(row["correct"] for row in rows if row["english"] == english)}/{len(pairs)}' for english in (False, True)))
            print(f'  capped: {sum(row.get("finish_reason") == "length" for row in rows)}; '
                  f'empty: {sum(not row["raw"] for row in rows)}; '
                  f'observed token-valued cost: ${sum(row["cost"] for row in rows):.5f}')
        suite_differences = []
        for world, language in sorted(pairs):
            prompt, gold = build(world, language, length=manifest['length'], syncretism=True,
                                 revealed=manifest['revealed'], objects=tuple(manifest['objects']))
            last = prompt.split('\n\n')[2].splitlines()[-1].split()[-1].split('-')[0]
            possible = suffix_blind_answers(prompt, tuple(manifest['objects']))
            paired.append((outcomes[('terra', world, language, False)] - outcomes[('luna', world, language, False)],
                           last == gold, 1 / len(possible)))
            suite_differences.append(paired[-1][0])
        strata.append(suite_differences)
    observed = sum(row[0] for row in paired) / len(paired)
    rng = random.Random(492014)
    samples = sorted(sum(stratum[rng.randrange(len(stratum))] for stratum in strata for _ in stratum)
                     / len(paired) for _ in range(10000))
    print(f'Terra minus Luna paired accuracy: {observed:+.1%}; '
          f'suite-stratified bootstrap 95% interval {samples[249]:+.1%} to {samples[9749]:+.1%}')
    print(f'Last-name baseline: {sum(row[1] for row in paired)}/{len(paired)}; '
          f'suffix-blind random expected: {sum(row[2] for row in paired)/len(paired):.1%}')


if __name__ == '__main__':
    main()
