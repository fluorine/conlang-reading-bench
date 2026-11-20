"""Single-question probe with case markers selected by prior possession."""
from itertools import permutations
from random import Random
from .language import SUFFIXES
from .tier3 import make, PEOPLE, OBJECTS


def build(world_seed, language_seed, length=12, english=False):
    initial, events, gold, _, lang, initial_lines = make(world_seed, language_seed, length)
    roots = lang[0]
    rng = Random(language_seed ^ 0xF468)
    markers = rng.sample(SUFFIXES, 6)
    cases = {"giver": markers[0:2], "recipient": markers[2:4], "other": markers[4:6]}
    state = initial.copy()
    encoded = []
    for index, (obj, giver, recipient) in enumerate(events):
        other = next(value for value in OBJECTS if value != obj)
        context = "giver" if state[other] == giver else "recipient" if state[other] == recipient else "other"
        gm, rm = cases[context]
        if index % 2:
            gm, rm = rm, gm
        names = [giver + "-" + gm, recipient + "-" + rm]
        rng.shuffle(names)
        encoded.append(" ".join(names + [roots[obj], roots["gives"]]))
        state[obj] = recipient

    possible = {tuple(initial[obj] for obj in OBJECTS)}
    for index, line in enumerate(encoded):
        first, second, object_word, verb = line.split()
        obj = next(obj for obj in OBJECTS if roots[obj] == object_word)
        other = next(value for value in OBJECTS if value != obj)
        next_states = set()
        for values in possible:
            prior = dict(zip(OBJECTS, values))
            for giver_word, receiver_word in permutations((first, second)):
                giver, gm = giver_word.split("-")
                receiver, rm = receiver_word.split("-")
                context = "giver" if prior[other] == giver else "recipient" if prior[other] == receiver else "other"
                expected = cases[context]
                if index % 2:
                    expected = list(reversed(expected))
                if (verb == roots["gives"] and giver in PEOPLE and receiver in PEOPLE
                        and giver != receiver and prior[obj] == giver and [gm, rm] == expected):
                    updated = prior.copy()
                    updated[obj] = receiver
                    next_states.add(tuple(updated[value] for value in OBJECTS))
        possible = next_states
    answers = {dict(zip(OBJECTS, values))["coin"] for values in possible}
    if answers != {gold[2]}:
        raise ValueError("case grammar does not determine the answer")

    instruction = ("Answer the question. The answer is Ada, Bo, Cy, Dee, Eli, or Fay. "
                   "Return only a JSON array containing the one name.")
    question = "Who holds the coin at the end?"
    if english:
        lines = [f"{person} starts with the {obj}." for obj, person in initial.items()]
        lines += [f"{giver} gives the {obj} to {recipient}." for obj, giver, recipient in events]
        return "\n\n".join([instruction, "Story:\n" + "\n".join(lines), question]), gold[2]
    clue = (f"Word meanings: {roots['holds']} = initially holds, {roots['coin']} = coin, "
            f"{roots['key']} = key, {roots['gives']} = gives. Initial statements are holder, "
            "holds, object. Transfers contain two marked names in either order, followed by "
            "object and verb. Only the current holder gives. Pick the suffix pair according to "
            "who holds the OTHER object immediately before the transfer: "
            f"if giver, giver -{cases['giver'][0]}, recipient -{cases['giver'][1]}; "
            f"if recipient, giver -{cases['recipient'][0]}, recipient -{cases['recipient'][1]}; "
            f"if someone else, giver -{cases['other'][0]}, recipient -{cases['other'][1]}. "
            "On even-numbered transfers swap the giver and recipient suffixes of the selected pair. "
            "Transfers are chronological.")
    return "\n\n".join([instruction, clue, "Story:\n" + "\n".join(initial_lines[:2] + encoded),
                           question]), gold[2]
