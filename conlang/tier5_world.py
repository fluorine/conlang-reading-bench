"""Tier 5 event histories, narration, rendering, questions and ablated readers."""
from random import Random

from .tier5_grammar import FILLER_RATE, OBJECTS, PEOPLE, PRONOUN_RATE

MAX_SAME_ANSWER = 2


def _transfer(verb, agent, other):
    return (agent, other) if verb == "give" else (other, agent)


def make_lines(rng, lvl, lang):
    """Return (people, membership, initial, lines) or None if the draw is unusable.

    A line is a dict: verb, obj, agent, other, status (real/neg/irr), plup,
    particle meaning or None, and persons: [(person, role, is_pronoun)] in
    token order. Real lines in text order with each plup line swapped before
    its predecessor give the chronological history.
    """
    people = rng.sample(PEOPLE, lvl["people"])
    classes = lvl["classes"]
    membership = {}
    if classes:
        labels = list(range(classes)) + [rng.randrange(classes) for _ in people[classes:]]
        rng.shuffle(labels)
        membership = dict(zip(people, labels))
    holders = rng.sample(people, len(OBJECTS))
    initial = dict(zip(OBJECTS, holders))
    state = dict(initial)
    events = []
    for step in range(lvl["transfers"]):
        if events and rng.random() < 0.5:
            obj = events[-1]["obj"]
        else:
            obj = rng.choice(OBJECTS)
        giver = state[obj]
        recipient = rng.choice([p for p in people if p != giver])
        verb = rng.choice(("give", "take"))
        agent, other = (giver, recipient) if verb == "give" else (recipient, giver)
        events.append(dict(verb=verb, obj=obj, agent=agent, other=other))
        state[obj] = recipient
    pairs_needed = max(1, int(lvl["out_of_order"] * lvl["transfers"] / 2 + 0.5))
    candidates = [i for i in range(1, len(events)) if events[i]["obj"] == events[i - 1]["obj"]]
    rng.shuffle(candidates)
    chosen, used = [], set()
    for i in candidates:
        if len(chosen) == pairs_needed:
            break
        if i - 1 in used or i in used:
            continue
        chosen.append(i)
        used.update((i - 1, i))
    if len(chosen) < pairs_needed:
        return None
    text = []
    i = 0
    while i < len(events):
        if i + 1 in chosen:
            text.append(dict(events[i + 1], status="real", plup=False))
            text.append(dict(events[i], status="real", plup=True))
            i += 2
        else:
            text.append(dict(events[i], status="real", plup=False))
            i += 1
    # Distractors go only where the line below is not pluperfect.
    kinds = ["neg"] * lvl["distractors"]
    if "irrealis" in lvl["modules"]:
        kinds = ["neg" if k % 2 == 0 else "irr" for k in range(lvl["distractors"])]
    for kind in kinds:
        slots = [s for s in range(len(text) + 1) if s == len(text) or not text[s]["plup"]]
        slot = rng.choice(slots)
        state = dict(initial)
        for line in _chronological(text[:slot]):
            state[line["obj"]] = _transfer(line["verb"], line["agent"], line["other"])[1]
        obj = rng.choice(OBJECTS)
        giver = state[obj]
        recipient = rng.choice([p for p in people if p != giver])
        verb = rng.choice(("give", "take"))
        agent, other = (giver, recipient) if verb == "give" else (recipient, giver)
        text.insert(slot, dict(verb=verb, obj=obj, agent=agent, other=other,
                               status=kind, plup=False))
    for line in text:
        line["particle"] = (line["status"] if line["status"] != "real"
                            else "filler" if rng.random() < FILLER_RATE else None)
    _place_persons(rng, lvl, lang, text, membership)
    return people, membership, initial, text


def _chronological(lines):
    real = []
    for line in lines:
        if line["status"] != "real":
            continue
        if line["plup"]:
            real.insert(len(real) - 1, line)
        else:
            real.append(line)
    return real


def _place_persons(rng, lvl, lang, text, membership):
    """Fix token order and pronoun use for each line."""
    pronouns = "pronoun" in lvl["modules"]
    last = {}
    for line in text:
        if lvl["fixed_order"]:
            order = [r for r in lang["order"] if r in ("agent", "other")]
        else:
            order = rng.sample(("agent", "other"), 2)
        persons = []
        for role in order:
            person = line[role]
            label = membership.get(person)
            use = pronouns and last.get(label) == person and rng.random() < PRONOUN_RATE
            persons.append((person, role, use))
            if label is not None:
                last[label] = person
        line["persons"] = persons
        if not lvl["fixed_order"]:
            line["core"] = rng.sample(("person0", "person1", "object"), 3)


def render(lvl, lang, membership, initial, text):
    roots = lang["roots"]
    pronoun_of = {label: word for word, label in lang["pronouns"].items()}
    particle_of = {meaning: word for word, meaning in lang["particles"].items()}
    out = [f"{person} {roots[obj]} {roots['hold']}" for obj, person in initial.items()]
    for line in text:
        tokens = {}
        for index, (person, role, pronoun) in enumerate(line["persons"]):
            label = membership.get(person)
            stem = pronoun_of[label] if pronoun else person
            if lvl["declension"]:
                agent_suffix = lang["case"][label]
            else:
                agent_suffix = lang["case"]
            other_suffix = next(s for s in lang["suffixes"] if s != agent_suffix)
            tokens[f"person{index}"] = f"{stem}-{agent_suffix if role == 'agent' else other_suffix}"
            tokens[role] = tokens[f"person{index}"]
        tokens["object"] = roots[line["obj"]]
        tense = lang["tense"]["plup" if line["plup"] else "past"]
        verb = f"{roots[line['verb']]}-{tense}"
        if lang["agree_target"]:
            label = membership[line[lang["agree_target"]]]
            prefix = next(p for p, l in lang["prefixes"].items() if l == label)
            verb = f"{prefix}-{verb}"
        tokens["verb"] = verb
        if lvl["fixed_order"]:
            words = [tokens[role] for role in lang["order"]]
        else:
            words = [tokens[slot] for slot in line["core"]]
            words = [verb] + words if lang["verb_position"] == "first" else words + [verb]
        if line["particle"]:
            words.insert(0, particle_of[line["particle"]])
        out.append(" ".join(words))
    return out


def english(initial, text):
    out = [f"{person} starts with the {obj}." for obj, person in initial.items()]
    for line in text:
        a, o, b = line["agent"], line["obj"], line["other"]
        give = line["verb"] == "give"
        if line["status"] == "neg":
            out.append(f"{a} did not {'give' if give else 'take'} the {o} "
                       f"{'to' if give else 'from'} {b}.")
        elif line["status"] == "irr":
            out.append(f"It was only reported that {a} {'gave' if give else 'took'} the {o} "
                       f"{'to' if give else 'from'} {b}; it did not happen.")
        elif line["plup"]:
            out.append(f"Just before that, {a} had {'given' if give else 'taken'} the {o} "
                       f"{'to' if give else 'from'} {b}.")
        else:
            out.append(f"{a} {'gave' if give else 'took'} the {o} {'to' if give else 'from'} {b}.")
    return out


QUESTION_TEXT = {
    "final": "Who holds the {o} at the end?",
    "first_receiver": "Who was the first person to receive the {o}?",
    "last_giver": "Who had the {o} just before its final transfer?",
    "before_last": "Who held the {o} just before the final transfer of the {a}?",
    "after_first": "Who held the {o} just after the first transfer of the {a}?",
}


def candidate_questions():
    specs = []
    for kind in ("final", "first_receiver", "last_giver"):
        specs.extend((kind, o) for o in OBJECTS)
    for kind in ("before_last", "after_first"):
        specs.extend((kind, o, a) for o in OBJECTS for a in OBJECTS if a != o)
    return specs


def question_text(spec):
    return QUESTION_TEXT[spec[0]].format(o=spec[1], a=spec[2] if len(spec) > 2 else "")


def answer(initial, transfers, spec):
    """Answer one question from chronological (obj, giver, recipient) transfers."""
    kind, obj = spec[0], spec[1]
    states = [dict(initial)]
    for o, giver, recipient in transfers:
        state = dict(states[-1])
        state[o] = recipient
        states.append(state)
    own = [i for i, t in enumerate(transfers) if t[0] == obj]
    if kind == "final":
        return states[-1][obj]
    if not own and kind in ("first_receiver", "last_giver"):
        return None
    if kind == "first_receiver":
        return transfers[own[0]][2]
    if kind == "last_giver":
        return transfers[own[-1]][1]
    anchor = [i for i, t in enumerate(transfers) if t[0] == spec[2]]
    if not anchor:
        return None
    if kind == "before_last":
        return states[anchor[-1]][obj]
    return states[anchor[0] + 1][obj]


def read(lvl, lang, membership, initial, text, ablate=None):
    """Lenient reader. With `ablate`, ignore that one module."""
    last_any = None
    reading = []
    for line in text:
        persons = []
        for person, role, pronoun in line["persons"]:
            if pronoun and ablate == "pronoun":
                person = last_any
            persons.append((person, role))
            last_any = person
        if ablate == "role":
            agent = next(p for p, r in persons if r == "other")
            other = next(p for p, r in persons if r == "agent")
        elif ablate == "agreement" and lvl["declension"]:
            uniform = lang["case"][0]
            apparent = []
            for (person, role), (true_person, _, _) in zip(persons, line["persons"]):
                true_agent = lang["case"][membership[true_person]]
                flipped = true_agent != uniform
                apparent.append("agent" if (role == "agent") != flipped else "other")
            if apparent.count("agent") == 1:
                agent = persons[apparent.index("agent")][0]
                other = persons[1 - apparent.index("agent")][0]
            else:
                agent, other = persons[0][0], persons[1][0]
        else:
            agent = next(p for p, r in persons if r == "agent")
            other = next(p for p, r in persons if r == "other")
        verb = "give" if ablate == "inversion" else line["verb"]
        status = line["status"]
        if (status == "neg" and ablate == "negation") or (status == "irr" and ablate == "irrealis"):
            status = "real"
        reading.append(dict(line, agent=agent, other=other, verb=verb, status=status,
                            plup=line["plup"] and ablate != "tense"))
    return [(l["obj"], *_transfer(l["verb"], l["agent"], l["other"]))
            for l in _chronological(reading)]


def truth(initial, text):
    return [(l["obj"], *_transfer(l["verb"], l["agent"], l["other"])) for l in _chronological(text)]


def select_questions(rng, lvl, lang, membership, initial, text, count=6):
    """Pick questions that cover every load-bearing module; None if impossible."""
    gold = truth(initial, text)
    required = ["role", "inversion", "tense", "negation"]
    if lvl["declension"]:
        required.append("agreement")
    for module in ("irrealis", "pronoun"):
        if module in lvl["modules"]:
            required.append(module)
    ablated = {m: read(lvl, lang, membership, initial, text, m) for m in required}
    pool = []
    for spec in candidate_questions():
        value = answer(initial, gold, spec)
        if value is None:
            continue
        tags = {m for m in required if answer(initial, ablated[m], spec) != value}
        pool.append((spec, value, tags))
    rng.shuffle(pool)
    content = set(required) - {"role", "inversion"}
    chosen, covered = [], set()

    def allowed(item):
        return sum(value == item[1] for _, value, _ in chosen) < MAX_SAME_ANSWER

    while len(chosen) < count and covered != set(required):
        options = [item for item in pool if allowed(item) and item[2] - covered]
        if not options:
            return None
        best = max(options, key=lambda item: (len(item[2] - covered), len(item[2] & content)))
        chosen.append(best)
        covered |= best[2]
        pool.remove(best)
    pool.sort(key=lambda item: len(item[2] & content))
    while len(chosen) < count and pool:
        item = pool.pop()
        if allowed(item):
            chosen.append(item)
    if len(chosen) < count:
        return None
    rng.shuffle(chosen)
    return chosen
