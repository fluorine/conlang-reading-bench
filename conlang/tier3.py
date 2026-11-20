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


def alternating_lines(events, lang, initial_lines):
    """Render alternating role order and suffix meanings under explicit rules."""
    roots, gs, rs, order = lang
    lines = list(initial_lines[:2])
    for index, (obj, giver, recipient) in enumerate(events):
        odd = index % 2 == 0
        roles = order if odd else list(reversed(order))
        parts = dict(giver=giver + "-" + (gs if odd else rs),
                     recipient=recipient + "-" + (rs if odd else gs),
                     object=roots[obj], verb=roots["gives"])
        lines.append(" ".join(parts[role] for role in roles))
    return lines


def verify_alternating(initial, lines, lang, gold):
    roots, gs, rs, order = lang
    objects = {roots[obj]: obj for obj in OBJECTS}
    state = initial.copy()
    events = []
    for index, line in enumerate(lines[2:]):
        odd = index % 2 == 0
        roles = order if odd else list(reversed(order))
        parts = dict(zip(roles, line.split()))
        giver_suffix, recipient_suffix = (gs, rs) if odd else (rs, gs)
        if (parts["verb"] != roots["gives"] or parts["object"] not in objects
                or not parts["giver"].endswith("-" + giver_suffix)
                or not parts["recipient"].endswith("-" + recipient_suffix)):
            return False
        obj = objects[parts["object"]]
        giver = parts["giver"].split("-")[0]
        recipient = parts["recipient"].split("-")[0]
        if giver not in PEOPLE or recipient not in PEOPLE or state[obj] != giver or giver == recipient:
            return False
        state[obj] = recipient
        events.append((obj, giver, recipient))
    return [events[0][2], events[-2][2], state["coin"], state["key"]] == gold


def fusional(seed, events, initial_lines):
    """Encode role and object together; Fay has separately evidenced irregular forms."""
    rng = Random(seed ^ 0x5F123)
    syllables = ("ak", "em", "ir", "os", "ul", "av", "en", "iz")
    suffixes = rng.sample(syllables, 8)
    meanings = [(role, obj) for obj in OBJECTS for role in ("giver", "recipient")]
    regular = dict(zip(meanings, suffixes[:4]))
    irregular = dict(zip(meanings, suffixes[4:]))
    lines = list(initial_lines[:2])
    for obj, giver, recipient in events:
        first = irregular if giver == "Fay" else regular
        second = irregular if recipient == "Fay" else regular
        lines.append(f"{giver}-{first[('giver', obj)]} {recipient}-{second[('recipient', obj)]}")
    examples = []
    for obj in OBJECTS:
        for giver, recipient in (("Ada", "Bo"), ("Fay", "Cy"), ("Cy", "Fay")):
            a = irregular if giver == "Fay" else regular
            b = irregular if recipient == "Fay" else regular
            examples.append(f"{giver}-{a[('giver', obj)]} {recipient}-{b[('recipient', obj)]}"
                            f" = {giver} gives the {obj} to {recipient}")
    return lines, examples


def verify_fusional(initial, lines, examples, gold):
    """Derive marker meanings from visible examples and replay every event."""
    marker_meanings = {}
    for example in examples:
        encoded, meaning = example.split(" = ")
        words = meaning.split()
        giver, recipient = encoded.split()
        for marked, role in ((giver, "giver"), (recipient, "recipient")):
            name, suffix = marked.split("-")
            key = ("Fay" if name == "Fay" else "regular", suffix)
            value = (role, words[3])
            if key in marker_meanings and marker_meanings[key] != value:
                return False
            marker_meanings[key] = value
    state = initial.copy()
    events = []
    for line in lines[2:]:
        interpretations = []
        for marked in line.split():
            name, suffix = marked.split("-")
            key = ("Fay" if name == "Fay" else "regular", suffix)
            if name not in PEOPLE or key not in marker_meanings:
                return False
            interpretations.append((name, *marker_meanings[key]))
        if len(interpretations) != 2:
            return False
        (giver, role_a, obj), (recipient, role_b, obj_b) = interpretations
        if role_a != "giver" or role_b != "recipient" or obj != obj_b or state[obj] != giver or giver == recipient:
            return False
        state[obj] = recipient
        events.append((obj, giver, recipient))
    return [events[0][2], events[-2][2], state["coin"], state["key"]] == gold


def irregular_forms(seed, events, initial_lines):
    """Every name has four independently sampled object-and-role endings."""
    rng = Random(seed ^ 0xAC938)
    syllables = [a + b for a in "ptkmns" for b in "aeiou"]
    endings = {}
    examples = []
    for name in PEOPLE:
        markers = rng.sample(syllables, 4)
        for (role, obj), marker in zip(product(("giver", "recipient"), OBJECTS), markers):
            endings[name, role, obj] = marker
            if role == "giver":
                examples.append(f"{name}-{marker} = {name} gives the {obj}")
            else:
                examples.append(f"{name}-{marker} = {name} receives the {obj}")
    rng.shuffle(examples)
    lines = list(initial_lines[:2])
    for obj, giver, recipient in events:
        lines.append(f"{giver}-{endings[giver, 'giver', obj]} "
                     f"{recipient}-{endings[recipient, 'recipient', obj]}")
    return lines, examples


def verify_irregular(initial, lines, examples, gold):
    forms = {}
    for example in examples:
        form, meaning = example.split(" = ")
        name, verb, _, obj = meaning.split()
        key = name, form.split("-")[1]
        value = ("giver" if verb == "gives" else "recipient", obj)
        if key in forms and forms[key] != value:
            return False
        forms[key] = value
    state = initial.copy()
    events = []
    for line in lines[2:]:
        decoded = []
        for word in line.split():
            name, suffix = word.split("-")
            if name not in PEOPLE or (name, suffix) not in forms:
                return False
            decoded.append((name, *forms[name, suffix]))
        if len(decoded) != 2:
            return False
        (giver, a, obj), (recipient, b, other) = decoded
        if a != "giver" or b != "recipient" or obj != other or state[obj] != giver or giver == recipient:
            return False
        state[obj] = recipient
        events.append((obj, giver, recipient))
    return [events[0][2], events[-2][2], state["coin"], state["key"]] == gold
