"""Infer unlisted fused case endings while certifying a unique final answer."""
import re
from itertools import permutations, product
from random import Random

from .fused_case_probe import build as full_case
from .tier3 import OBJECTS

ENTRY = re.compile(r"^(coin|key), other object held by (giver|recipient|other): giver -(\w+), recipient -(\w+)$")


def build(world_seed, language_seed, examples=3, english=False, length=12):
    if english:
        return full_case(world_seed, language_seed, length=length, english=True)
    prompt, gold = full_case(world_seed, language_seed, length=length)
    instruction, clue, story, question = prompt.split("\n\n")
    clue_lines = clue.splitlines()
    entries = clue_lines[1:]
    rng = Random(language_seed ^ 0xA05)
    shown = rng.sample(entries, examples)
    known = {}
    for line in shown:
        match = ENTRY.fullmatch(line)
        if not match:
            raise ValueError("invalid example")
        obj, context, giver, recipient = match.groups()
        known[giver] = (obj, context, "giver")
        known[recipient] = (obj, context, "recipient")
    initial_lines = story.splitlines()[1:3]
    words = re.findall(r"(\w+) = (initially holds|coin|key)", clue_lines[0])
    roots = {meaning: word for word, meaning in words}
    initial = {}
    for line in initial_lines:
        name, _, object_word = line.split()
        obj = next(key for key in OBJECTS if roots[key] == object_word)
        initial[obj] = name

    # Each suffix has one meaning and all 12 possible meanings have distinct suffixes.
    outcomes = set()
    visited = 0
    encoded = story.splitlines()[3:]

    def search(index, state, mapping):
        nonlocal visited
        visited += 1
        if visited > 100000:
            raise ValueError("search limit exceeded")
        if index == len(encoded):
            outcomes.add(state["coin"])
            return
        if len(outcomes) > 1:
            return
        first, second = encoded[index].split()
        for obj, (giver_word, recipient_word) in product(OBJECTS, permutations((first, second))):
            giver, gm = giver_word.split("-")
            recipient, rm = recipient_word.split("-")
            if giver == recipient or state[obj] != giver:
                continue
            other = next(value for value in OBJECTS if value != obj)
            context = "giver" if state[other] == giver else "recipient" if state[other] == recipient else "other"
            required = ((gm, (obj, context, "giver")), (rm, (obj, context, "recipient")))
            updated_mapping = mapping.copy()
            for marker, meaning in required:
                if (marker in updated_mapping and updated_mapping[marker] != meaning
                        or marker not in updated_mapping and meaning in updated_mapping.values()):
                    break
                updated_mapping[marker] = meaning
            else:
                updated_state = state.copy()
                updated_state[obj] = recipient
                search(index + 1, updated_state, updated_mapping)
    search(0, initial, known)
    if outcomes != {gold}:
        raise ValueError("insufficient clues for a unique answer")
    hint = ("The following table shows only some suffixes; infer the rest from the story."
            if shown else "No suffix meanings are supplied; infer them from the story.")
    overview = clue_lines[0].replace("Use the following table.", (
        "Each of the twelve possible object, context, and role combinations has a different suffix. "
        + hint))
    return "\n\n".join((instruction, overview + "\n" + "\n".join(shown), story, question)), gold
