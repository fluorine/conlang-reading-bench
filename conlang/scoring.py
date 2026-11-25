"""Offline, exact, per-question grading and paired uncertainty."""
import json
import random
import re
from statistics import mean

from . import VERSION
from .suite import TIERS, certified, digest


SCORER = "0.1.1"
FINAL_ARRAY_SCORER = "final-array-1.0"


def parse(raw, *, strict=False):
    if isinstance(raw, str) and not strict:
        fence = re.fullmatch(r"```(?:json)?[ \t]*\r?\n(.*?)\r?\n```", raw.strip(), re.DOTALL | re.IGNORECASE)
        if fence:
            raw = fence.group(1)
    try:
        values = json.loads(raw)
    except (ValueError, TypeError):
        return []
    if not isinstance(values, list) or len(values) > 4:
        return []
    return [v.strip().casefold() if isinstance(v, str) else "" for v in values]


def parse_final_answer(raw, max_items=4):
    """Parse a JSON answer array at the end of a reply, allowing preceding text.

    The only permitted trailing material is a closing Markdown fence or a
    matching Markdown bold delimiter. This is
    an explicitly separate regrade; it does not change the original scorer or
    stored response marks. Apply the same rule to every compared model.
    """
    if not isinstance(raw, str):
        return []
    text = raw.strip()
    decoder = json.JSONDecoder()
    for index in range(len(text) - 1, -1, -1):
        if text[index] != '[':
            continue
        try:
            value, end = decoder.raw_decode(text[index:])
        except ValueError:
            continue
        suffix = text[index + end:].strip()
        bold = suffix == '**' and text[:index].rstrip().endswith('**')
        fenced = suffix == '```' and re.search(r'```(?:json)?\s*$', text[:index], re.IGNORECASE)
        if (suffix != '' and not bold and not fenced) or not isinstance(value, list) or len(value) > max_items:
            continue
        if not all(isinstance(item, str) for item in value):
            return []
        return [item.strip().casefold() for item in value]
    return []


def grade(manifest, bundle, *, strict=False):
    prompts, keys = certified(manifest)
    if bundle["version"] != VERSION or bundle["suite_hash"] != digest([manifest, prompts]):
        raise ValueError("protocol or suite hash mismatch")
    rows = bundle["responses"]
    if rows.keys() - prompts.keys():
        raise ValueError("unexpected response IDs")
    by_tier = {c: [] for c in manifest["conditions"]}
    outcomes, missing = {}, []
    for item, prompt in prompts.items():
        story, tier = item.split("/")
        row = rows.get(item)
        predicted = []
        if row is None:
            missing.append(item)
        else:
            if row["prompt_hash"] != digest(prompt) or not isinstance(row["raw"], str):
                raise ValueError(f"invalid response for {item}")
            predicted = parse(row["raw"], strict=strict)
        marks = [i < len(predicted) and predicted[i] == name.casefold()
                 for i, name in enumerate(keys[story]["answers"])]
        outcomes[item] = marks
        by_tier[tier].append(marks)
    accuracy = {t: 100 * mean(sum(m) / 4 for m in rows) for t, rows in by_tier.items()}
    solved = {t: 100 * mean(all(m) for m in rows) for t, rows in by_tier.items()}
    headline = mean(accuracy[t] for t in TIERS) if all(t in accuracy for t in TIERS) else None
    return dict(version=VERSION, scorer_version="0.1.0" if strict else SCORER,
                complete=not missing, missing=missing, accuracy=accuracy,
                all_four_correct=solved, headline=headline, outcomes=outcomes,
                english_minus_grammar=accuracy["english"] - accuracy["grammar"]
                if "grammar" in accuracy and "english" in accuracy else None)


def compare(manifest, a, b):
    reports = [grade(manifest, run) for run in (a, b)]
    if not all(r["complete"] and r["headline"] is not None for r in reports):
        raise ValueError("comparison requires complete, compatible comprehension runs")
    deltas = []
    for item in reports[0]["outcomes"]:
        story, tier = item.split("/")
        if tier == TIERS[0]:
            values = [mean(sum(r["outcomes"][f"{story}/{t}"]) / 4 for t in TIERS) for r in reports]
            deltas.append(100 * (values[1] - values[0]))
    rng = random.Random(1776)
    boot = sorted(mean(rng.choices(deltas, k=len(deltas))) for _ in range(10000))
    return dict(direction="second minus first, percentage points", paired_stories=len(deltas),
                difference=mean(deltas), interval95=[boot[249], boot[9749]],
                resolved=boot[249] > 0 or boot[9749] < 0,
                runs=[dict(settings=r["settings"], usage=r.get("usage_summary")) for r in (a, b)])
