"""Freeze a three-object Tier 4 development sample without model selection."""
import json
from collections import Counter
from pathlib import Path
from random import Random

from conlang.tier4_audit import decode_full
from conlang.tier4_compact import OBJECTS, build_story
from conlang.verify_tier3_search import suffix_blind_answers


def main():
    rng = Random(430018)
    pairs, rejected, attempts = [], Counter(), 0
    previous_files = ('tier4-confirmation.json', 'tier4-observed-fresh.json',
                      'tier4-deferred-dev.json', 'tier4-policy-audit.json',
                      'tier4-paired-random.json', 'tier4-checkpoint-dev.json',
                      'tier4-focus-fresh-0.json', 'tier4-focus-fresh-1.json',
                      'tier4-focus-fresh-2.json', 'tier4-focus-fresh-3.json')
    previous = {tuple(pair) for filename in previous_files for pair in
                json.loads((Path('experiments') / filename).read_text(encoding='utf-8'))['pairs']}
    while len(pairs) < 12 and attempts < 10000:
        attempts += 1
        world, language = rng.randrange(2**31), rng.randrange(2**31)
        if (world, language) in previous:
            rejected['previous pair'] += 1
            continue
        try:
            case = build_story(world, language, hint_levels=(1, 3, 18), min_observed_markers=10)
            if decode_full(case['prompts'][2], objects=OBJECTS, targets=OBJECTS) != case['answers']:
                raise ValueError('independent full replay disagrees')
            for index, answer in enumerate(case['answers']):
                possible = suffix_blind_answers(case['prompts'][0], OBJECTS, index)
                if len(possible) < 2 or answer not in possible:
                    raise ValueError('suffix-blind answer determined')
        except ValueError as exc:
            rejected[str(exc)] += 1
            continue
        pairs.append([world, language])
        previous.add((world, language))
    if len(pairs) != 12:
        raise RuntimeError('insufficient valid stories')
    manifest = {'name': 'tier4-compact-dev', 'variant': 'compact-three', 'seed': 430018,
                'length': 30, 'question_count': 3, 'hint_levels': [1, 3, 18],
                'scheme': 'unique', 'observed_hints': True, 'min_observed_markers': 10,
                'modes': ['fresh_conlang', 'fresh_english'], 'pairs': pairs,
                'attempts': attempts, 'rejections': dict(rejected),
                'excluded_manifests': list(previous_files),
                'purpose': 'development: same transfer grammar with three objects and randomized hints; '
                           'not independent confirmation'}
    Path('experiments/tier4-compact-dev.json').write_text(
        json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'{len(pairs)} stories; {attempts} attempts; rejected {dict(rejected)}')


if __name__ == '__main__':
    main()
