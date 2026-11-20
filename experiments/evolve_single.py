"""Reproducible single-story search for sound-rule sequences that challenge Luna."""
import json
import os
import random
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from conlang.runner import bound, price, settings
from conlang.scoring import parse
from conlang.single_probe import build
from conlang.suite import write

DIRECTORY = Path(".work/evolution")
MODEL = settings("gpt-6-luna", "medium", 8192, [0.1, 0.5])
BUDGET = 0.15


def evaluate(candidate, path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    rules = candidate["rules"]
    prompt, gold = build(len(rules), divisors=rules)
    body = {"model": MODEL["model"], "reasoning_effort": "medium",
            "max_completion_tokens": MODEL["max_completion_tokens"],
            "messages": [{"role": "user", "content": prompt}]}
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"],
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=150) as response:
        result = json.load(response)
    raw = result["choices"][0]["message"].get("content") or ""
    usage = result["usage"]
    record = {**candidate, "prompt": prompt, "gold": gold, "raw": raw,
              "correct": parse(raw) == [gold.casefold()], "model": result["model"],
              "usage": usage, "cost": price(MODEL, usage["prompt_tokens"], usage["completion_tokens"])}
    write(path, record)
    return record


def main():
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    rng = random.Random(138270)
    parent = [2 + i % 11 for i in range(24)]
    for generation in range(2):
        candidates = []
        for candidate_id in range(6):
            rules = parent.copy()
            for _ in range(4):
                rules[rng.randrange(len(rules))] = rng.randrange(2, 13)
            candidates.append(dict(generation=generation, candidate=candidate_id, rules=rules))
        manifest = DIRECTORY / f"generation-{generation}.json"
        if manifest.exists():
            if json.loads(manifest.read_text(encoding="utf-8")) != candidates:
                raise ValueError("search state does not match seeded candidates")
        else:
            write(manifest, candidates)
        paths = [DIRECTORY / f"g{generation}-{c['candidate']}.json" for c in candidates]
        spent = sum(json.loads(p.read_text(encoding="utf-8"))["cost"]
                    for p in DIRECTORY.glob("g[0-9]-[0-9].json"))
        remaining = sum(bound(MODEL, build(24, divisors=c["rules"])[0])
                        for c, p in zip(candidates, paths) if not p.exists())
        if spent + remaining > BUDGET:
            raise ValueError("remaining worst-case estimate exceeds search budget")
        with ThreadPoolExecutor(max_workers=3) as pool:
            records = list(pool.map(evaluate, candidates, paths))
        # Prefer a completed wrong answer; otherwise retain the largest reasoning budget.
        parent_record = max(records, key=lambda row: (
            bool(row["raw"]) and not row["correct"], row["usage"]["completion_tokens"]))
        parent = parent_record["rules"]
        print(f"Generation {generation}: {sum(not r['correct'] for r in records)} failures, "
              f"selected candidate {parent_record['candidate']}", flush=True)


if __name__ == "__main__":
    main()
