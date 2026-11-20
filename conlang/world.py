"""Ownership simulator. A transfer records (object, giver, recipient)."""
from random import Random

PEOPLE = ("Ada", "Bo", "Cy")
OBJECTS = ("coin", "key")


def simulate(initial, events):
    if set(initial) != set(OBJECTS) or any(p not in PEOPLE for p in initial.values()):
        raise ValueError("invalid initial ownership")
    history = [dict(initial)]
    for obj, giver, recipient in events:
        state = history[-1].copy()
        if state.get(obj) != giver or giver == recipient or recipient not in PEOPLE:
            raise ValueError("illegal transfer")
        state[obj] = recipient
        history.append(state)
    return history


def make_world(seed, length, rotation):
    rng = Random(seed)
    names = list(PEOPLE)
    rng.shuffle(names)
    names = [PEOPLE[(PEOPLE.index(p) + rotation) % 3] for p in names]
    initial = dict(zip(OBJECTS, names))
    state = initial.copy()
    events = []
    for _ in range(length):
        obj = rng.choice(OBJECTS)
        giver = state[obj]
        recipient = rng.choice([p for p in names if p != giver])
        events.append((obj, giver, recipient))
        state[obj] = recipient
    return initial, events


def questions(seed):
    rng = Random(seed)
    direct = rng.randrange(2)
    past = rng.choice(OBJECTS)
    first, second = rng.sample(OBJECTS, 2)
    return (direct, past, first, second), [
        f"Who received an object in transfer {direct + 1}?",
        f"Who held the {past} immediately before transfer 2?",
        f"Who holds the {first} at the end?",
        f"Who holds the {second} at the end?",
    ]


def answers(initial, events, query):
    direct, past, first, second = query
    states = simulate(initial, events)
    return (events[direct][2], states[1][past], states[-1][first], states[-1][second])


def english(initial, events):
    return [f"{person} starts with the {obj}." for obj, person in initial.items()] + [
        f"{giver} gives the {obj} to {recipient}." for obj, giver, recipient in events
    ]
