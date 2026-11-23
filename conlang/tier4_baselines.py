"""Transparent baselines using only information visible in a Tier 4 prompt."""
import re

from .tier4_dynamic import TARGETS, _parts


def last_disclosed_transfer(prompt, query_after=None, targets=TARGETS):
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
    seen_transfers = 0
    for line in lines:
        words = line.split()
        if len(words) == 3 and words[2] in roots:
            holders[roots[words[2]]] = words[0]
        elif len(words) == 2 and all('-' in word for word in words):
            seen_transfers += 1
            if query_after is not None and seen_transfers > query_after:
                break
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
    if any(target not in holders for target in targets):
        raise ValueError('missing initial holder')
    return [holders[target] for target in targets]


def deferred_policy_candidates(prompt):
    """Holders possible under the public final-transfer withholding policy.

    Every queried object is guaranteed to have moved, and the two markers on
    its final transfer are withheld. Its final transfer must therefore be on
    a line with no disclosed marker, after its latest identified transfer.
    Intersect these names with suffix-blind legal holders. This is a necessary
    condition only; the resulting sets need not be sufficient or calibrated.
    """
    from .tier4_dynamic import OBJECTS
    from .verify_tier3_search import suffix_blind_answers

    _, _, meanings, story, _ = _parts(prompt)
    known = {}
    for entry in meanings:
        marker, description = entry.split(': ', 1)
        parsed = [tuple(value.split('/')) for value in description.split(' or ')]
        objects = {obj for obj, _, _ in parsed}
        if len(objects) == 1:
            known[marker.removeprefix('-')] = next(iter(objects))
    lines = story.splitlines()[1 + len(OBJECTS):]
    latest = {target: -1 for target in TARGETS}
    events = []
    for index, line in enumerate(lines):
        pairs = [word.split('-', 1) for word in line.split()]
        if len(pairs) != 2 or any(len(pair) != 2 for pair in pairs):
            raise ValueError('invalid transfer line')
        disclosed = {known[suffix] for _, suffix in pairs if suffix in known}
        for target in disclosed & set(TARGETS):
            latest[target] = index
        events.append((pairs, bool(disclosed)))
    results = []
    for target in TARGETS:
        names = {name for i, (pairs, has_known) in enumerate(events)
                 if i > latest[target] and not has_known for name, _ in pairs}
        results.append(names & suffix_blind_answers(prompt, OBJECTS, OBJECTS.index(target)))
    return results


def last_role_recipient(prompt):
    """Name the final transfer's recipient using an explicitly provided role inventory."""
    _, header, _, story, _ = _parts(prompt)
    match = re.search(r' Role-only inventory: giver suffixes (.*?); recipient suffixes (.*?)\.', header)
    if not match:
        raise ValueError('no role-only inventory')
    recipient_suffixes = {marker.removeprefix('-') for marker in match.group(2).split(', ')}
    words = story.splitlines()[-1].split()
    recipients = [word.split('-', 1)[0] for word in words
                  if word.split('-', 1)[1] in recipient_suffixes]
    if len(recipients) != 1:
        raise ValueError('final transfer does not have exactly one recipient')
    return recipients[0]
