"""Regrade the zero-hint regular-grammar development sample."""
import json
from pathlib import Path
from random import Random

from .tier4_dynamic import build_story
from .verify_tier4_hint_baseline import analyze


def main():
    archive_path = Path('reports/tier4-regular-zero-dev-responses.json')
    manifest_path = Path('experiments/tier4-regular-zero-dev.json')
    analyze(archive_path, manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    archive = json.loads(archive_path.read_text(encoding='utf-8'))
    rows = {(r['world'], r['language']): r for r in archive['responses']
            if r['mode'] == 'fresh_conlang' and r['stage'] == 0}
    differences = []
    for world, language in manifest['pairs']:
        case = build_story(world, language, scheme='unique', observed_hints=True,
                           hint_levels=(0, 1, 10), min_observed_markers=10, context_free=True)
        last = case['prompts'][0].split('\n\n')[2].splitlines()[-1].split()[-1].split('-')[0]
        baseline = sum(answer == last for answer in case['answers'])
        differences.append((sum(rows[(world, language)]['marks']) - baseline) / len(case['answers']))
    rng = Random(430021)
    samples = sorted(sum(rng.choice(differences) for _ in differences) / len(differences)
                     for _ in range(10000))
    print(f'Luna minus last-name {100*sum(differences)/len(differences):+.1f} points; '
          f'95% story bootstrap {100*samples[249]:+.1f} to {100*samples[9749]:+.1f}')


if __name__ == '__main__':
    main()
