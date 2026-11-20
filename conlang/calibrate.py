"""Select a transfer count using development data only."""
import re
from statistics import mean
from pathlib import Path

from .runner import MODELS
from .scoring import grade, parse
from .suite import ROOT, TIERS, certified, load_suite, read
from .world import PEOPLE


def assess(length, directory):
    manifest = load_suite(f"dev{length}")
    prompts, keys = certified(manifest)
    controls = load_suite("questions")
    cq, _ = certified(controls)
    reports, blind = [], []
    for model in MODELS:
        run = read(directory / manifest["name"] / f"{model}.json")
        control = read(directory / "questions" / f"{model}.json")
        report = grade(manifest, run)
        if not (report["complete"] and grade(controls, control)["complete"]):
            raise ValueError("development controls and runs must be complete")
        reports.append(report)
        hits = []
        for story, key in keys.items():
            item = story + "/questions"
            if cq[item].split("\n\n")[-1] != prompts[story + "/english"].split("\n\n")[-1]:
                raise ValueError("question-only control text mismatch")
            pred = parse(control["responses"][item]["raw"])
            hits.extend(i < len(pred) and pred[i] == gold.lower() for i, gold in enumerate(key["answers"]))
        blind.append(100 * mean(hits))
    recent = []
    for story, key in keys.items():
        for tier in TIERS:
            passage = prompts[story + "/" + tier].split("Story:\n")[1].split("\n\n")[0]
            name = re.findall(r"\b(?:" + "|".join(PEOPLE) + r")\b", passage)[-1]
            recent.extend(n == name for n in key["answers"])
    halves = []
    ids = list(keys)
    for half in (ids[:6], ids[6:]):
        scores = [100 * mean(sum(r["outcomes"][s + "/" + t]) / 4 for s in half for t in TIERS)
                  for r in reports]
        halves.append(scores[1] - scores[0])
    stronger = max(range(len(reports)), key=lambda i: reports[i]["headline"])
    passed = (halves[0] * halves[1] > 0 and min(r["accuracy"]["english"] for r in reports) >= 90
              and reports[stronger]["headline"] > max(blind[stronger], 100 * mean(recent)))
    return dict(passes=passed, models=list(MODELS), headline=[r["headline"] for r in reports],
                english=[r["accuracy"]["english"] for r in reports], half_differences_pp=halves,
                questions_only=blind, last_person=100 * mean(recent))


def select(directory=ROOT / "results"):
    forms = {str(n): assess(n, Path(directory)) for n in (2, 3)}
    selected = next((int(n) for n, v in forms.items() if v["passes"]), None)
    return dict(selected_length=selected, reference_length=selected or 2, forms=forms,
                decision="shortest passing form" if selected else "neither passed; shortest exploratory reference")
