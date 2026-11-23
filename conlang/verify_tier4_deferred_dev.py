"""Regrade the exploratory deferred-marker sample and its heuristic."""
from pathlib import Path
from .verify_tier4_hint_baseline import analyze


def main():
    analyze(Path('reports/tier4-deferred-dev-responses.json'),
            Path('experiments/tier4-deferred-dev.json'))


if __name__ == '__main__':
    main()
