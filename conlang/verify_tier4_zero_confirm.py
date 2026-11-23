"""Regrade the 48-story zero-hint confirmation."""
from .verify_tier4_regular_confirm import analyze_family


def main():
    analyze_family('tier4-zero-confirm', (0, 1, 10), 430022)


if __name__ == '__main__':
    main()
