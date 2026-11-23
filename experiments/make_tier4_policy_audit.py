"""Generate a reproducible offline sample to audit deferred-hint leakage."""
import json
from collections import Counter
from pathlib import Path
from random import Random

from conlang.tier4_dynamic import build_story


def main():
    rng = Random(430014)
    pairs, rejected, attempts = [], Counter(), 0
    while len(pairs) < 64 and attempts < 10000:
        attempts += 1
        world, language = rng.randrange(2**31), rng.randrange(2**31)
        try:
            build_story(world, language, scheme='unique', observed_hints=True,
                        hint_levels=(10, 20, 30), min_observed_markers=20,
                        defer_target_final=True)
        except ValueError as exc:
            rejected[str(exc)] += 1
            continue
        pairs.append([world, language])
    if len(pairs) != 64:
        raise RuntimeError('insufficient valid stories')
    manifest = {'name': 'tier4-policy-audit', 'seed': 430014, 'length': 30,
                'question_count': 4, 'hint_levels': [10, 20, 30], 'scheme': 'unique',
                'observed_hints': True, 'min_observed_markers': 20,
                'defer_target_final': True, 'pairs': pairs, 'attempts': attempts,
                'rejections': dict(rejected), 'purpose': 'offline policy-leak audit; no model calls'}
    Path('experiments/tier4-policy-audit.json').write_text(json.dumps(manifest, indent=2) + '\n',
                                                           encoding='utf-8')
    print(f'{len(pairs)} stories; {attempts} attempts; rejected {dict(rejected)}')


if __name__ == '__main__':
    main()
