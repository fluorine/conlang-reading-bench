"""Enumerate the Tier 5 grammars consistent with visible text and revealed cards."""
from itertools import permutations, product

from .tier5_grammar import OBJECTS, PEOPLE
from .tier5_world import answer


class _Done(Exception):
    pass


class Unknown(Exception):
    """The search passed its node cap before it settled every question."""


def parse_visible(lines, roots):
    objects = {roots[o]: o for o in OBJECTS}
    verbs = {roots["give"]: "give", roots["take"]: "take"}
    initial = {}
    for line in lines[:len(OBJECTS)]:
        name, word, _ = line.split()
        initial[objects[word]] = name
    events = []
    for line in lines[len(OBJECTS):]:
        particle, persons, obj, verb = None, [], None, None
        for token in line.split():
            if "-" not in token:
                if token in objects:
                    obj = objects[token]
                else:
                    particle = token
                continue
            parts = token.split("-")
            root = next((i for i, part in enumerate(parts) if part in verbs), None)
            if root is None:
                persons.append((parts[0], parts[1]))
            else:
                verb = (parts[0] if root == 1 else None, verbs[parts[root]], parts[-1])
        if obj is None or verb is None or len(persons) != 2:
            raise ValueError(f"unparseable line: {line}")
        events.append((particle, tuple(persons), obj, verb))
    return initial, events


def _injective(keys, values, fixed):
    keys = sorted(keys)
    free = [k for k in keys if k not in fixed]
    left = [v for v in values if v not in fixed.values()]
    for chosen in permutations(left, len(free)):
        yield {**fixed, **dict(zip(free, chosen))}


def hypotheses(lvl, lang, membership, events, revealed):
    """Yield (case, target, prefix_map, plup, particle_map, pronoun_map, agent_first, members)."""
    classes = lvl["classes"]
    labels = list(range(classes))
    suffixes = sorted({s for _, persons, _, _ in events for _, s in persons})
    tenses = sorted({verb[2] for _, _, _, verb in events})
    prefixes = sorted({verb[0] for _, _, _, verb in events if verb[0] is not None})
    particles = sorted({p for p, _, _, _ in events if p is not None})
    pronouns = sorted({stem for _, persons, _, _ in events for stem, _ in persons
                       if stem not in PEOPLE})
    meanings = ["neg", "filler"] + (["irr"] if "irrealis" in lvl["modules"] else [])

    if "case" in revealed:
        cases = [tuple(lang["case"][l] for l in labels) if lvl["declension"] else lang["case"]]
    elif lvl["declension"]:
        cases = list(product(suffixes, repeat=classes))
    else:
        cases = suffixes
    if classes and "agreement" in revealed:
        targets = [lang["agree_target"]]
        prefix_maps = [{p: lang["prefixes"][p] for p in prefixes}]
        members = membership
    elif classes:
        targets = ["agent", "other"]
        labelled = ("case" in revealed and lvl["declension"]) or "pronoun" in revealed
        prefix_maps = (list(_injective(prefixes, labels, {})) if labelled
                       else [dict(zip(prefixes, labels))])
        members = None
    else:
        targets, prefix_maps, members = [None], [{}], {}
    if "tense" in revealed:
        plups = [lang["tense"]["plup"]]
    else:
        plups = tenses + ([None] if len(tenses) < 2 else [])
    fixed = {}
    for card, meaning in (("negation", "neg"), ("irrealis", "irr")):
        if card in revealed:
            word = next(w for w, m in lang["particles"].items() if m == meaning)
            if word in particles:
                fixed[word] = meaning
    particle_maps = list(_injective(particles, meanings, fixed))
    if "pronoun" in revealed:
        pronoun_maps = [{w: lang["pronouns"][w] for w in pronouns}]
    else:
        pronoun_maps = list(_injective(pronouns, labels, {}))
    if "order" in revealed and lvl["fixed_order"]:
        firsts = [lang["order"].index("agent") < lang["order"].index("other")]
    else:
        firsts = [None]
    for combo in product(cases, targets, prefix_maps, plups, particle_maps, pronoun_maps, firsts):
        yield (*combo, members)


def answer_sets(lvl, lang, membership, lines, questions, revealed, cap=300_000):
    """Return one set of possible answers per question, or raise Unknown."""
    initial, events = parse_visible(lines, lang["roots"])
    found = [set() for _ in questions]
    nodes = [0]
    classes = lvl["classes"]
    n = len(events)

    def walk(H, i, members, holder, pending, transfers, last):
        case, target, prefix_map, plup, particle_map, pronoun_map, agent_first, _ = H
        nodes[0] += 1
        if nodes[0] > cap:
            raise Unknown
        if i == n:
            for index, spec in enumerate(questions):
                found[index].add(answer(initial, transfers, spec))
            if all(len(values) > 1 for values in found):
                raise _Done
            return
        particle, persons, obj, (prefix, verb, tense) = events[i]
        new = sorted({stem for stem, _ in persons if stem in PEOPLE and stem not in members})
        for labels in product(range(classes), repeat=len(new)) if classes else [()]:
            m = {**members, **dict(zip(new, labels))}
            seen = dict(last)
            resolved = []
            for stem, suffix in persons:
                if stem in PEOPLE:
                    person, label = stem, m.get(stem)
                else:
                    label = pronoun_map[stem]
                    person = seen.get(label)
                    if person is None:
                        break
                resolved.append((person, label, suffix))
                if classes:
                    seen[label] = person
            else:
                roles = []
                for person, label, suffix in resolved:
                    agent_suffix = case[label] if lvl["declension"] else case
                    roles.append("agent" if suffix == agent_suffix else "other")
                if sorted(roles) != ["agent", "other"]:
                    continue
                if agent_first is not None and (roles[0] == "agent") != agent_first:
                    continue
                agent = resolved[roles.index("agent")]
                other = resolved[roles.index("other")]
                if agent[0] == other[0]:
                    continue
                if classes and prefix_map[prefix] != (agent if target == "agent" else other)[1]:
                    continue
                giver, recipient = ((agent[0], other[0]) if verb == "give"
                                    else (other[0], agent[0]))
                real = particle is None or particle_map[particle] == "filler"
                is_plup = tense == plup
                next_plup = i + 1 < n and events[i + 1][3][2] == plup
                h, p, t = dict(holder), pending, list(transfers)
                steps = []
                if real and is_plup:
                    if p is None or next_plup:
                        continue
                    steps = [(obj, giver, recipient), p]
                    p = None
                elif real and next_plup:
                    p = (obj, giver, recipient)
                elif real:
                    steps = [(obj, giver, recipient)]
                elif is_plup and p is not None:
                    steps, p = [p], None
                legal = True
                for o, g, r in steps:
                    if h[o] != g:
                        legal = False
                        break
                    h[o] = r
                    t.append((o, g, r))
                if legal:
                    walk(H, i + 1, m, h, p, t, seen)

    try:
        for H in hypotheses(lvl, lang, membership, events, revealed):
            members = H[-1]
            walk(H, 0, dict(members) if members else {}, dict(initial), None, [], {})
    except _Done:
        pass
    return found
