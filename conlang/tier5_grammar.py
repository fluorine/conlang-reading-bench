"""Tier 5 difficulty levels, sampled languages, rule cards and family text."""
from random import Random

from .language import WORDS

PEOPLE = ("Ada", "Bo", "Cy", "Dee", "Eli", "Fay")
OBJECTS = ("coin", "key", "book")
VERBS = ("give", "take")
ROLES = ("agent", "other", "object", "verb")
LABELS = ("I", "II", "III")

NAME_SUFFIXES = ("ru", "mi", "ta", "ko", "sen", "ul")
TENSE_SUFFIXES = ("ke", "lo", "pu", "de", "ri")
PREFIXES = ("na", "so", "ki", "pe")
PARTICLES = ("nu", "sa", "ga", "hi", "wo")
PRONOUNS = ("vo", "te", "ji", "ba")

CARDS = ("case", "order", "agreement", "tense", "negation", "irrealis", "pronoun")

LEVELS = {
    "L1": dict(modules=("case", "order", "tense", "negation"), transfers=12,
               declension=False, distractors=1, out_of_order=0.10, people=4,
               classes=0, fixed_order=True),
    "L2": dict(modules=("case", "order", "agreement", "tense", "negation"), transfers=16,
               declension=False, distractors=2, out_of_order=0.17, people=4,
               classes=2, fixed_order=True),
    "L3": dict(modules=("case", "order", "agreement", "tense", "negation", "irrealis"),
               transfers=20, declension=True, distractors=3, out_of_order=0.25,
               people=5, classes=2, fixed_order=False),
    "L4": dict(modules=CARDS, transfers=25, declension=True, distractors=4,
               out_of_order=0.32, people=6, classes=3, fixed_order=False),
    "L5": dict(modules=CARDS, transfers=30, declension=True, distractors=5,
               out_of_order=0.40, people=6, classes=3, fixed_order=False),
}
PRONOUN_RATE = 0.3
FILLER_RATE = 0.2


def level(name):
    if name not in LEVELS:
        raise ValueError(f"unknown level: {name}")
    return dict(LEVELS[name], name=name)


def sample_language(seed, lvl):
    """Sample every grammar value for one language. Membership is per story."""
    rng = Random(seed)
    roots = dict(zip((*OBJECTS, *VERBS, "hold"), rng.sample(WORDS, len(OBJECTS) + 3)))
    suffixes = rng.sample(NAME_SUFFIXES, 2)
    classes = lvl["classes"]
    if lvl["declension"]:
        while True:
            case = {label: rng.choice(suffixes) for label in range(classes)}
            if len(set(case.values())) == 2:
                break
    else:
        case = suffixes[0]
    if lvl["fixed_order"]:
        order = rng.sample(ROLES, len(ROLES))
        verb_position = None
    else:
        order = None
        verb_position = rng.choice(("first", "last"))
    meanings = ["neg", "filler"] + (["irr"] if "irrealis" in lvl["modules"] else [])
    particles = dict(zip(rng.sample(PARTICLES, len(meanings)), meanings))
    return dict(
        roots=roots, suffixes=sorted(suffixes), case=case, order=order,
        verb_position=verb_position,
        prefixes=dict(zip(rng.sample(PREFIXES, classes), range(classes))) if classes else {},
        agree_target=rng.choice(("agent", "other")) if classes else None,
        tense=dict(zip(("past", "plup"), rng.sample(TENSE_SUFFIXES, 2))),
        particles=particles,
        pronouns=(dict(zip(rng.sample(PRONOUNS, classes), range(classes)))
                  if "pronoun" in lvl["modules"] else {}),
    )


def card_text(card, lang, lvl, membership):
    roots_suffix = lang["suffixes"]
    if card == "case":
        if lvl["declension"]:
            parts = []
            for label in range(lvl["classes"]):
                agent = lang["case"][label]
                other = next(s for s in roots_suffix if s != agent)
                parts.append(f"in class {LABELS[label]}, -{agent} marks the agent "
                             f"and -{other} marks the other person")
            return "Case depends on noun class: " + "; ".join(parts) + "."
        other = next(s for s in roots_suffix if s != lang["case"])
        return f"The suffix -{lang['case']} marks the agent. The suffix -{other} marks the other person."
    if card == "order":
        if lvl["fixed_order"]:
            words = {"agent": "agent", "other": "other person", "object": "object", "verb": "verb"}
            return "Word order is fixed: " + ", ".join(words[r] for r in lang["order"]) + "."
        return (f"Word order is free and does not mark roles. The verb always comes "
                f"{lang['verb_position']}.")
    if card == "agreement":
        groups = []
        for prefix, label in sorted(lang["prefixes"].items(), key=lambda item: item[1]):
            names = [p for p, l in sorted(membership.items()) if l == label]
            groups.append(f"class {LABELS[label]} is {', '.join(names)} (prefix {prefix}-)")
        target = "agent" if lang["agree_target"] == "agent" else "other person"
        return f"The verb prefix agrees with the class of the {target}: " + "; ".join(groups) + "."
    if card == "tense":
        return (f"The verb suffix -{lang['tense']['past']} is the ordinary past. The verb suffix "
                f"-{lang['tense']['plup']} marks an event that happened just before the event "
                "in the line above it.")
    if card == "negation":
        word = next(w for w, m in lang["particles"].items() if m == "neg")
        return f"The particle {word} means that the event did not happen."
    if card == "irrealis":
        word = next(w for w, m in lang["particles"].items() if m == "irr")
        return f"The particle {word} means that the event was only reported and did not happen."
    if card == "pronoun":
        parts = [f"{word} is class {LABELS[label]}"
                 for word, label in sorted(lang["pronouns"].items(), key=lambda item: item[1])]
        return "Pronouns: " + "; ".join(parts) + "."
    raise ValueError(f"unknown card: {card}")


def family_text(lvl):
    """The grammar family. It names feature types, never their values."""
    modules = lvl["modules"]
    lines = [
        "Starting lines have the form: name, object word, hold word. They say who starts "
        "with each object. Every other line is one event in which a person gives or takes "
        "an object. Only the current holder can give an object away, and a person can "
        "only take an object from its current holder.",
        "Each name carries a case suffix after a hyphen. Case marks the agent (the person "
        "who gives or takes) or the other person.",
        "Word order may be fixed or free.",
    ]
    if "agreement" in modules:
        labels = ", ".join(LABELS[:lvl["classes"]])
        lines.append(f"Names belong to noun classes {labels}. The verb has a prefix that "
                     "agrees with the class of one of the two persons.")
    if lvl["declension"]:
        lines.append("The meaning of a case suffix depends on the noun class of the name.")
    lines.append("The verb has a tense suffix. One tense is the ordinary past. The other "
                 "marks an event that happened just before the event in the line above it.")
    particles = ["One particle marks an event that did not happen."]
    if "irrealis" in modules:
        particles.append("Another particle marks an event that was only reported and did not happen.")
    particles.append("A particle can also carry no meaning.")
    lines.append(" ".join(particles))
    if "pronoun" in modules:
        lines.append("A pronoun can replace a name and takes a case suffix. Each pronoun "
                     "belongs to one noun class and refers to the most recently mentioned "
                     "person of that class in the event lines.")
    return "\n".join("- " + line for line in lines)


def card_orders(lvl, seed):
    """Four rotations of one seeded base order, used as a Latin square."""
    cards = [c for c in CARDS if c in lvl["modules"]]
    base = Random(seed).sample(cards, len(cards))
    step = len(base) / 4
    return [base[round(i * step):] + base[:round(i * step)] for i in range(4)]
