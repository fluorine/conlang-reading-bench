"""Regrade a target-balanced fresh focused-question development evaluation."""
import json
from pathlib import Path
from random import Random

from .tier4_baselines import last_disclosed_transfer
from .tier4_dynamic import OBJECTS, TARGETS, build_story
from .tier4_checkpoint import suffix_blind_checkpoint
from .verify_tier4_dynamic import verify_run


def main():
    groups, all_pairs, total_cost = [], set(), 0.0
    for index in range(4):
        manifest_path = Path(f'experiments/tier4-focus-fresh-{index}.json')
        archive_path = Path(f'reports/tier4-focus-fresh-{index}-responses.json')
        verify_run(archive_path, manifest_path)
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        archive = json.loads(archive_path.read_text(encoding='utf-8'))
        if (manifest.get('focus_index') != index or len(manifest['pairs']) != 8
                or manifest['hint_levels'] != [1, 3, 30] or manifest.get('query_after') != 15
                or manifest.get('modes') != ['fresh_conlang', 'fresh_english']):
            raise ValueError('invalid target group')
        pairs = [tuple(pair) for pair in manifest['pairs']]
        if all_pairs.intersection(pairs):
            raise ValueError('story repeated across target groups')
        all_pairs.update(pairs)
        lookup = {(r['world'], r['language'], r['mode'], r['stage']): r for r in archive['responses']}
        observations = []
        for world, language in pairs:
            case = build_story(world, language, scheme='unique', observed_hints=True,
                               hint_levels=(1, 3, 30), min_observed_markers=20,
                               query_after=15, focus_index=index)
            answer = case['answers'][0]
            prompt = case['prompts'][0]
            guess = last_disclosed_transfer(prompt, 15)[index]
            lines = prompt.split('\n\n')[2].splitlines()
            last = lines[1 + len(OBJECTS) + 15 - 1].split()[-1].split('-')[0]
            possible = suffix_blind_checkpoint(prompt, 15)[OBJECTS.index(TARGETS[index])]
            if answer not in possible or len(possible) < 2:
                raise ValueError('invalid suffix-blind possibilities')
            observations.append({'marks': [int(lookup[(world, language, 'fresh_conlang', s)]['marks'][0])
                                            for s in range(3)],
                                 'english': [int(lookup[(world, language, 'fresh_english', s)]['marks'][0])
                                             for s in range(3)],
                                 'tracker': int(guess == answer), 'last': int(last == answer),
                                 'blind': 1 / len(possible)})
        groups.append(observations)
        total_cost += sum(row['cost'] for row in archive['responses'])
    rows = [row for group in groups for row in group]
    n = len(rows)
    for stage, hints in enumerate((1, 3, 30)):
        print(f'{hints} hints: Luna {sum(r["marks"][stage] for r in rows)}/{n}; '
              f'English {sum(r["english"][stage] for r in rows)}/{n}')
    print(f'one-hint tracker {sum(r["tracker"] for r in rows)}/{n}; '
          f'checkpoint last-name {sum(r["last"] for r in rows)}/{n}; '
          f'suffix-blind uniform expected {100*sum(r["blind"] for r in rows)/n:.1f}%; '
          f'cost ${total_cost:.5f}')
    for i, group in enumerate(groups):
        print(f'{TARGETS[i]}: one-hint Luna {sum(r["marks"][0] for r in group)}/8; '
              f'tracker {sum(r["tracker"] for r in group)}/8')
    for seed, key in ((430017, 'tracker'), (430018, 'last')):
        diffs = [[r['marks'][0] - r[key] for r in group] for group in groups]
        rng = Random(seed)
        samples = sorted(sum(sum(rng.choice(group) for _ in group) for group in diffs) / n
                         for _ in range(10000))
        point = sum(sum(group) for group in diffs) / n
        print(f'Luna minus {key}: {100*point:+.1f} points; 95% target-stratified story bootstrap '
              f'{100*samples[249]:+.1f} to {100*samples[9749]:+.1f}')


if __name__ == '__main__':
    main()
