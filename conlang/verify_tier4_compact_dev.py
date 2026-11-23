"""Regrade the three-object development sample."""
from pathlib import Path
from .verify_tier4_hint_baseline import analyze


def main():
    analyze(Path('reports/tier4-compact-dev-responses.json'),
            Path('experiments/tier4-compact-dev.json'))


if __name__ == '__main__':
    main()
