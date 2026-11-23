"""Regrade adaptive intermediate-hint development attempts."""
from pathlib import Path
import json
import random
from conlang.verify_tier4_dynamic import verify_run
from conlang.tier4_dynamic import build_story
from conlang.verify_tier4_observed import main as verify_baseline


def main():
    verify_baseline()
    archive_path = Path('reports/tier4-hint-tuning-responses.json')
    manifest_path = Path('experiments/tier4-hint-tuning.json')
    verify_run(archive_path, manifest_path)
    archive = json.loads(archive_path.read_text(encoding='utf-8'))
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    baseline = json.loads(Path('reports/tier4-observed-fresh-responses.json').read_text(encoding='utf-8'))
    records = {(r['world'], r['language'], r['stage']): r for r in archive['responses']}
    initial = {(r['world'], r['language']): r for r in baseline['responses']
               if r['mode'] == 'fresh_conlang' and r['stage'] == 0}
    for stage, count in enumerate(manifest['hint_levels']):
        differences = []
        for world, language in manifest['pairs']:
            case = build_story(world, language, scheme='unique', observed_hints=True)
            last = case['prompts'][0].split('\n\n')[2].splitlines()[-1].split()[-1].split('-')[0]
            score = sum(records[(world, language, stage)]['marks']) / 4
            differences.append((score - sum(initial[(world, language)]['marks']) / 4,
                                score - sum(answer == last for answer in case['answers']) / 4))
        for index, label in enumerate(('initial score', 'last-name shortcut')):
            values = [row[index] for row in differences]
            rng = random.Random(431000 + stage * 2 + index)
            samples = sorted(sum(rng.choice(values) for _ in values) / len(values) for _ in range(10000))
            print(f'{count} hints minus {label}: {100 * sum(values) / len(values):+.1f} points; '
                  f'95% descriptive story bootstrap {100 * samples[249]:+.1f} to {100 * samples[9749]:+.1f}')


if __name__ == '__main__':
    main()
