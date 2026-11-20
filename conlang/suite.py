"""Manifests name every world and grammar seed; hashing is platform independent."""
import hashlib
import json
import os
import tempfile
from pathlib import Path
from collections import Counter
from random import Random

from . import VERSION
from .language import evidence, interpretations, language, render
from .world import answers, english, make_world, questions, simulate

TIERS = ("minimal", "glossary", "grammar")
CONDITIONS = (*TIERS, "english")
ROOT = Path(__file__).resolve().parent.parent


def digest(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(data.encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")
    os.replace(f.name, path)


def build(manifest):
    if manifest["version"] != VERSION or manifest["length"] not in (2, 3):
        raise ValueError("unsupported protocol or transfer count")
    prompts, keys, rejected = {}, {}, []
    for index, (world, lex) in enumerate(manifest["pairs"]):
        story = f"w{world}-l{lex}"
        initial, events = make_world(world, manifest["length"], index % 3)
        query, qs = questions(world + 1729)
        lang = language(lex)
        lines = render(lang, initial, events)
        roots = lang[0]
        example = f"Ivy {roots['holds']} {roots['coin']}"
        gold = answers(initial, events, query)
        candidates = interpretations(lines, example, roots["gives"], query)
        if candidates != {gold}:
            rejected.append(dict(world=world, language=lex, reason="ambiguous or disagrees with simulator"))
            continue
        if story in keys:
            raise ValueError("duplicate seed pair")
        keys[story] = dict(answers=gold, initial=initial, events=events, history=simulate(initial, events))
        clues = evidence(lang)
        for condition in manifest["conditions"]:
            instructions = ["Answer four reading questions. Each answer is Ada, Bo, or Cy. "
                            "Return only a JSON array of four names in question order."]
            if condition in TIERS:
                instructions += clues[:TIERS.index(condition) + 1] + ["Story:\n" + "\n".join(lines)]
            elif condition == "english":
                instructions += ["Story:\n" + "\n".join(english(initial, events))]
            elif condition != "questions":
                raise ValueError("unknown condition")
            prompt = "\n\n".join(instructions + ["\n".join(f"{i}. {q}" for i, q in enumerate(qs, 1))])
            prompts[f"{story}/{condition}"] = prompt
    return prompts, keys, rejected


def certified(manifest):
    prompts, keys, rejected = build(manifest)
    if rejected or not keys:
        raise ValueError(f"suite admission failed: {rejected}")
    return prompts, keys


def load_suite(name):
    return read(ROOT / "suites" / (name + ".json"))


def sample_manifest(name, seed, count, length):
    """Balance person-name frequencies per question across both candidate forms."""
    if count < 1 or length not in (2, 3) or not name.isalnum():
        raise ValueError("use a positive story count, alphanumeric name and 2 or 3 transfers")
    rng = Random(seed)
    counts = Counter()
    used = set()
    pairs = []
    for index in range(count):
        def answer_cells(world):
            query, _ = questions(world + 1729)
            return [(size, slot, person) for size in (2, 3)
                    for slot, person in enumerate(answers(*make_world(world, size, index % 3), query))]

        candidates = [rng.randrange(2**31) for _ in range(600)]
        selected = min((w for w in candidates if w not in used),
                       key=lambda w: sum(counts[cell] for cell in answer_cells(w)))
        counts.update(answer_cells(selected))
        used.add(selected)
        pairs.append([selected, rng.randrange(2**31)])
    return dict(name=name, version=VERSION, length=length, pairs=pairs, conditions=list(CONDITIONS))
