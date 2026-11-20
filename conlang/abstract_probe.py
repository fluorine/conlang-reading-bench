"""A single-question probe whose case marking depends on the previous world state."""
from random import Random
from .tier3 import make, PEOPLE, OBJECTS


def build(world_seed, language_seed, length=12, english=False):
    initial, events, gold, _, lang, initial_lines = make(world_seed, language_seed, length)
    roots, giver_suffix, recipient_suffix, _ = lang
    rng = Random(language_seed ^ 0x7913)
    state = initial.copy()
    encoded = []
    for obj, giver, recipient in events:
        other = next(value for value in OBJECTS if value != obj)
        swap = state[other] == recipient
        giver_marker = recipient_suffix if swap else giver_suffix
        recipient_marker = giver_suffix if swap else recipient_suffix
        words = [f"{giver}-{giver_marker}", f"{recipient}-{recipient_marker}"]
        rng.shuffle(words)
        encoded.append(" ".join(words + [roots[obj], roots["gives"]]))
        state[obj] = recipient

    # Explore every interpretation allowed by the supplied markers and state rule.
    possible = {tuple(initial[obj] for obj in OBJECTS)}
    for line in encoded:
        first, second, object_word, verb = line.split()
        obj = next(obj for obj in OBJECTS if roots[obj] == object_word)
        other = next(value for value in OBJECTS if value != obj)
        next_states = set()
        for values in possible:
            prior = dict(zip(OBJECTS, values))
            for giver_word, receiver_word in ((first, second), (second, first)):
                giver, gm = giver_word.split("-")
                receiver, rm = receiver_word.split("-")
                swap = prior[other] == receiver
                if (verb == roots["gives"] and giver in PEOPLE and receiver in PEOPLE
                        and giver != receiver and prior[obj] == giver
                        and gm == (recipient_suffix if swap else giver_suffix)
                        and rm == (giver_suffix if swap else recipient_suffix)):
                    updated = prior.copy()
                    updated[obj] = receiver
                    next_states.add(tuple(updated[value] for value in OBJECTS))
        possible = next_states
    answers = {dict(zip(OBJECTS, values))["coin"] for values in possible}
    if answers != {gold[2]}:
        raise ValueError("abstract grammar does not determine the answer")

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
            "object and verb. Only the current holder gives an object. Normally "
            f"-{giver_suffix} marks the giver and -{recipient_suffix} marks the recipient. "
            "If the recipient holds the other object immediately before the transfer, "
            "the two markers exchange meanings for that transfer. Transfers are chronological.")
    story = initial_lines[:2] + encoded
    return "\n\n".join([instruction, clue, "Story:\n" + "\n".join(story), question]), gold[2]
