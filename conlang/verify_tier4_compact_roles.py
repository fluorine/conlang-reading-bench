"""Regrade compact role-inventory diagnostics and the role-aware shortcut."""
import json
from pathlib import Path
from random import Random

from .tier4_baselines import last_role_recipient
from .tier4_compact import build_story
from .verify_tier4_hint_baseline import analyze


def main():
    archive_path = Path('reports/tier4-compact-roles-dev-responses.json')
    manifest_path = Path('experiments/tier4-compact-roles-dev.json')
    analyze(archive_path, manifest_path)
    archive = json.loads(archive_path.read_text(encoding='utf-8'))
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    rows = {(row['world'], row['language'], row['stage']): row for row in archive['responses']}
    totals, differences = 0, []
    for world, language in manifest['pairs']:
        case = build_story(world, language, hint_levels=manifest['hint_levels'],
                           min_observed_markers=manifest['min_observed_markers'], role_hints=True)
        guess = last_role_recipient(case['prompts'][0])
        base = sum(name == guess for name in case['answers'])
        totals += base
        differences.append((sum(rows[(world, language, 0)]['marks']) - base) / 3)
    rng = Random(430018)
    samples = sorted(sum(rng.choice(differences) for _ in differences) / len(differences)
                     for _ in range(10000))
    print(f'role-aware last recipient {totals}/{3 * len(differences)}; '
          f'Luna minus shortcut {100*sum(differences)/len(differences):+.1f} points; '
          f'95% story bootstrap {100*samples[249]:+.1f} to {100*samples[9749]:+.1f}')


if __name__ == '__main__':
    main()
