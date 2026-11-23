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


def build_story(world_seed, language_seed, scheme='shared'):
    """Return the same questions at three nested hint levels and an English control.

    Every accepted item has one answer for all four questions at the least
    disclosed level, and none is uniquely answered after erasing all suffixes.
    """
    if scheme not in ('shared', 'unique'):
        raise ValueError('unknown marker scheme')
    shared = scheme == 'shared'
    hint_levels = HINT_LEVELS if shared else SIMPLE_HINT_LEVELS
    prompts, answer = [], None
    for count in hint_levels:
        prompt, gold = build(world_seed, language_seed, length=LENGTH, objects=OBJECTS,
                             syncretism=shared, revealed=count, query_objects=TARGETS,
                             nested_hints=True, allow_simple_hints=not shared)
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
    english, english_gold = build(world_seed, language_seed, length=LENGTH, objects=OBJECTS,
                                  syncretism=shared, revealed=hint_levels[0], query_objects=TARGETS,
                                  nested_hints=True, allow_simple_hints=not shared, english=True)
    if english_gold != answer:
        raise ValueError('English control does not match')
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
