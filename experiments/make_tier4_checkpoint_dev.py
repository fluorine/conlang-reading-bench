"""Create fresh midpoint-question development stories without model selection."""
import json
from collections import Counter
from pathlib import Path
from random import Random

from conlang.tier4_audit import decode_full
from conlang.tier4_checkpoint import suffix_blind_checkpoint
from conlang.tier4_dynamic import build_story


def main():
    rng = Random(430016)
    pairs, rejected, attempts = [], Counter(), 0
    previous_files = ('tier4-confirmation.json', 'tier4-observed-fresh.json',
                      'tier4-deferred-dev.json', 'tier4-policy-audit.json',
                      'tier4-paired-random.json')
    previous = {tuple(pair) for filename in previous_files for pair in
                json.loads((Path('experiments') / filename).read_text(encoding='utf-8'))['pairs']}
    while len(pairs) < 8 and attempts < 10000:
        attempts += 1
        world, language = rng.randrange(2**31), rng.randrange(2**31)
        if (world, language) in previous:
            rejected['previous pair'] += 1
            continue
        try:
            case = build_story(world, language, scheme='unique', observed_hints=True,
                               hint_levels=(1, 3, 30), min_observed_markers=20,
                               query_after=15)
            possible = suffix_blind_checkpoint(case['prompts'][0], 15)
            if any(len(possible[i]) < 2 or answer not in possible[i]
                   for i, answer in enumerate(case['answers'])):
                raise ValueError('suffix-free shortcut determines checkpoint answer')
            if decode_full(case['prompts'][2], query_after=15) != case['answers']:
                raise ValueError('independent checkpoint audit disagrees')
        except ValueError as exc:
            rejected[str(exc)] += 1
            continue
        pairs.append([world, language])
    if len(pairs) != 8:
        raise RuntimeError('insufficient valid stories')
    manifest = {'name': 'tier4-checkpoint-dev', 'seed': 430016, 'length': 30,
                'question_count': 4, 'query_after': 15, 'hint_levels': [1, 3, 30],
                'scheme': 'unique', 'observed_hints': True, 'min_observed_markers': 20,
                'modes': ['fresh_conlang', 'fresh_english'], 'pairs': pairs,
                'attempts': attempts, 'rejections': dict(rejected),
                'excluded_manifests': list(previous_files),
                'purpose': 'adaptive development: fixed midpoint questions, random answer-independent hints; '
                           'hint levels chosen after inspecting offline shortcut scores'}
    Path('experiments/tier4-checkpoint-dev.json').write_text(
        json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'{len(pairs)} stories; {attempts} attempts; rejected {dict(rejected)}')


if __name__ == '__main__':
    main()
