"""Freeze a small development sample with final-transfer markers deferred."""
import json
from collections import Counter
from pathlib import Path
from random import Random

from conlang.tier4_dynamic import build_story


def main():
    rng = Random(430013)
    pairs = []
    rejected = Counter()
    attempts = 0
    while len(pairs) < 6 and attempts < 10000:
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
    if len(pairs) != 6:
        raise RuntimeError('could not find enough valid stories')
    manifest = {'name': 'tier4-deferred-dev', 'seed': 430013, 'length': 30,
                'question_count': 4, 'hint_levels': [10, 20, 30], 'scheme': 'unique',
                'observed_hints': True, 'min_observed_markers': 20, 'defer_target_final': True,
                'modes': ['fresh_conlang', 'fresh_english'], 'pairs': pairs,
                'attempts': attempts, 'rejections': dict(rejected),
                'purpose': 'exploratory development; defer markers on target final transfers; '
                           'not an independent confirmation'}
    Path('experiments/tier4-deferred-dev.json').write_text(
        json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'attempts': attempts, 'rejections': dict(rejected), 'pairs': pairs}))


if __name__ == '__main__':
    main()
