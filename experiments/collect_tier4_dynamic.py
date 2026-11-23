"""Collect a completed progressive-hint run for offline verification."""
import argparse
from pathlib import Path

from conlang.suite import read, write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    path = Path(args.run)
    if list(path.glob('*.pending')):
        raise ValueError('run contains unresolved requests')
    write(args.out, {'description': 'Tier 4 dynamic development run; not an official benchmark.',
                     'metadata': read(path / 'run.json'),
                     'responses': [read(p) for p in sorted(path.glob('*.json')) if p.name != 'run.json'],
                     'uncertain_attempts': [{'file': p.name, **read(p)}
                                            for p in sorted((path / 'uncertain').glob('*.json'))]})


if __name__ == '__main__':
    main()
