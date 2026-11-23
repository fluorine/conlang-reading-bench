"""Regrade focused-question trials and compare matched multi-question calls."""
import json
from pathlib import Path
from random import Random

from .verify_tier4_dynamic import verify_run


def analyze_family(prefix='tier4-focus', original_name='tier4-checkpoint-dev'):
    original_path = Path(f'reports/{original_name}-responses.json')
    original_manifest_path = Path(f'experiments/{original_name}.json')
    verify_run(original_path, original_manifest_path)
    original_manifest = json.loads(original_manifest_path.read_text(encoding='utf-8'))
    original = json.loads(original_path.read_text(encoding='utf-8'))
    original_rows = {(r['world'], r['language'], r['stage']): r
                     for r in original['responses'] if r['mode'] == 'fresh_conlang'}
    results = {}
    cost = 0.0
    for index in range(4):
        manifest_path = Path(f'experiments/{prefix}-{index}-dev.json')
        archive_path = Path(f'reports/{prefix}-{index}-dev-responses.json')
        verify_run(archive_path, manifest_path)
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        archive = json.loads(archive_path.read_text(encoding='utf-8'))
        if (manifest.get('focus_index') != index or manifest['pairs'] != original_manifest['pairs']
                or manifest['hint_levels'] != original_manifest['hint_levels']
                or manifest.get('query_after') != original_manifest.get('query_after')):
            raise ValueError('mismatched focus manifest')
        for row in archive['responses']:
            original_row = original_rows[(row['world'], row['language'], row['stage'])]
            if row['answers'] != [original_row['answers'][index]]:
                raise ValueError('focus gold mismatch')
            results[(row['world'], row['language'], row['stage'], index)] = row
            cost += row['cost']
    for stage, hints in enumerate(original_manifest['hint_levels']):
        differences = []
        focused_total = joint_total = 0
        for world, language in original_manifest['pairs']:
            original_row = original_rows[(world, language, stage)]
            focused = sum(results[(world, language, stage, i)]['marks'][0] for i in range(4))
            joint = sum(original_row['marks'])
            focused_total += focused
            joint_total += joint
            differences.append((focused - joint) / 4)
        rng = Random(430016 + stage)
        samples = sorted(sum(rng.choice(differences) for _ in differences) / len(differences)
                         for _ in range(10000))
        total = 4 * len(original_manifest['pairs'])
        print(f'{hints} hints: focused {focused_total}/{total}, joint {joint_total}/{total}; '
              f'difference {100*sum(differences)/len(differences):+.1f} points; '
              f'95% story bootstrap {100*samples[249]:+.1f} to {100*samples[9749]:+.1f}')
    print(f'focused token-valued cost ${cost:.5f}; no new English calls')


def main():
    analyze_family()


if __name__ == '__main__':
    main()
