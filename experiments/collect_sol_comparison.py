"""Collect two completed matched runs for offline regrading."""
import argparse
from pathlib import Path

from conlang.suite import read, write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--holdout', required=True)
    parser.add_argument('--fresh2', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--label', default='Sol low')
    args = parser.parse_args()
    runs = {}
    for name, directory in (('holdout', args.holdout), ('fresh2', args.fresh2)):
        path = Path(directory)
        if list(path.glob('*.pending')):
            raise ValueError(f'{path} has an unresolved request')
        runs[name] = {'metadata': read(path / 'run.json'),
                      'responses': [read(p) for p in sorted(path.glob('*.json')) if p.name != 'run.json'],
                      'uncertain_attempts': [{'file': p.name, **read(p)}
                                             for p in sorted((path / 'uncertain').glob('*.json'))]}
    write(args.out, {'description': f'{args.label} matched research comparison; not an official tier.', 'runs': runs})


if __name__ == '__main__':
    main()
