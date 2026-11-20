"""Induce unique fused markers for three objects from a short transfer story."""
from itertools import permutations, product
from random import Random

PEOPLE = ("Ada", "Bo", "Cy", "Dee", "Eli", "Fay")
OBJECTS = ("coin", "key", "book")
CONTEXTS = ("giver", "recipient", "other")


def build(world_seed, language_seed, length=18, english=False, objects=OBJECTS):
    world = Random(world_seed)
    initial = dict(zip(objects, world.sample(PEOPLE, len(objects))))
    state = initial.copy()
    events = []
    for _ in range(length):
        obj = world.choice(objects)
        giver = state[obj]
        recipient = world.choice([name for name in PEOPLE if name != giver])
        events.append((obj, giver, recipient))
        state[obj] = recipient
    gold = state["coin"]
    rng = Random(language_seed)
    suffixes = rng.sample([a + b for a in "ptkmns" for b in "aeiou"], len(objects) * 6)
    meanings = list(product(objects, CONTEXTS, ("giver", "recipient")))
    markers = dict(zip(meanings, suffixes))
    roots = dict(zip((*objects, "holds"), rng.sample(
        [a + b for a in ("lu", "zo", "mi", "ve", "ka", "po") for b in ("ma", "to", "ki", "se")], len(objects) + 1)))
    state = initial.copy()
    encoded = []
    for obj, giver, recipient in events:
        # The special reference object is always the key, or the book when the key moves.
        reference = "book" if obj == "key" else "key"
        context = "giver" if state[reference] == giver else "recipient" if state[reference] == recipient else "other"
        words = [giver + "-" + markers[obj, context, "giver"],
                 recipient + "-" + markers[obj, context, "recipient"]]
        rng.shuffle(words)
        encoded.append(" ".join(words))
        state[obj] = recipient

    outcomes = set()
    visited = 0

    def search(index, state, mapping):
        nonlocal visited
        visited += 1
        if visited > 150000:
            raise ValueError("search limit exceeded")
        if len(outcomes) > 1:
            return
        if index == len(encoded):
            outcomes.add(state["coin"])
            return
        first, second = encoded[index].split()
        for obj, (giver_word, recipient_word) in product(objects, permutations((first, second))):
            giver, gm = giver_word.split("-")
            recipient, rm = recipient_word.split("-")
            if giver == recipient or state[obj] != giver:
                continue
            reference = "book" if obj == "key" else "key"
            context = "giver" if state[reference] == giver else "recipient" if state[reference] == recipient else "other"
            required = ((gm, (obj, context, "giver")), (rm, (obj, context, "recipient")))
            updated = mapping.copy()
            for marker, meaning in required:
                if (marker in updated and updated[marker] != meaning
                        or marker not in updated and meaning in updated.values()):
                    break
                updated[marker] = meaning
            else:
                next_state = state.copy()
                next_state[obj] = recipient
                search(index + 1, next_state, updated)
    search(0, initial, {})
    if outcomes != {gold}:
        raise ValueError("clues do not determine the answer")
    blind_states = {tuple(initial[obj] for obj in objects)}
    for line in encoded:
        first, second = [word.split("-")[0] for word in line.split()]
        next_states = set()
        for values in blind_states:
            prior = dict(zip(objects, values))
            for obj, (giver, receiver) in product(objects, permutations((first, second))):
                if prior[obj] == giver and giver != receiver:
                    updated = prior.copy()
                    updated[obj] = receiver
                    next_states.add(tuple(updated[value] for value in objects))
        blind_states = next_states
    if len({dict(zip(objects, values))["coin"] for values in blind_states}) < 2:
        raise ValueError("suffix-free shortcut determines the answer")

    instruction = ("Answer the question. The answer is Ada, Bo, Cy, Dee, Eli, or Fay. "
                   "Return only a JSON array containing the one name.")
    question = "Who holds the coin at the end?"
    if english:
        lines = [f"{person} starts with the {obj}." for obj, person in initial.items()]
        lines += [f"{giver} gives the {obj} to {recipient}." for obj, giver, recipient in events]
        return "\n\n".join([instruction, "Story:\n" + "\n".join(lines), question]), gold
    clue = (f"Initial words: {roots['holds']} = initially holds, {roots['coin']} = coin, "
            f"{roots['key']} = key, {roots['book']} = book"
            + (f", {roots['ring']} = ring" if "ring" in objects else "")
            + (f", {roots['cup']} = cup" if "cup" in objects else "")
            + ". Initial statements are holder, holds, object. "
            "Each later line is a transfer, with two marked names in either order. Each suffix "
            "uniquely indicates the object transferred, the person's role, and whether the "
            "reference object is held by the giver, recipient, or someone else immediately before "
            "the transfer. The reference is the key, except when the key moves it is the book. "
            f"Each of the {'eighteen' if len(objects) == 3 else str(len(objects) * 6)} object, context, and role combinations has a different suffix. "
            "Infer suffix meanings from the story. Only the current holder gives. Transfers are chronological.")
    initial_lines = [f"{person} {roots['holds']} {roots[obj]}" for obj, person in initial.items()]
    return "\n\n".join([instruction, clue, "Story:\n" + "\n".join(initial_lines + encoded),
                           question]), gold
