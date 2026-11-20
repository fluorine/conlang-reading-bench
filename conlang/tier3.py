"""Six-person transfer stories with deterministic clues and answer verification."""
from random import Random
from itertools import permutations, product

from .language import ROLES, language

PEOPLE = ("Ada", "Bo", "Cy", "Dee", "Eli", "Fay")
OBJECTS = ("coin", "key")


def make(seed, language_seed, length):
    rng = Random(seed)
    names = rng.sample(PEOPLE, len(PEOPLE))
    initial = dict(zip(OBJECTS, names))
    if rng.randrange(2):
        initial = dict(reversed(list(initial.items())))
    state = initial.copy()
    events = []
    first = rng.choice(OBJECTS)
    for i in range(length):
        obj = first if i % 2 == 0 else next(x for x in OBJECTS if x != first)
        giver = state[obj]
        recipient = rng.choice([x for x in PEOPLE if x != giver])
        events.append((obj, giver, recipient))
        state[obj] = recipient
    query_object = events[-2][0]
    anchor = events[-1][0]
    query = [events[0][2], events[-2][2], state["coin"], state["key"]]
    questions = ["Who received an object in transfer 1?",
                 f"Who held the {query_object} immediately before the final transfer of the {anchor}?",
                 "Who holds the coin at the end?", "Who holds the key at the end?"]
    roots, gs, rs, order = language(language_seed)
    initial_lines = [f"{p} {roots['holds']} {roots[o]}" for o,p in initial.items()]
    sentences = []
    for obj,giver,recipient in events:
        parts = dict(giver=giver+"-"+gs, recipient=recipient+"-"+rs,
                     object=roots[obj], verb=roots["gives"])
        sentences.append(" ".join(parts[role] for role in order))
    return initial, events, query, questions, (roots, gs, rs, order), initial_lines + sentences


def verify(initial, lines, lang, gold):
    roots, gs, rs, order = lang
    vocab = {roots["coin"]: "coin", roots["key"]: "key"}
    possible = set()
    for roles, suffixes in product(permutations(ROLES), permutations((gs, rs))):
        state = initial.copy()
        events = []
        for line in lines[2:]:
            part = dict(zip(roles, line.split()))
            if (part["verb"] != roots["gives"] or part["object"] not in vocab
                    or not part["giver"].endswith("-"+suffixes[0])
                    or not part["recipient"].endswith("-"+suffixes[1])):
                break
            obj = vocab[part["object"]]
            giver, recipient = part["giver"].split("-")[0], part["recipient"].split("-")[0]
            if giver not in PEOPLE or recipient not in PEOPLE or state[obj] != giver or giver == recipient:
                break
            state[obj] = recipient
            events.append((obj, giver, recipient))
        else:
            possible.add((events[0][2], events[-2][2], state["coin"], state["key"]))
    return possible == {tuple(gold)}
