"""Regrade focused end-of-story development responses."""
from .verify_tier4_focus import analyze_family


def main():
    analyze_family('tier4-final-focus', 'tier4-observed-fresh')


if __name__ == '__main__':
    main()
