"""Regrade matched Tier 4 model runs and paired story-level differences."""
import json
from pathlib import Path
from random import Random

from .scoring import parse
from .verify_tier4_dynamic import verify_run
from .verify_tier4_regular_confirm import analyze_family


def main():
    analyze_family('tier4-zero-confirm', (0, 1, 10), 430022)
    base = {}
    for i in range(4):
        archive = json.loads(Path(f'reports/tier4-zero-confirm-{i}-responses.json').read_text(encoding='utf-8'))
        base.update({(r['world'], r['language'], r['mode'], r['stage']): r for r in archive['responses']})
    for model_index, label in enumerate(('luna-medium', 'terra-medium')):
        rows, total_cost, revisions = {}, 0.0, set()
        for i in range(4):
            manifest_path = Path(f'experiments/tier4-zero-{label}-{i}.json')
            archive_path = Path(f'reports/tier4-zero-{label}-{i}-responses.json')
            verify_run(archive_path, manifest_path)
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            archive = json.loads(archive_path.read_text(encoding='utf-8'))
            original = json.loads(Path(f'experiments/tier4-zero-confirm-{i}.json').read_text(encoding='utf-8'))
            if manifest.get('source_manifest') != f'tier4-zero-confirm-{i}.json' or manifest['pairs'] != original['pairs']:
                raise ValueError('comparison stories do not match')
            for row in archive['responses']:
                key = (row['world'], row['language'], row['mode'], row['stage'])
                if key not in base or row['messages'] != base[key]['messages'] or row['answers'] != base[key]['answers']:
                    raise ValueError('comparison prompt or gold mismatch')
                if key in rows:
                    raise ValueError('repeated comparison call')
                rows[key] = row
                total_cost += row['cost']
                revisions.add(row['model'])
        if set(rows) != set(base):
            raise ValueError('incomplete comparison coverage')
        print(f'=== {label}: observed model revisions {sorted(revisions)}; cost ${total_cost:.5f} ===')
        for stage, hints in enumerate((0, 1, 10)):
            model = [r for key, r in rows.items() if key[2] == 'fresh_conlang' and key[3] == stage]
            english = [r for key, r in rows.items() if key[2] == 'fresh_english' and key[3] == stage]
            differences = [(sum(r['marks']) - sum(base[(r['world'], r['language'], 'fresh_conlang', stage)]['marks'])) / 4
                           for r in model]
            rng = Random(430040 + model_index * 3 + stage)
            samples = sorted(sum(rng.choice(differences) for _ in differences) / len(differences)
                             for _ in range(10000))
            missing = sum(max(0, 4 - len(parse(r['raw']))) for r in model)
            print(f'{hints} meanings: conlang {sum(sum(r["marks"]) for r in model)}/192; '
                  f'English {sum(sum(r["marks"]) for r in english)}/192; '
                  f'minus Luna low {100*sum(differences)/len(differences):+.1f} points '
                  f'(95% story bootstrap {100*samples[249]:+.1f} to {100*samples[9749]:+.1f}); '
                  f'missing answers {missing}')
        print(f'capped {sum(r.get("finish_reason") == "length" for r in rows.values())}; '
              f'empty {sum(not r["raw"] for r in rows.values())}')


if __name__ == '__main__':
    main()
