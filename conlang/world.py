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
    if length >= 4 and rng.randrange(2):
        initial = dict(reversed(list(initial.items())))
    state = initial.copy()
    events = []
    for step in range(length):
        obj = rng.choice(OBJECTS) if length < 4 or step == 0 else next(
            item for item in OBJECTS if item != events[-1][0]
        )
        giver = state[obj]
        recipient = rng.choice([p for p in names if p != giver])
        events.append((obj, giver, recipient))
        state[obj] = recipient
    return initial, events


def questions(seed, events=()):
    rng = Random(seed)
    direct = rng.randrange(2)
    past = rng.choice(OBJECTS)
    first, second = rng.sample(OBJECTS, 2)
    if len(events) == 4:
        past, anchor = events[2][0], events[3][0]
        return (direct, past, first, second), [
            f"Who received an object in transfer {direct + 1}?",
            f"Who held the {past} immediately before the {anchor} was given away for the second time?",
            f"Who holds the {first} at the end?",
            f"Who holds the {second} at the end?",
        ]
    if len(events) > 4:
        past, anchor = events[-2][0], events[-1][0]
        return (direct, past, first, second), [
            f"Who received an object in transfer {direct + 1}?",
            f"Who held the {past} immediately before the final transfer of the {anchor}?",
            f"Who holds the {first} at the end?",
            f"Who holds the {second} at the end?",
        ]
    return (direct, past, first, second), [
        f"Who received an object in transfer {direct + 1}?",
        f"Who held the {past} immediately before transfer 2?",
        f"Who holds the {first} at the end?",
        f"Who holds the {second} at the end?",
    ]


def answers(initial, events, query):
    direct, past, first, second = query
    states = simulate(initial, events)
    before_anchor = len(events) - 1 if len(events) >= 4 else 1
    return (events[direct][2], states[before_anchor][past], states[-1][first], states[-1][second])


def english(initial, events):
    return [f"{person} starts with the {obj}." for obj, person in initial.items()] + [
        f"{giver} gives the {obj} to {recipient}." for obj, giver, recipient in events
    ]
