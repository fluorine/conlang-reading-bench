"""Three-object progressive story prototype using the established grammar."""
from .three_object_probe import build
from .tier4_dynamic import _parts

OBJECTS = ('coin', 'key', 'book')
LENGTH = 30


def build_story(world_seed, language_seed, hint_levels=(1, 3, 18),
                min_observed_markers=0, focus_index=None, role_hints=False,
                object_hint_counts=None):
    if (len(hint_levels) != 3 or tuple(sorted(set(hint_levels))) != tuple(hint_levels)
            or any(type(n) is not int or not 1 <= n <= 18 for n in hint_levels)):
        raise ValueError('invalid compact hint levels')
    if (type(min_observed_markers) is not int or min_observed_markers < 0 or type(role_hints) is not bool
            or (focus_index is not None and (type(focus_index) is not int or not 0 <= focus_index < 3))):
        raise ValueError('invalid compact options')
    if object_hint_counts is not None and (not isinstance(object_hint_counts, (list, tuple))
            or len(object_hint_counts) != 3
            or any(type(n) is not int or not 0 <= n <= 18 for n in object_hint_counts)
            or list(object_hint_counts) != sorted(object_hint_counts) or role_hints
            or hint_levels[-1] != 18):
        raise ValueError('invalid object-only inventory')
    prompts, answers = [], None
    for count in hint_levels:
        prompt, gold = build(world_seed, language_seed, length=LENGTH, objects=OBJECTS,
                             revealed=count, query_objects=OBJECTS, nested_hints=True,
                             allow_simple_hints=True, observed_hints=True)
        if answers is not None and gold != answers:
            raise ValueError('gold changed across stages')
        answers = gold
        prompts.append(prompt)
    parts = [_parts(p) for p in prompts]
    if any((p[0], p[1], p[3], p[4]) != (parts[0][0], parts[0][1], parts[0][3], parts[0][4])
           for p in parts[1:]):
        raise ValueError('story changed across hint stages')
    if any(parts[i][2] != parts[i+1][2][:len(parts[i][2])] for i in range(2)):
        raise ValueError('noncumulative hints')
    observed = {word.split('-', 1)[1] for line in parts[0][3].splitlines()
                for word in line.split() if '-' in word}
    if len(observed) < min_observed_markers:
        raise ValueError('too few observed markers')
    early = [entry.split(':', 1)[0].removeprefix('-') for entry in parts[1][2]]
    if any(marker not in observed for marker in early[:min(len(observed), len(early))]):
        raise ValueError('an early disclosed marker is absent from the story')
    english, gold = build(world_seed, language_seed, length=LENGTH, objects=OBJECTS,
                          revealed=hint_levels[0], query_objects=OBJECTS, nested_hints=True,
                          allow_simple_hints=True, observed_hints=True, english=True)
    if gold != answers:
        raise ValueError('English control does not match')
    if role_hints:
        if hint_levels[-1] != 18:
            raise ValueError('role inventory requires full mapping in final stage')
        mapping = {}
        for entry in parts[-1][2]:
            marker, meaning = entry.split(': ', 1)
            mapping[marker] = meaning.split('/')[-1]
        if len(mapping) != 18 or set(mapping.values()) != {'giver', 'recipient'}:
            raise ValueError('invalid role inventory')
        giver = ', '.join(sorted(marker for marker, role in mapping.items() if role == 'giver'))
        receiver = ', '.join(sorted(marker for marker, role in mapping.items() if role == 'recipient'))
        note = (f' Role-only inventory: giver suffixes {giver}; recipient suffixes {receiver}. '
                'This identifies roles only, not objects or reference contexts.')
        prefix = ' Known suffix meanings (object/reference holder/role): '
        prompts = [p.replace(prefix, note + prefix, 1) for p in prompts]
    if object_hint_counts is not None:
        full = [entry.split(': ', 1) for entry in parts[-1][2]]
        prefix = ' Known suffix meanings (object/reference holder/role): '
        revised = []
        for prompt, count in zip(prompts, object_hint_counts):
            entries = '; '.join(f'{marker}: {meaning.split("/")[0]}' for marker, meaning in full[:count])
            note = (f' Object-only inventory: {entries}. '
                    'These identify objects only, not roles or reference contexts.')
            revised.append(prompt.replace(prefix, note + prefix, 1))
        prompts = revised
    if focus_index is not None:
        def focus(prompt):
            sections = prompt.split('\n\n')
            selected = sections[-1].splitlines()[focus_index]
            sections[-1] = '1.' + selected.split('.', 1)[1]
            sections[0] = sections[0].replace('containing 3 names', 'containing 1 name')
            return '\n\n'.join(sections)
        prompts = [focus(prompt) for prompt in prompts]
        english = focus(english)
        answers = [answers[focus_index]]
    return {'prompts': prompts, 'english': english, 'answers': answers}
