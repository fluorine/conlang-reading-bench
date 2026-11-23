"""Regrade adaptive intermediate-hint development attempts."""
from pathlib import Path
from conlang.verify_tier4_dynamic import verify_run


def main():
    verify_run(Path('reports/tier4-hint-tuning-responses.json'),
               Path('experiments/tier4-hint-tuning.json'))


if __name__ == '__main__':
    main()
