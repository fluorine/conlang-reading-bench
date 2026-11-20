"""Case forms jointly identify role, object, and a prior-state relation."""
from itertools import permutations, product
from random import Random
from .tier3 import make, PEOPLE, OBJECTS

CONTEXTS = ("giver", "recipient", "other")


def build(world_seed, language_seed, length=12, english=False):
    initial, events, gold, _, lang, initial_lines = make(world_seed, language_seed, length)
    roots = lang[0]
    rng = Random(language_seed ^ 0x4A719)
    forms = [a + b for a in "ptkmns" for b in "aeiou"]
    rng.shuffle(forms)
    meanings = list(product(OBJECTS, CONTEXTS, ("giver", "recipient")))
    markers = dict(zip(meanings, forms))
    state = initial.copy()
    encoded = []
    for obj, giver, recipient in events:
        other = next(value for value in OBJECTS if value != obj)
        context = "giver" if state[other] == giver else "recipient" if state[other] == recipient else "other"
        words = [giver + "-" + markers[obj, context, "giver"],
                 recipient + "-" + markers[obj, context, "recipient"]]
        rng.shuffle(words)
        encoded.append(" ".join(words))
        state[obj] = recipient

    possible = {tuple(initial[obj] for obj in OBJECTS)}
    for line in encoded:
        first, second = line.split()
        next_states = set()
        for values in possible:
            prior = dict(zip(OBJECTS, values))
            for obj, (giver_word, receiver_word) in product(OBJECTS, permutations((first, second))):
                giver, gm = giver_word.split("-")
                receiver, rm = receiver_word.split("-")
                other = next(value for value in OBJECTS if value != obj)
                context = "giver" if prior[other] == giver else "recipient" if prior[other] == receiver else "other"
                if (giver in PEOPLE and receiver in PEOPLE and giver != receiver and prior[obj] == giver
                        and gm == markers[obj, context, "giver"] and rm == markers[obj, context, "recipient"]):
                    updated = prior.copy()
                    updated[obj] = receiver
                    next_states.add(tuple(updated[value] for value in OBJECTS))
        possible = next_states
    if {dict(zip(OBJECTS, values))["coin"] for values in possible} != {gold[2]}:
        raise ValueError("fused case grammar does not determine the answer")

    instruction = ("Answer the question. The answer is Ada, Bo, Cy, Dee, Eli, or Fay. "
                   "Return only a JSON array containing the one name.")
    question = "Who holds the coin at the end?"
    if english:
        lines = [f"{person} starts with the {obj}." for obj, person in initial.items()]
        lines += [f"{giver} gives the {obj} to {recipient}." for obj, giver, recipient in events]
        return "\n\n".join([instruction, "Story:\n" + "\n".join(lines), question]), gold[2]
    entries = [f"{obj}, other object held by {context}: giver -{markers[obj, context, 'giver']}, "
               f"recipient -{markers[obj, context, 'recipient']}"
               for obj in OBJECTS for context in CONTEXTS]
    rng.shuffle(entries)
    clue = (f"Initial words: {roots['holds']} = initially holds, {roots['coin']} = coin, "
            f"{roots['key']} = key. Initial statements are holder, holds, object. Each subsequent "
            "line is a transfer. Its two marked names appear in either order. Each suffix jointly "
            "indicates the transferred object, the person's role, and who holds the OTHER object "
            "immediately before the transfer. 'Other' means neither giver nor recipient. Use the "
            "following table. Only the current holder gives. Transfers are chronological.\n"
            + "\n".join(entries))
    return "\n\n".join([instruction, clue, "Story:\n" + "\n".join(initial_lines[:2] + encoded),
                           question]), gold[2]
