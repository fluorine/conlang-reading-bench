"""Longer, multi-question stories with cumulative, verified marker hints."""
from .scoring import parse
from .three_object_probe import build

OBJECTS = ('coin', 'key', 'book', 'ring', 'cup')
TARGETS = ('coin', 'key', 'book', 'ring')
HINT_LEVELS = (1, 5, 15)
SIMPLE_HINT_LEVELS = (1, 5, 30)
LENGTH = 30


def _parts(prompt):
    instruction, clue, story, questions = prompt.split('\n\n')
    prefix = ' Known suffix meanings (object/reference holder/role): '
    if prefix not in clue:
        raise ValueError('expected a disclosed marker')
    header, meanings = clue.split(prefix, 1)
    return instruction, header, meanings.removesuffix('.').split('; '), story, questions


def build_story(world_seed, language_seed, scheme='shared', observed_hints=False, hint_levels=None,
                min_observed_markers=0, defer_target_final=False, query_after=None):
    """Return the same questions at three nested hint levels and an English control.

    Every accepted item has one answer for all four questions at the least
    disclosed level, and none is uniquely answered after erasing all suffixes.
    """
    if scheme not in ('shared', 'unique'):
        raise ValueError('unknown marker scheme')
    if (type(min_observed_markers) is not int or min_observed_markers < 0
            or (min_observed_markers and not observed_hints)
            or type(defer_target_final) is not bool
            or (defer_target_final and (not observed_hints or scheme != 'unique'))):
        raise ValueError('invalid observed-marker minimum')
    shared = scheme == 'shared'
    maximum = 15 if shared else 30
    hint_levels = tuple(hint_levels) if hint_levels is not None else (HINT_LEVELS if shared else SIMPLE_HINT_LEVELS)
    if (len(hint_levels) != 3 or any(type(count) is not int or not 1 <= count <= maximum for count in hint_levels)
            or tuple(sorted(set(hint_levels))) != hint_levels):
        raise ValueError('hint levels must be three increasing valid counts')
    prompts, answer = [], None
    for count in hint_levels:
        prompt, gold = build(world_seed, language_seed, length=LENGTH, objects=OBJECTS,
                             syncretism=shared, revealed=count, query_objects=TARGETS,
                             nested_hints=True, allow_simple_hints=not shared,
                             observed_hints=observed_hints, defer_target_final=defer_target_final,
                             query_after=query_after)
        if answer is not None and gold != answer:
            raise ValueError('gold changed across hint stages')
        prompts.append(prompt)
        answer = gold
    parts = [_parts(prompt) for prompt in prompts]
    if any((p[0], p[1], p[3], p[4]) != (parts[0][0], parts[0][1], parts[0][3], parts[0][4])
           for p in parts[1:]):
        raise ValueError('story, question or grammar changed across stages')
    if any(parts[i][2] != parts[i + 1][2][:len(parts[i][2])] for i in range(len(parts) - 1)):
        raise ValueError('hint stages are not cumulative')
    if observed_hints:
        observed = {word.split('-', 1)[1] for line in parts[0][3].splitlines()
                    for word in line.split() if '-' in word}
        if len(observed) < min_observed_markers:
            raise ValueError('too few observed markers')
        first_hints = [entry.split(':', 1)[0].removeprefix('-') for entry in parts[1][2]]
        if any(marker not in observed for marker in first_hints[:min(len(observed), len(first_hints))]):
            raise ValueError('an early disclosed marker is absent from the story')
    english, english_gold = build(world_seed, language_seed, length=LENGTH, objects=OBJECTS,
                                  syncretism=shared, revealed=hint_levels[0], query_objects=TARGETS,
                                  nested_hints=True, allow_simple_hints=not shared,
                                  observed_hints=observed_hints, defer_target_final=defer_target_final,
                                  english=True, query_after=query_after)
    if english_gold != answer:
        raise ValueError('English control does not match')
    if defer_target_final:
        events = english.split('\n\n')[1].splitlines()[1 + len(OBJECTS):]
        transfers = parts[0][3].splitlines()[1 + len(OBJECTS):]
        excluded = set()
        for target in TARGETS:
            indices = [i for i, line in enumerate(events) if f' the {target} to ' in line]
            if not indices:
                raise ValueError('target has no transfer')
            excluded.update(word.split('-', 1)[1] for word in transfers[indices[-1]].split())
        disclosed = {entry.split(':', 1)[0].removeprefix('-') for entry in parts[0][2]}
        if disclosed & excluded or any(marker not in observed for marker in disclosed):
            raise ValueError('insufficient eligible hints before final-transfer markers')
    questions = parts[0][4]
    continuation = []
    for i in range(1, len(parts)):
        new = parts[i][2][len(parts[i - 1][2]):]
        continuation.append('Additional suffix meanings (object/reference holder/role): '
                            + '; '.join(new) + '.\n\n' + questions
                            + '\n\nReturn only a JSON array of four names in question order.')
    repeat = ('No new information has been provided. Answer the same questions again.\n\n'
              + questions + '\n\nReturn only a JSON array of four names in question order.')
    return {'prompts': prompts, 'continuation': continuation, 'repeat': repeat,
            'english': english, 'answers': answer}


def score(raw, answers):
    parsed = parse(raw)
    return [i < len(parsed) and parsed[i] == gold.casefold() for i, gold in enumerate(answers)]
