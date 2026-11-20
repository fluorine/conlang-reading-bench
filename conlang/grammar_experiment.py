"""Matched grammar variants for the Tier 3 development experiment."""
from random import Random
from itertools import product
from .tier3 import PEOPLE, OBJECTS

VARIANTS = ("fused", "sound", "irregular", "combined")


def render(seed, initial, events, initial_lines, gold, variant):
    rng = Random(seed ^ 0x5F123)
    suffixes = rng.sample(("ak", "em", "ir", "os", "ul", "av", "en", "iz"), 8)
    meanings = list(product(OBJECTS, ("giver", "recipient")))
    regular = dict(zip(meanings, suffixes[:4]))
    irregular = dict(zip(meanings, suffixes[4:]))
    use_irregular = variant in ("irregular", "combined")
    use_sound = variant in ("sound", "combined")
    examples = []
    for obj, role in meanings:
        for name in (("Ada", "Fay") if use_irregular else ("Ada",)):
            suffix = (irregular if name == "Fay" and use_irregular else regular)[obj, role]
            verb = "gives" if role == "giver" else "receives"
            examples.append(f"{name}-{suffix} = {name} {verb} the {obj}")

    lines = list(initial_lines[:2])
    for index, (obj, giver, recipient) in enumerate(events):
        pieces = []
        for name, role in ((giver, "giver"), (recipient, "recipient")):
            suffix = (irregular if name == "Fay" and use_irregular else regular)[obj, role]
            if use_sound and index % 2:
                suffix = suffix.translate(str.maketrans("aeiou", "eioua"))
            pieces.append(name + "-" + suffix)
        lines.append(" ".join(pieces))
    clue = ("Transfer sentences contain a giver followed by a recipient. Each ending combines "
            "the person's role and object. Only the current holder can give. Examples show all "
            "base endings. All names use Ada's pattern"
            + (" except Fay, whose endings are shown separately." if use_irregular else "."))
    if use_sound:
        clue += (" On even-numbered transfers, change every vowel in an ending once using "
                 "a→e, e→i, i→o, o→u, u→a. Odd-numbered transfers use the base endings.")
    clue += "\nExamples:\n" + "\n".join(examples)

    # Decode the observed forms using only the provided examples and sound rule.
    lookup = {}
    for example in examples:
        marked, meaning = example.split(" = ")
        name, verb, _, obj = meaning.split()
        suffix = marked.split("-")[1]
        lookup[("Fay" if use_irregular and name == "Fay" else "regular", suffix)] = (
            "giver" if verb == "gives" else "recipient", obj)
    state = initial.copy()
    decoded_events = []
    for index, line in enumerate(lines[2:]):
        parsed = []
        for token in line.split():
            name, suffix = token.split("-")
            if use_sound and index % 2:
                suffix = suffix.translate(str.maketrans("eioua", "aeiou"))
            key = ("Fay" if use_irregular and name == "Fay" else "regular", suffix)
            if name not in PEOPLE or key not in lookup:
                raise ValueError("unrecognized form")
            parsed.append((name, *lookup[key]))
        (giver, role_a, obj), (recipient, role_b, other) = parsed
        if role_a != "giver" or role_b != "recipient" or obj != other or state[obj] != giver:
            raise ValueError("invalid decoded event")
        state[obj] = recipient
        decoded_events.append((obj, giver, recipient))
    decoded_gold = [decoded_events[0][2], decoded_events[-2][2], state["coin"], state["key"]]
    if decoded_gold != gold:
        raise ValueError("decoded answers disagree")
    return lines, clue
