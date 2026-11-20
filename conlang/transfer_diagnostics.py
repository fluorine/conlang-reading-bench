"""Completion rates and the last-person baseline for paired transfer suites."""
import argparse
import json
import re

from .scoring import grade, parse
from .suite import certified, load_suite, read
from .world import PEOPLE

NAME = re.compile(r"\b(?:" + "|".join(PEOPLE) + r")\b")
VALID_NAMES = {name.casefold() for name in PEOPLE}


def summarize(manifest, bundles):
    prompts, keys = certified(manifest)
    conditions = manifest["conditions"]
    baseline = {}
    for condition in conditions:
        correct = 0
        for story, key in keys.items():
            passage = prompts[f"{story}/{condition}"].split("Story:\n", 1)[1].split("\n\n", 1)[0]
            guess = NAME.findall(passage)[-1]
            correct += sum(answer == guess for answer in key["answers"])
        baseline[condition] = correct

    results = []
    for bundle in bundles:
        scored = grade(manifest, bundle)
        if not scored["complete"]:
            raise ValueError("diagnostics require every request in the suite")
        rows = {}
        cap = bundle["settings"]["max_completion_tokens"]
        for condition in conditions:
            answered = correct = full = empty = capped_empty = 0
            for story in keys:
                item = f"{story}/{condition}"
                row = bundle["responses"][item]
                n = sum(value in VALID_NAMES for value in parse(row["raw"]))
                answered += n
                correct += sum(scored["outcomes"][item])
                full += n == 4
                if not row["raw"].strip():
                    empty += 1
                    capped_empty += row.get("usage", {}).get("completion_tokens") == cap
            rows[condition] = dict(correct=correct, answered=answered, wrong=answered - correct,
                                   full_responses=full, empty_responses=empty,
                                   empty_at_cap=capped_empty)
        results.append(dict(settings=bundle["settings"], usage=bundle.get("usage_summary"), conditions=rows))
    return dict(stories=len(keys), questions_per_condition=4 * len(keys),
                last_person_correct=baseline, results=results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", choices=("transfer4", "transfer4fresh"))
    parser.add_argument("bundles", nargs="*")
    args = parser.parse_args()
    print(json.dumps(summarize(load_suite(args.suite), [read(p) for p in args.bundles]), indent=2))


if __name__ == "__main__":
    main()
