"""Offline Tier 5 checks: admission, stage answerability and shortcut baselines."""
import argparse
import json
import time
from random import Random
from statistics import mean, median

from .tier5 import build_story
from .tier5_grammar import LEVELS


def seeds(level_name, count, base):
    rng = Random(f"tier5-offline:{base}:{level_name}")
    return [(rng.randrange(2**31), rng.randrange(2**31)) for _ in range(count)]


def summarize(level_name, count, base=0):
    started = time.time()
    items, failures = [], 0
    for index, (world, language) in enumerate(seeds(level_name, count, base)):
        try:
            items.append(build_story(world, language, level_name, index, answerability=True))
        except ValueError:
            failures += 1
    stages = len(items[0]["answerable"]) if items else 0
    shares, means, unknown = [], [], []
    for stage in range(stages):
        known = [item["answerable"][stage] for item in items if item["answerable"][stage] is not None]
        unknown.append(len(items) - len(known))
        values = [sum(a) / len(a) for a in known]
        shares.append(round(100 * median(values), 1) if known else None)
        means.append(round(100 * mean(values), 1) if known else None)
    readers = items[0]["baselines"].keys() if items else ()
    baselines = {r: round(100 * mean(item["baselines"][r] for item in items), 1) for r in readers}
    final_unique = all(all(item["answerable"][-1]) for item in items)
    return dict(level=level_name, requested=count, built=len(items), rejected=failures,
                stages=stages, median_answerable_percent=shares,
                mean_answerable_percent=means, unknown_stages=unknown,
                final_stage_unique=final_unique, baseline_percent=baselines,
                strongest_baseline=max(baselines.items(), key=lambda kv: kv[1]) if baselines else None,
                seconds=round(time.time() - started, 1))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=200)
    parser.add_argument("--levels", nargs="*", default=list(LEVELS))
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    report = [summarize(name, args.count) for name in args.levels]
    text = json.dumps(report, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
