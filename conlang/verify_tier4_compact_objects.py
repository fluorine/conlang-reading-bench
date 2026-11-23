"""Regrade the object-inventory diagnostic and its object-aware tracker."""
import json
from pathlib import Path
from random import Random

from .tier4_baselines import object_inventory_tracker
from .tier4_compact import OBJECTS, build_story
from .verify_tier4_hint_baseline import analyze


def main():
    archive_path = Path('reports/tier4-compact-objects-dev-responses.json')
    manifest_path = Path('experiments/tier4-compact-objects-dev.json')
    analyze(archive_path, manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    archive = json.loads(archive_path.read_text(encoding='utf-8'))
    rows = {(r['world'], r['language'], r['stage']): r for r in archive['responses']}
    for stage, count in enumerate(manifest['object_hint_counts']):
        total, differences = 0, []
        for world, language in manifest['pairs']:
            case = build_story(world, language, hint_levels=manifest['hint_levels'],
                               min_observed_markers=manifest['min_observed_markers'],
                               object_hint_counts=manifest['object_hint_counts'])
            guesses = object_inventory_tracker(case['prompts'][stage], OBJECTS)
            baseline = sum(a == b for a, b in zip(guesses, case['answers']))
            total += baseline
            differences.append((sum(rows[(world, language, stage)]['marks']) - baseline) / len(OBJECTS))
        rng = Random(430020 + stage)
        samples = sorted(sum(rng.choice(differences) for _ in differences) / len(differences)
                         for _ in range(10000))
        print(f'{count} object-only hints: tracker {total}/{len(differences)*len(OBJECTS)}; '
              f'model minus tracker {100*sum(differences)/len(differences):+.1f} points; '
              f'95% story bootstrap {100*samples[249]:+.1f} to {100*samples[9749]:+.1f}')


if __name__ == '__main__':
    main()
