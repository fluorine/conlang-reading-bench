"""Regrade Luna low on the matched five-object story sets."""
from pathlib import Path
from conlang.verify_sol_comparison import verify_extra

ARCHIVE = Path('reports/luna-low-comparison-responses.json')


def main():
    verify_extra(ARCHIVE, 'gpt-6-luna', 'low', [0.1, 0.5], 'Luna low')


if __name__ == '__main__':
    main()
