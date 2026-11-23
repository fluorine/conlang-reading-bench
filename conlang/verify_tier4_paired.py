"""Regrade paired hint-policy development responses and story-level contrasts."""
import json
from pathlib import Path
from random import Random

from .verify_tier4_hint_baseline import analyze


def main():
    manifests = {key: Path(f'experiments/tier4-paired-{key}.json') for key in ('random', 'deferred')}
    archives = {key: Path(f'reports/tier4-paired-{key}-responses.json') for key in manifests}
    data = {}
    for key in manifests:
        print(f'--- {key} ---')
        analyze(archives[key], manifests[key])
        data[key] = (json.loads(manifests[key].read_text(encoding='utf-8')),
                     json.loads(archives[key].read_text(encoding='utf-8')))
    left, right = data['random'][0], data['deferred'][0]
    if (left['pairs'] != right['pairs'] or left['hint_levels'] != right['hint_levels']
            or left['defer_target_final'] or not right['defer_target_final']):
        raise ValueError('paired manifests do not match')
    rows = {key: {(r['world'], r['language'], r['stage']): r
                  for r in data[key][1]['responses'] if r['mode'] == 'fresh_conlang'}
            for key in data}
    for stage, hints in enumerate(left['hint_levels']):
        differences = []
        for world, language in left['pairs']:
            one = rows['random'][(world, language, stage)]
            two = rows['deferred'][(world, language, stage)]
            if one['answers'] != two['answers']:
                raise ValueError('paired gold answers differ')
            differences.append((sum(two['marks']) - sum(one['marks'])) / len(one['answers']))
        rng = Random(430015 + stage)
        samples = sorted(sum(rng.choice(differences) for _ in differences) / len(differences)
                         for _ in range(10000))
        print(f'{hints} hints: deferred minus randomized '
              f'{100 * sum(differences)/len(differences):+.1f} points; '
              f'95% story bootstrap {100*samples[249]:+.1f} to {100*samples[9749]:+.1f}')


if __name__ == '__main__':
    main()
