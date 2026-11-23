"""Regrade Sonnet 5.5 low on the matched five-object story sets."""
from pathlib import Path
from conlang.verify_sol_comparison import verify_extra

ARCHIVE = Path('reports/tier3-sonnet-low-responses.json')


def main():
    verify_extra(ARCHIVE, 'claude-sonnet-5-5', 'low', [2, 10], 'Sonnet 5.5 low', max_output=4096)


if __name__ == '__main__':
    main()
