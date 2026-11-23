"""Regrade the 48-story regular-grammar evaluation and its predeclared gates."""
import json
from pathlib import Path
from random import Random

from .scoring import parse
from .tier4_baselines import last_disclosed_transfer
from .tier4_dynamic import build_story
from .verify_tier4_dynamic import verify_run


def analyze_family(prefix='tier4-regular-confirm', levels=(1, 3, 10), seed=430020):
    entries, seen, total_cost = [], set(), 0.0
    for index in range(4):
        manifest_path = Path(f'experiments/{prefix}-{index}.json')
        archive_path = Path(f'reports/{prefix}-{index}-responses.json')
        verify_run(archive_path, manifest_path)
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        archive = json.loads(archive_path.read_text(encoding='utf-8'))
        if (len(manifest['pairs']) != 12 or manifest.get('context_free') is not True
                or manifest['hint_levels'] != list(levels) or manifest.get('min_observed_markers') != 10
                or manifest.get('modes') != ['fresh_conlang', 'fresh_english']):
            raise ValueError('unexpected confirmation configuration')
        lookup = {(r['world'], r['language'], r['mode'], r['stage']): r for r in archive['responses']}
        for world, language in manifest['pairs']:
            if (world, language) in seen:
                raise ValueError('repeated confirmation story')
            seen.add((world, language))
            case = build_story(world, language, scheme='unique', observed_hints=True,
                               hint_levels=levels, min_observed_markers=10, context_free=True)
            prediction = last_disclosed_transfer(case['prompts'][0])
            last = case['prompts'][0].split('\n\n')[2].splitlines()[-1].split()[-1].split('-')[0]
            tracker = sum(a == b for a, b in zip(prediction, case['answers']))
            last_count = sum(answer == last for answer in case['answers'])
            model = [lookup[(world, language, 'fresh_conlang', stage)] for stage in range(3)]
            english = [lookup[(world, language, 'fresh_english', stage)] for stage in range(3)]
            entries.append({'model': model, 'english': english, 'tracker': tracker, 'last': last_count})
        total_cost += sum(row['cost'] for row in archive['responses'])
    if len(entries) != 48:
        raise ValueError('incomplete evaluation')
    total = len(entries) * 4
    for stage, hints in enumerate(levels):
        conlang = sum(sum(e['model'][stage]['marks']) for e in entries)
        english = sum(sum(e['english'][stage]['marks']) for e in entries)
        missing = sum(max(0, 4 - len(parse(e['model'][stage]['raw']))) for e in entries)
        print(f'{hints} hints: Luna {conlang}/{total} ({100*conlang/total:.1f}%); '
              f'English {english}/{total} ({100*english/total:.1f}%); missing conlang answers {missing}')
    print(f'tracker {sum(e["tracker"] for e in entries)}/{total}; '
          f'last-name {sum(e["last"] for e in entries)}/{total}; token-valued cost ${total_cost:.5f}')
    bounds = []
    for comparison_seed, key in ((seed, 'tracker'), (seed + 1, 'last')):
        differences = [(sum(e['model'][0]['marks']) - e[key]) / 4 for e in entries]
        rng = Random(comparison_seed)
        samples = sorted(sum(rng.choice(differences) for _ in differences) / len(differences)
                         for _ in range(10000))
        lower, upper = samples[249], samples[9749]
        bounds.append(lower)
        print(f'Luna minus {key}: {100*sum(differences)/len(differences):+.1f} points; '
              f'95% story bootstrap {100*lower:+.1f} to {100*upper:+.1f}')
    all_rows = [row for e in entries for kind in ('model', 'english') for row in e[kind]]
    primary = sum(sum(e['model'][0]['marks']) for e in entries) / total
    primary_story = [sum(e['model'][0]['marks']) / 4 for e in entries]
    rng = Random(seed + 2)
    primary_samples = sorted(sum(rng.choice(primary_story) for _ in primary_story) / len(primary_story)
                             for _ in range(10000))
    print(f'primary accuracy 95% descriptive story bootstrap '
          f'{100*primary_samples[249]:.1f}% to {100*primary_samples[9749]:.1f}%')
    english = sum(sum(e['english'][0]['marks']) for e in entries) / total
    full = sum(sum(e['model'][2]['marks']) for e in entries) / total
    clean = all(row['raw'] and row.get('finish_reason') != 'length' for row in all_rows)
    passed = primary < .4 and english >= .9 and full >= .9 and clean and all(bound > 0 for bound in bounds)
    print(f'predeclared acceptance: {"PASS" if passed else "NOT MET"}; '
          f'primary <40% {primary < .4}; English >=90% {english >= .9}; '
          f'full >=90% {full >= .9}; no empty/capped {clean}; '
          f'both baseline bounds positive {all(bound > 0 for bound in bounds)}')


def main():
    analyze_family()


if __name__ == '__main__':
    main()
