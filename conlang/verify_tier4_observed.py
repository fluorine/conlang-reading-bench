"""Regrade the independently seeded observed-marker Tier 4 sample."""
from pathlib import Path
from conlang.verify_tier4_dynamic import verify_run


def main():
    verify_run(Path('reports/tier4-observed-fresh-responses.json'),
               Path('experiments/tier4-observed-fresh.json'))


if __name__ == '__main__':
    main()
