"""Collect completed five-object comparison transcripts for offline regrading."""
import argparse
from pathlib import Path

from conlang.suite import read, write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--terra-holdout', required=True)
    parser.add_argument('--luna-fresh2', required=True)
    parser.add_argument('--terra-fresh2', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    historical = read('reports/tier3-search-responses.json')
    runs = {'luna-holdout': {'responses': historical['datasets']['syncretic-five-object-holdout'],
                             'metadata': historical['run_metadata']['syncretic-five-object-holdout'],
                             'uncertain_attempts': historical['uncertain_attempts'].get('syncretic-five-object-holdout', [])}}
    for key, directory in (('terra-holdout', args.terra_holdout), ('luna-fresh2', args.luna_fresh2),
                           ('terra-fresh2', args.terra_fresh2)):
        path = Path(directory)
        if list(path.glob('*.pending')):
            raise ValueError(f'{path} has an unresolved request')
        runs[key] = {'metadata': read(path / 'run.json'),
                     'responses': [read(p) for p in sorted(path.glob('*.json')) if p.name != 'run.json'],
                     'uncertain_attempts': [{'file': p.name, **read(p)}
                                            for p in sorted((path / 'uncertain').glob('*.json'))]}
    write(args.out, {'description': 'Matched five-object research comparison; not an official tier.', 'runs': runs})


if __name__ == '__main__':
    main()
