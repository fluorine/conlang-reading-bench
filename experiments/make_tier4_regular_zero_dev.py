"""Freeze a fresh zero-hint regular-grammar development sample."""
import json
from collections import Counter
from pathlib import Path
from random import Random

from conlang.tier4_audit import decode_full
from conlang.tier4_dynamic import build_story


def main():
    rng = Random(430021)
    pairs, rejected, attempts = [], Counter(), 0
    previous_files = ('tier4-confirmation.json', 'tier4-observed-fresh.json',
                      'tier4-deferred-dev.json', 'tier4-policy-audit.json',
                      'tier4-paired-random.json', 'tier4-checkpoint-dev.json',
                      'tier4-focus-fresh-0.json', 'tier4-focus-fresh-1.json',
                      'tier4-focus-fresh-2.json', 'tier4-focus-fresh-3.json',
                      'tier4-compact-dev.json', 'tier4-regular-dev.json',
                      'tier4-regular-confirm-0.json', 'tier4-regular-confirm-1.json',
                      'tier4-regular-confirm-2.json', 'tier4-regular-confirm-3.json')
    previous = {tuple(pair) for name in previous_files for pair in
                json.loads((Path('experiments') / name).read_text(encoding='utf-8'))['pairs']}
    while len(pairs) < 12 and attempts < 10000:
        attempts += 1
        world, language = rng.randrange(2**31), rng.randrange(2**31)
        if (world, language) in previous:
            rejected['previous pair'] += 1
            continue
        try:
            case = build_story(world, language, scheme='unique', observed_hints=True,
                               hint_levels=(0, 1, 10), min_observed_markers=10, context_free=True)
            if decode_full(case['prompts'][2], context_free=True) != case['answers']:
                raise ValueError('independent replay disagrees')
        except ValueError as exc:
            rejected[str(exc)] += 1
            continue
        pairs.append([world, language])
        previous.add((world, language))
    if len(pairs) != 12:
        raise RuntimeError('insufficient valid stories')
    manifest = {'name': 'tier4-regular-zero-dev', 'seed': 430021, 'length': 30,
                'question_count': 4, 'hint_levels': [0, 1, 10], 'scheme': 'unique',
                'context_free': True, 'observed_hints': True, 'min_observed_markers': 10,
                'modes': ['fresh_conlang', 'fresh_english'], 'pairs': pairs,
                'attempts': attempts, 'rejections': dict(rejected),
                'excluded_manifests': list(previous_files),
                'purpose': 'adaptive zero-hint development after one-hint confirmation exceeded target'}
    Path('experiments/tier4-regular-zero-dev.json').write_text(
        json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'{len(pairs)} stories; {attempts} attempts; rejected {dict(rejected)}')


if __name__ == '__main__':
    main()
