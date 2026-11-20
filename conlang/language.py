"""A small typed grammar and an independent finite interpretation checker."""
from itertools import permutations, product
from random import Random

from .world import OBJECTS, PEOPLE, answers

ROLES = ("giver", "recipient", "object", "verb")
MEANINGS = (*OBJECTS, "holds", "gives")
WORDS = tuple(a + b for a in ("lu", "zo", "mi", "ve", "ka", "po", "ri", "nu")
              for b in ("ma", "to", "ki", "se", "vu", "pa"))
SUFFIXES = ("af", "il", "om", "es", "un", "ak")


def language(seed):
    rng = Random(seed)
    roots = dict(zip(MEANINGS, rng.sample(WORDS, 4)))
    giver, recipient = rng.sample(SUFFIXES, 2)
    order = rng.sample(ROLES, 4)
    return roots, giver, recipient, order


def render(lang, initial, events):
    roots, giver_suffix, recipient_suffix, order = lang
    lines = [f"{person} {roots['holds']} {roots[obj]}" for obj, person in initial.items()]
    for obj, giver, recipient in events:
        parts = dict(giver=giver + "-" + giver_suffix, recipient=recipient + "-" + recipient_suffix,
                     object=roots[obj], verb=roots["gives"])
        lines.append(" ".join(parts[k] for k in order))
    return lines


def evidence(lang):
    roots, giver, recipient, order = lang
    return [
        "There are two objects (coin, key) and two predicates (holds initially, gives). "
        "Each has its own word. Initial statements use holder, predicate, object. "
        "Transfers use the same four positions in some order. Each name has a role suffix "
        "after a hyphen. Only the current holder may give an object. Events are chronological. "
        f"Key word: {roots['gives']} means gives. Separate example: "
        f'Ivy {roots["holds"]} {roots["coin"]} means Ivy starts with the coin.',
        "Glossary: " + ", ".join(f"{w} = {m}" for m, w in roots.items()) + ".",
        f"Giver suffix is -{giver}; recipient suffix is -{recipient}. "
        + "Transfer order is " + ", ".join(order) + ".",
    ]


def interpretations(lines, example, gives, query):
    """Use only visible tokens, the public rules, the glossary anchor and the example."""
    initial_lines = [line.split() for line in lines[:2]]
    transfer_lines = [line.split() for line in lines[2:]]
    if len(initial_lines) != 2 or any(len(row) != 3 for row in initial_lines):
        return set()
    if not transfer_lines or any(len(row) != 4 for row in transfer_lines):
        return set()
    holds = initial_lines[0][1]
    objects = {row[2] for row in initial_lines}
    if len(objects) != 2:
        return set()
    if any(p not in PEOPLE or pred != holds for p, pred, _ in initial_lines):
        return set()
    coins = objects
    if example is not None:
        name, predicate, coin = example.split()
        if name != "Ivy" or predicate != holds or coin not in objects:
            return set()
        coins = {coin}
    possible = set()
    for coin in coins:
        vocab = {coin: "coin", next(iter(objects - {coin})): "key"}
        initial = {vocab[word]: p for p, _, word in initial_lines}
        possible.update(decode_transfers(transfer_lines, gives, query, vocab, initial))
    return possible


def decode_transfers(transfer_lines, gives, query, vocab, initial):
    suffixes = sorted({w.split("-")[1] for row in transfer_lines for w in row if "-" in w})
    if len(suffixes) != 2:
        return set()
    possible = set()
    for order, (gs, rs) in product(permutations(ROLES), permutations(suffixes)):
        events = []
        for tokens in transfer_lines:
            slot = dict(zip(order, tokens))
            if (slot["verb"] != gives or slot["object"] not in vocab
                    or not slot["giver"].endswith("-" + gs)
                    or not slot["recipient"].endswith("-" + rs)):
                break
            events.append((vocab[slot["object"]], slot["giver"].split("-")[0],
                           slot["recipient"].split("-")[0]))
        else:
            try:
                possible.add(answers(initial, events, query))
            except ValueError:
                continue
    return possible
