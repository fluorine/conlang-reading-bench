"""Score a Tier 5 run directory: stage curve, DCS, rules to solve and gate checks."""
import argparse
import json
from pathlib import Path
from random import Random
from statistics import mean, median

from .suite import read
from .tier5 import load_manifest, score

# Question tags that a card resolves. Lexical inversion has no card.
TAG_CARD = {"role": "case", "agreement": "agreement", "tense": "tense",
            "negation": "negation", "irrealis": "irrealis", "pronoun": "pronoun"}
BAND = (10.0, 90.0)
TUNING = (30.0, 70.0)


def _bootstrap(values, seed=1776, rounds=10000):
    rng = Random(seed)
    boot = sorted(mean(rng.choices(values, k=len(values))) for _ in range(rounds))
    return [boot[int(0.025 * rounds)], boot[int(0.975 * rounds) - 1]]


def report(manifest_path, run_dir):
    manifest, items = load_manifest(manifest_path)
    run_dir = Path(run_dir)
    missing, capped, cost, calls = 0, 0, 0.0, 0
    stories = []
    for item in items:
        marks = []
        for stage in [*range(len(item["prompts"])), "english"]:
            path = run_dir / f"{item['world_seed']}-{item['language_seed']}-{stage}.json"
            if not path.exists():
                missing += 1
                marks.append([False] * len(item["answers"]))
                continue
            row = read(path)
            prompt = item["prompts"][stage] if stage != "english" else item["english"]
            if row["prompt"] != prompt or row["answers"] != item["answers"]:
                raise ValueError(f"transcript does not match the manifest: {path}")
            marks.append(score(row["raw"], item["answers"]))
            capped += bool(row.get("capped"))
            cost += row["cost"]
            calls += 1
        stories.append((item, marks[:-1], marks[-1]))
    stages = len(items[0]["prompts"])
    curve = [100 * mean(sum(m[s]) / len(m[s]) for _, m, _ in stories) for s in range(stages)]
    per_story = [100 * mean(sum(stage) / len(stage) for stage in m) for _, m, _ in stories]
    rts = []
    for _, m, _ in stories:
        solved = [all(stage) for stage in m]
        rts.append(next((k for k in range(stages) if all(solved[k:])), stages))
    kept = [(a, b) for _, m, _ in stories for k in range(stages - 1)
            for a, b in zip(m[k], m[k + 1]) if a]
    modules = {}
    for tag, card in TAG_CARD.items():
        before, after = [], []
        for item, m, _ in stories:
            if card not in item["cards"]:
                continue
            reveal = item["cards"].index(card) + 1
            for q, tags in enumerate(item["tags"]):
                if tag in tags:
                    for k in range(stages):
                        (after if k >= reveal else before).append(m[k][q])
        if before or after:
            modules[tag] = dict(before=round(100 * mean(before), 1) if before else None,
                                after=round(100 * mean(after), 1) if after else None)
    english = 100 * mean(sum(e) / len(e) for _, _, e in stories)
    dcs = mean(per_story)
    readers = items[0]["baselines"].keys()
    baselines = {r: 100 * mean(item["baselines"][r] for item in items) for r in readers}
    strongest = max(baselines.items(), key=lambda kv: kv[1])
    total = len(items) * (stages + 1)
    checks = dict(
        in_hard_band=BAND[0] <= dcs <= BAND[1],
        in_tuning_band=TUNING[0] <= dcs <= TUNING[1],
        ladder_gap_at_least_30=curve[-1] - curve[0] >= 30,
        final_within_10_of_english=english - curve[-1] <= 10,
        capped_under_2_percent=capped < 0.02 * total,
        dcs_20_above_strongest_baseline=dcs - strongest[1] >= 20,
    )
    return dict(manifest=manifest["name"], level=manifest["level"],
                run=read(run_dir / "run.json") if (run_dir / "run.json").exists() else None,
                complete=missing == 0, missing=missing, calls=calls, cost_usd=round(cost, 4),
                capped=capped, dcs=round(dcs, 2), dcs_interval95=[round(x, 2) for x in _bootstrap(per_story)],
                stage_curve=[round(x, 2) for x in curve], english=round(english, 2),
                rules_to_solve_median=median(rts), rules_to_solve=rts,
                retention=round(100 * mean(b for _, b in kept), 1) if kept else None,
                module_profile=modules,
                baselines={k: round(v, 1) for k, v in baselines.items()},
                strongest_baseline=[strongest[0], round(strongest[1], 1)], checks=checks)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--run", required=True)
    args = parser.parse_args(argv)
    print(json.dumps(report(args.manifest, args.run), indent=2))


if __name__ == "__main__":
    main()
