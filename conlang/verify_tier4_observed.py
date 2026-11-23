"""Regrade the independently seeded observed-marker Tier 4 sample."""
from pathlib import Path
import json
import random
from conlang.verify_tier4_dynamic import verify_run
from conlang.tier4_dynamic import build_story


def analyze(archive_path, manifest_path):
    verify_run(archive_path, manifest_path)
    archive = json.loads(archive_path.read_text(encoding='utf-8'))
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    lookup = {(r['world'], r['language'], r['mode'], r['stage']): r for r in archive['responses']}
    differences = {'fresh full minus initial': [], 'continued hints minus no-new-hint': [],
                   'fresh initial minus last-name shortcut': []}
    for world, language in manifest['pairs']:
        rate = lambda mode, stage: sum(lookup[(world, language, mode, stage)]['marks']) / 4
        case = build_story(world, language, scheme='unique', observed_hints=True,
                           hint_levels=manifest.get('hint_levels', [1, 5, 30]),
                           min_observed_markers=manifest.get('min_observed_markers', 0))
        last = case['prompts'][0].split('\n\n')[2].splitlines()[-1].split()[-1].split('-')[0]
        baseline = sum(answer == last for answer in case['answers']) / 4
        differences['fresh full minus initial'].append(rate('fresh_conlang', 2) - rate('fresh_conlang', 0))
        differences['continued hints minus no-new-hint'].append(rate('continued_hints', 2) - rate('continued_nohint', 2))
        differences['fresh initial minus last-name shortcut'].append(rate('fresh_conlang', 0) - baseline)
    for index, (label, values) in enumerate(differences.items()):
        rng = random.Random(430011 + index)
        samples = sorted(sum(rng.choice(values) for _ in values) / len(values) for _ in range(10000))
        print(f'{label}: {100 * sum(values) / len(values):+.1f} points; '
              f'95% story bootstrap {100 * samples[249]:+.1f} to {100 * samples[9749]:+.1f}')


def main():
    analyze(Path('reports/tier4-observed-fresh-responses.json'),
            Path('experiments/tier4-observed-fresh.json'))


if __name__ == '__main__':
    main()
