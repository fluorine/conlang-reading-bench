"""Transparent baselines using only information visible in a Tier 4 prompt."""
import re

from .tier4_dynamic import TARGETS, _parts


def last_disclosed_transfer(prompt):
    """Track the latest transfer whose object and role a disclosed suffix identifies.

    Unrecognized transfers are ignored, so the tracked holder can become stale.
    The initial holder is the fallback. This is a heuristic, not a solver.
    """
    _, header, meanings, story, _ = _parts(prompt)
    roots = {word: obj for word, obj in re.findall(
        r'([a-z]+) = (coin|key|book|ring|cup)', header)}
    known = {}
    for entry in meanings:
        marker, description = entry.split(': ', 1)
        alternatives = description.split(' or ')
        parsed = [tuple(meaning.split('/')) for meaning in alternatives]
        choices = {(obj, role) for obj, _, role in parsed}
        if len(choices) == 1:
            known[marker.removeprefix('-')] = next(iter(choices))
    lines = story.splitlines()[1:]
    holders = {}
    for line in lines:
        words = line.split()
        if len(words) == 3 and words[2] in roots:
            holders[roots[words[2]]] = words[0]
        elif len(words) == 2 and all('-' in word for word in words):
            names = [word.split('-', 1) for word in words]
            evidence = []
            for index, (_, suffix) in enumerate(names):
                if suffix in known:
                    obj, role = known[suffix]
                    recipient = names[index if role == 'recipient' else 1 - index][0]
                    evidence.append((obj, recipient))
            if evidence and len(set(evidence)) == 1:
                obj, recipient = evidence[0]
                holders[obj] = recipient
    if any(target not in holders for target in TARGETS):
        raise ValueError('missing initial holder')
    return [holders[target] for target in TARGETS]
