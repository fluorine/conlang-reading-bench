"""Freeze identical stories valid under randomized and deferred hint policies."""
import json
from collections import Counter
from pathlib import Path
from random import Random

from conlang.tier4_dynamic import build_story


def main():
    rng = Random(430015)
    pairs, rejected, attempts = [], Counter(), 0
    previous = set()
    previous_files = ('tier4-confirmation.json', 'tier4-observed-fresh.json',
                      'tier4-deferred-dev.json', 'tier4-policy-audit.json')
    for filename in previous_files:
        path = Path('experiments') / filename
        for pair in json.loads(path.read_text(encoding='utf-8')).get('pairs', []):
            previous.add(tuple(pair))
    while len(pairs) < 12 and attempts < 10000:
        attempts += 1
        world, language = rng.randrange(2**31), rng.randrange(2**31)
        if (world, language) in previous:
            rejected['previous pair'] += 1
            continue
        try:
            for deferred in (False, True):
                build_story(world, language, scheme='unique', observed_hints=True,
                            hint_levels=(10, 20, 30), min_observed_markers=20,
                            defer_target_final=deferred)
        except ValueError as exc:
            rejected[str(exc)] += 1
            continue
        pairs.append([world, language])
    if len(pairs) != 12:
        raise RuntimeError('insufficient valid stories')
    common = {'seed': 430015, 'length': 30, 'question_count': 4,
              'hint_levels': [10, 20, 30], 'scheme': 'unique', 'observed_hints': True,
              'min_observed_markers': 20, 'pairs': pairs, 'attempts': attempts,
              'rejections': dict(rejected), 'excluded_manifests': list(previous_files),
              'purpose': 'paired development comparison; '
              'accepted only when both policies give unique answers; not a final benchmark'}
    for label, deferred, modes in [('random', False, ['fresh_conlang', 'fresh_english']),
                                    ('deferred', True, ['fresh_conlang'])]:
        manifest = {**common, 'name': 'tier4-paired-' + label,
                    'defer_target_final': deferred, 'modes': modes}
        Path(f'experiments/tier4-paired-{label}.json').write_text(
            json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'{len(pairs)} matched stories; {attempts} attempts; rejected {dict(rejected)}')


if __name__ == '__main__':
    main()
