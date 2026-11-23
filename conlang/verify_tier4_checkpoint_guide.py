"""Regrade the adaptive midpoint procedural-guidance run."""
from pathlib import Path
from .verify_tier4_hint_baseline import analyze


def main():
    analyze(Path('reports/tier4-checkpoint-guide-dev-responses.json'),
            Path('experiments/tier4-checkpoint-guide-dev.json'))


if __name__ == '__main__':
    main()
