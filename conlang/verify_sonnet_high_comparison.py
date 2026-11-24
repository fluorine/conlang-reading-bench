"""Regrade Sonnet 5.5 high on the matched five-object story sets."""
from pathlib import Path
from conlang.verify_sol_comparison import verify_extra

ARCHIVE = Path('reports/tier3-sonnet-high-responses.json')


def main():
    verify_extra(ARCHIVE, 'claude-sonnet-5-5', 'high', [2, 10], 'Sonnet 5.5 high', max_output=8192)


if __name__ == '__main__':
    main()
