"""Compare a disclosed-transfer heuristic with saved Tier 4 model responses."""
import json
import random
from pathlib import Path

from .tier4_baselines import last_disclosed_transfer
from .tier4_dynamic import build_story
from .verify_tier4_dynamic import verify_run


def analyze(archive_path, manifest_path):
    verify_run(archive_path, manifest_path)
    archive = json.loads(archive_path.read_text(encoding='utf-8'))
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    rows = {(row['world'], row['language'], row['stage']): row
            for row in archive['responses'] if row['mode'] == 'fresh_conlang'}
    print('Disclosed-transfer baseline (fresh conlang):')
    for stage, count in enumerate(manifest['hint_levels']):
        baseline_total = model_total = 0
        differences = []
        for world, language in manifest['pairs']:
            if manifest.get('variant') == 'compact-three':
                from conlang.tier4_compact import build_story as build_compact, OBJECTS as compact_targets
                case = build_compact(world, language, hint_levels=manifest['hint_levels'],
                                     min_observed_markers=manifest.get('min_observed_markers', 0),
                                     focus_index=manifest.get('focus_index'),
                                     role_hints=manifest.get('role_hints', False),
                                     object_hint_counts=manifest.get('object_hint_counts'))
                prediction = last_disclosed_transfer(case['prompts'][stage], targets=compact_targets)
            else:
                case = build_story(world, language, scheme=manifest['scheme'],
                                   observed_hints=manifest['observed_hints'],
                                   hint_levels=manifest['hint_levels'],
                                   min_observed_markers=manifest.get('min_observed_markers', 0),
                                   defer_target_final=manifest.get('defer_target_final', False),
                                   query_after=manifest.get('query_after'),
                                   reasoning_guide=manifest.get('reasoning_guide', False),
                                   response_format=manifest.get('response_format', 'array'),
                                   focus_index=manifest.get('focus_index'))
                prediction = last_disclosed_transfer(case['prompts'][stage], manifest.get('query_after'))
            if manifest.get('focus_index') is not None:
                prediction = [prediction[manifest['focus_index']]]
            baseline = sum(a == b for a, b in zip(prediction, case['answers']))
            model = sum(rows[(world, language, stage)]['marks'])
            baseline_total += baseline
            model_total += model
            differences.append((model - baseline) / len(case['answers']))
        rng = random.Random(31000 + stage)
        samples = sorted(sum(rng.choice(differences) for _ in differences) / len(differences)
                         for _ in range(10000))
        total = len(differences) * len(case['answers'])
        print(f'{count} meanings: heuristic {baseline_total}/{total}; model {model_total}/{total}; '
              f'difference {100 * sum(differences) / len(differences):+.1f} points '
              f'(95% story bootstrap {100 * samples[249]:+.1f} to {100 * samples[9749]:+.1f})')


def main():
    analyze(Path('reports/tier4-confirmation-responses.json'),
            Path('experiments/tier4-confirmation.json'))
    analyze(Path('reports/tier4-hint-tuning-responses.json'),
            Path('experiments/tier4-hint-tuning.json'))


if __name__ == '__main__':
    main()
