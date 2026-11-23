"""Freeze 48 fresh regular-grammar stories for the predeclared confirmation."""
import json
from collections import Counter
from pathlib import Path
from random import Random

from conlang.tier4_audit import decode_full
from conlang.tier4_dynamic import build_story


def main():
    rng = Random(430020)
    groups = [[] for _ in range(4)]
    rejected, attempts = Counter(), 0
    previous_files = ('tier4-confirmation.json', 'tier4-observed-fresh.json',
                      'tier4-deferred-dev.json', 'tier4-policy-audit.json',
                      'tier4-paired-random.json', 'tier4-checkpoint-dev.json',
                      'tier4-focus-fresh-0.json', 'tier4-focus-fresh-1.json',
                      'tier4-focus-fresh-2.json', 'tier4-focus-fresh-3.json',
                      'tier4-compact-dev.json', 'tier4-regular-dev.json')
    previous = {tuple(pair) for name in previous_files for pair in
                json.loads((Path('experiments') / name).read_text(encoding='utf-8'))['pairs']}
    while sum(map(len, groups)) < 48 and attempts < 10000:
        attempts += 1
        world, language = rng.randrange(2**31), rng.randrange(2**31)
        if (world, language) in previous:
            rejected['previous pair'] += 1
            continue
        try:
            case = build_story(world, language, scheme='unique', observed_hints=True,
                               hint_levels=(1, 3, 10), min_observed_markers=10,
                               context_free=True)
            if decode_full(case['prompts'][2], context_free=True) != case['answers']:
                raise ValueError('independent replay disagrees')
        except ValueError as exc:
            rejected[str(exc)] += 1
            continue
        groups[sum(map(len, groups)) % 4].append([world, language])
        previous.add((world, language))
    if sum(map(len, groups)) != 48:
        raise RuntimeError('insufficient valid stories')
    for index, pairs in enumerate(groups):
        manifest = {'name': f'tier4-regular-confirm-{index}', 'seed': 430020, 'length': 30,
                    'question_count': 4, 'hint_levels': [1, 3, 10], 'scheme': 'unique',
                    'context_free': True, 'observed_hints': True, 'min_observed_markers': 10,
                    'modes': ['fresh_conlang', 'fresh_english'], 'pairs': pairs,
                    'attempts': attempts, 'rejections': dict(rejected),
                    'excluded_manifests': list(previous_files),
                    'purpose': 'fresh regular-grammar candidate evaluation; fixed before model calls',
                    'analysis_plan': {'primary': 'one-hint fresh-context conlang accuracy',
                        'acceptance': 'score below 40%; initial English and full-grammar accuracy '
                        'at least 90%; no empty or capped requests; 95% paired story-bootstrap '
                        'lower bounds above zero versus both last-name and disclosed-transfer trackers',
                        'output_failures': 'invalid or missing answers count wrong; disclose rates',
                        'secondary': 'three hints, full grammar, English, token use and per-story outcomes'}}
        Path(f'experiments/tier4-regular-confirm-{index}.json').write_text(
            json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'48 stories, 12 per batch; {attempts} attempts; rejected {dict(rejected)}')


if __name__ == '__main__':
    main()
