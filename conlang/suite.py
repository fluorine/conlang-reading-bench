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
from . import tier3

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
    if manifest.get("family") in ("six_people", "alternating_grammar", "fusional", "irregular_forms", "opaque_names"):
        return build_six_people(manifest)
    if manifest["version"] != VERSION or manifest["length"] not in (2, 3, 4, 12, 24, 48):
        raise ValueError("unsupported protocol or transfer count")
    prompts, keys, rejected = {}, {}, []
    for index, (world, lex) in enumerate(manifest["pairs"]):
        story = f"w{world}-l{lex}"
        initial, events = make_world(world, manifest["length"], index % 3)
        query, qs = questions(world + 1729, events)
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


def build_six_people(manifest):
    if manifest["version"] != VERSION or manifest["length"] not in (12, 24, 48, 96):
        raise ValueError("unsupported six-person suite")
    prompts, keys, rejected = {}, {}, []
    for world, lex in manifest["pairs"]:
        story = f"w{world}-l{lex}"
        if story in keys:
            raise ValueError("duplicate seed pair")
        initial, events, gold, qs, lang, lines = tier3.make(world, lex, manifest["length"])
        if not tier3.verify(initial, lines, lang, gold):
            rejected.append(dict(world=world, language=lex, reason="ambiguous"))
            continue
        keys[story] = dict(answers=gold, initial=initial, events=events)
        roots = lang[0]
        clue = ("There are two objects (coin, key) and two predicates (holds initially, gives). "
                "Each has its own word. Initial statements use holder, predicate, object. "
                "Transfers use the same four positions in some order. Each name has a role suffix "
                "after a hyphen. Only the current holder may give an object. Events are chronological. "
                f"Key word: {roots['gives']} means gives. Separate example: "
                f"Ivy {roots['holds']} {roots['coin']} means Ivy starts with the coin.")
        if manifest.get("family") == "alternating_grammar":
            roots, gs, rs, order = lang
            lines = tier3.alternating_lines(events, lang, lines)
            if not tier3.verify_alternating(initial, lines, lang, gold):
                raise ValueError("alternating grammar failed independent decoding")
            clue = (f"Word meanings: {roots['coin']} = coin, {roots['key']} = key, "
                    f"{roots['holds']} = holds initially, {roots['gives']} = gives. "
                    "Initial statements use holder, predicate, object. "
                    f"For odd-numbered transfers, order is {', '.join(order)}, "
                    f"the giver has suffix -{gs} and the recipient has suffix -{rs}. "
                    "For even-numbered transfers, reverse that order and swap the two suffix meanings. "
                    "Only the current holder can give an object. Events are chronological.")
        if manifest.get("family") == "fusional":
            lines, examples = tier3.fusional(lex, events, lines)
            if not tier3.verify_fusional(initial, lines, examples, gold):
                raise ValueError("fusional grammar failed independent decoding")
            clue = (f"Initially: {roots['holds']} means holds, {roots['coin']} means coin, "
                    f"and {roots['key']} means key. Initial statements use holder, holds, object. "
                    "The following examples show the language's complete transfer pattern; Fay's "
                    "endings are irregular and all other names share the regular endings. "
                    "Names are unchanged. Transfers are chronological and "
                    "only the current holder gives an object.\nExamples:\n" + "\n".join(examples))
        if manifest.get("family") in ("irregular_forms", "opaque_names"):
            lines, examples = tier3.irregular_forms(lex, events, lines)
            if not tier3.verify_irregular(initial, lines, examples, gold):
                raise ValueError("irregular grammar failed independent decoding")
            clue = (f"Initially: {roots['holds']} means holds, {roots['coin']} means coin, "
                    f"and {roots['key']} means key. Initial statements use holder, holds, object. "
                    "In transfers each person has their own irregular endings, which identify "
                    "the role and object. Each transfer has two marked names in giver, recipient "
                    "order. Only the current holder can give. All endings are shown below.\n"
                    "Examples:\n" + "\n".join(examples))
            if manifest.get("family") == "opaque_names":
                import re
                from .language import WORDS
                rng = Random(lex ^ 0xA142)
                tokens = rng.sample([word for word in WORDS if word not in roots.values()], len(tier3.PEOPLE))
                mapping = dict(zip(tier3.PEOPLE, tokens))
                pattern = re.compile(r"\b(?:" + "|".join(tier3.PEOPLE) + r")\b")
                def encode(text):
                    return pattern.sub(lambda match: mapping[match.group()], text)
                lines = [encode(line) for line in lines]
                encoded_examples = []
                for example in examples:
                    form, meaning = example.split(" = ")
                    encoded_examples.append(encode(form) + " = " + meaning)
                dictionary = ", ".join(f"{word} = {name}" for name, word in mapping.items())
                clue = (f"Names: {dictionary}. Initially: {roots['holds']} means holds, "
                        f"{roots['coin']} means coin, and {roots['key']} means key. "
                        "Initial statements use holder, holds, object. In transfers, each person "
                        "has their own irregular endings identifying their role and the object. "
                        "Each transfer has two marked names in giver, recipient order. Only the "
                        "current holder can give. All endings are shown below.\nExamples:\n"
                        + "\n".join(encoded_examples))
        english_lines = [f"{p} starts with the {o}." for o, p in initial.items()] + [
            f"{g} gives the {o} to {r}." for o,g,r in events]
        for condition in manifest["conditions"]:
            if condition not in ("minimal", "english"):
                raise ValueError("unknown condition")
            sections = ["Answer four reading questions. Each answer is Ada, Bo, Cy, Dee, Eli, or Fay. "
                        "Return only a JSON array of four names in question order."]
            if condition == "minimal":
                sections += [clue, "Story:\n" + "\n".join(lines)]
            else:
                sections += ["Story:\n" + "\n".join(english_lines)]
            sections += ["\n".join(f"{i}. {q}" for i,q in enumerate(qs, 1))]
            prompts[f"{story}/{condition}"] = "\n\n".join(sections)
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
    if count < 1 or length not in (2, 3, 4, 12, 24, 48) or not name.isalnum():
        raise ValueError("use a positive story count, alphanumeric name and a supported transfer count")
    rng = Random(seed)
    counts = Counter()
    used = set()
    pairs = []
    for index in range(count):
        def answer_cells(world):
            cells = []
            for size in ((length,) if length >= 4 else (2, 3)):
                initial, events = make_world(world, size, index % 3)
                query, _ = questions(world + 1729, events)
                cells.extend((size, slot, person)
                             for slot, person in enumerate(answers(initial, events, query)))
            return cells

        candidates = [rng.randrange(2**31) for _ in range(600)]
        selected = min((w for w in candidates if w not in used),
                       key=lambda w: sum(counts[cell] for cell in answer_cells(w)))
        counts.update(answer_cells(selected))
        used.add(selected)
        pairs.append([selected, rng.randrange(2**31)])
    conditions = ("minimal", "english") if length >= 4 else CONDITIONS
    return dict(name=name, version=VERSION, length=length, pairs=pairs, conditions=list(conditions))
