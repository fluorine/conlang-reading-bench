"""Independently replay a fully disclosed unique-marker story from its text."""
import re
from itertools import product

from .tier4_dynamic import LENGTH, OBJECTS, TARGETS
from .three_object_probe import PEOPLE


def decode_full(prompt, query_after=None, objects=OBJECTS, targets=TARGETS, length=LENGTH,
                context_free=False):
    _, clue, story, _ = prompt.split('\n\n')
    roots = {meaning: word for word, meaning in re.findall(
        r'(\w+) = (initially holds|coin|key|book|ring|cup)', clue)}
    if set(roots) != {'initially holds', *objects} or len(set(roots.values())) != len(roots):
        raise ValueError('invalid initial vocabulary')
    prefix = ' Known suffix meanings (object/reference holder/role): '
    if prefix not in clue:
        raise ValueError('missing fully disclosed suffix table')
    mapping = {}
    for entry in clue.split(prefix, 1)[1].removesuffix('.').split('; '):
        marker, meaning = entry.split(': ', 1)
        if not marker.startswith('-') or marker[1:] in mapping:
            raise ValueError('invalid suffix table')
        mapping[marker[1:]] = tuple(meaning.split('/'))
    required = set(product(objects, ('other',) if context_free else ('giver', 'recipient', 'other'),
                           ('giver', 'recipient')))
    if len(mapping) != len(required) or set(mapping.values()) != required:
        raise ValueError('suffix table is not a complete one-to-one mapping')
    role_note = re.search(r' Role-only inventory: giver suffixes (.*?); recipient suffixes (.*?)\.', clue)
    if role_note:
        for role, listed in zip(('giver', 'recipient'), role_note.groups()):
            claimed = set(listed.split(', '))
            actual = {'-' + marker for marker, meaning in mapping.items() if meaning[2] == role}
            if claimed != actual:
                raise ValueError('role-only inventory disagrees with full suffix table')
    object_note = re.search(r' Object-only inventory: (.*?)\.', clue)
    if object_note and object_note.group(1):
        seen = set()
        for entry in object_note.group(1).split('; '):
            marker, obj = entry.split(': ', 1)
            if (not marker.startswith('-') or marker in seen or marker[1:] not in mapping
                    or mapping[marker[1:]][0] != obj):
                raise ValueError('object-only inventory disagrees with full suffix table')
            seen.add(marker)
    lines = story.splitlines()
    if lines[0] != 'Story:' or len(lines) != 1 + len(objects) + length:
        raise ValueError('invalid story length')
    state = {}
    inverse = {word: meaning for meaning, word in roots.items()}
    for line in lines[1:1 + len(objects)]:
        person, relation, word = line.split()
        obj = inverse.get(word)
        if person not in PEOPLE or relation != roots['initially holds'] or obj not in objects or obj in state:
            raise ValueError('invalid initial state')
        state[obj] = person
    checkpoint = None
    for index, line in enumerate(lines[1 + len(objects):], 1):
        words = line.split()
        if len(words) != 2:
            raise ValueError('invalid transfer')
        try:
            parsed = [(word.split('-', 1)[0], mapping[word.split('-', 1)[1]]) for word in words]
        except (KeyError, IndexError) as exc:
            raise ValueError('unknown marker') from exc
        (first, first_meaning), (second, second_meaning) = parsed
        if first not in PEOPLE or second not in PEOPLE or first == second or first_meaning[:2] != second_meaning[:2]:
            raise ValueError('inconsistent transfer markers')
        obj, context = first_meaning[:2]
        roles = {first_meaning[2]: first, second_meaning[2]: second}
        if set(roles) != {'giver', 'recipient'} or state[obj] != roles['giver']:
            raise ValueError('invalid transfer roles or holder')
        reference = 'book' if obj == 'key' else 'key'
        actual_context = ('other' if context_free else 'giver' if state[reference] == roles['giver'] else
                          'recipient' if state[reference] == roles['recipient'] else 'other')
        if actual_context != context:
            raise ValueError('invalid reference context')
        state[obj] = roles['recipient']
        if index == query_after:
            checkpoint = [state[obj] for obj in targets]
    if query_after is not None:
        if checkpoint is None:
            raise ValueError('invalid checkpoint')
        return checkpoint
    return [state[obj] for obj in targets]
