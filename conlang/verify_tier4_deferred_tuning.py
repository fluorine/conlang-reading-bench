"""Regrade adaptive hint-count tuning on the deferred-marker development stories."""
from pathlib import Path
from .verify_tier4_hint_baseline import analyze


def main():
    analyze(Path('reports/tier4-deferred-tuning-responses.json'),
            Path('experiments/tier4-deferred-tuning.json'))


if __name__ == '__main__':
    main()
