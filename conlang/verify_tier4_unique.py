"""Regrade the unique-marker progressive-hint development run."""
from pathlib import Path
from conlang.verify_tier4_dynamic import verify_run


def main():
    verify_run(Path('reports/tier4-unique-dev-responses.json'), Path('experiments/tier4-unique-dev.json'))


if __name__ == '__main__':
    main()
