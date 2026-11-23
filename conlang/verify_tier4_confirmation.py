"""Regrade the fresh ten-hint confirmation sample."""
from pathlib import Path
from conlang.verify_tier4_observed import analyze


def main():
    analyze(Path('reports/tier4-confirmation-responses.json'),
            Path('experiments/tier4-confirmation.json'))


if __name__ == '__main__':
    main()
