"""Measure implications of the deferred-marker policy without model calls."""
import json
from random import Random
from pathlib import Path

from .tier4_baselines import deferred_policy_candidates, last_disclosed_transfer
from .tier4_dynamic import OBJECTS, TARGETS, build_story
from .verify_tier3_search import suffix_blind_answers


def analyze(path):
    manifest = json.loads(Path(path).read_text(encoding='utf-8'))
    if not manifest.get('defer_target_final'):
        raise ValueError('policy not enabled')
    totals = {'questions': 0, 'reduced': 0, 'singleton': 0,
              'blind_sizes': 0, 'ordinary_sizes': 0, 'policy_sizes': 0,
              'blind_expected': 0, 'ordinary_expected': 0, 'policy_expected': 0,
              'regular_fully_hidden': 0, 'deferred_fully_hidden': 0,
              'unmarked_last_word': 0, 'last_word': 0, 'unmarked_events': 0, 'events': 0}
    for world, language in manifest['pairs']:
        case = build_story(world, language, scheme=manifest['scheme'],
                           observed_hints=manifest['observed_hints'],
                           hint_levels=manifest['hint_levels'],
                           min_observed_markers=manifest.get('min_observed_markers', 0),
                           defer_target_final=True)
        prompt = case['prompts'][0]
        policy = deferred_policy_candidates(prompt)
        last_known = last_disclosed_transfer(prompt)
        parts = prompt.split('\n\n')
        story_lines = parts[2].splitlines()[1 + len(OBJECTS):]
        english_lines = case['english'].split('\n\n')[1].splitlines()[1 + len(OBJECTS):]
        observed = {word.split('-')[1] for line in story_lines for word in line.split()}
        full_case = case if manifest['hint_levels'][-1] == 30 else build_story(
            world, language, scheme=manifest['scheme'], observed_hints=True,
            hint_levels=(manifest['hint_levels'][0], 29, 30),
            min_observed_markers=manifest.get('min_observed_markers', 0), defer_target_final=True)
        full_entries = full_case['prompts'][2].split(' Known suffix meanings (object/reference holder/role): ')[1].split('\n\n')[0]
        full_markers = sorted(entry.split(':', 1)[0].removeprefix('-')
                              for entry in full_entries.removesuffix('.').split('; '))
        order = Random(language ^ 0x51F).sample(full_markers, len(full_markers))
        order = [x for x in order if x in observed] + [x for x in order if x not in observed]
        regular_hints = set(order[:manifest['hint_levels'][0]])
        deferred_hints = {entry.split(':', 1)[0].removeprefix('-') for entry in
                          parts[1].split(' Known suffix meanings (object/reference holder/role): ')[1]
                          .removesuffix('.').split('; ')}
        unmarked_lines = [line for line in story_lines if all(
            word.split('-')[1] not in deferred_hints for word in line.split())]
        if not unmarked_lines:
            raise ValueError('policy requires undisclosed final-transfer markers')
        last_unmarked = unmarked_lines[-1].split()[-1].split('-')[0]
        last_word = story_lines[-1].split()[-1].split('-')[0]
        totals['unmarked_events'] += len(unmarked_lines)
        totals['events'] += len(story_lines)
        for index, candidates in enumerate(policy):
            indices = [i for i, line in enumerate(english_lines)
                       if f' the {TARGETS[index]} to ' in line]
            final_markers = {word.split('-')[1] for word in story_lines[indices[-1]].split()}
            totals['regular_fully_hidden'] += not bool(final_markers & regular_hints)
            totals['deferred_fully_hidden'] += not bool(final_markers & deferred_hints)
            totals['unmarked_last_word'] += last_unmarked == case['answers'][index]
            totals['last_word'] += last_word == case['answers'][index]
            blind = suffix_blind_answers(prompt, OBJECTS, OBJECTS.index(TARGETS[index]))
            if not candidates or case['answers'][index] not in candidates or not candidates <= blind:
                raise ValueError('invalid policy-based candidate set')
            # Without the withholding rule, the latest directly decoded
            # holder (or the initial holder) could still be the final holder.
            ordinary = candidates | ({last_known[index]} & blind)
            totals['questions'] += 1
            totals['reduced'] += len(candidates) < len(ordinary)
            totals['singleton'] += len(candidates) == 1
            totals['blind_sizes'] += len(blind)
            totals['ordinary_sizes'] += len(ordinary)
            totals['policy_sizes'] += len(candidates)
            totals['blind_expected'] += 1 / len(blind)
            totals['ordinary_expected'] += 1 / len(ordinary)
            totals['policy_expected'] += 1 / len(candidates)
    n = totals['questions']
    print(f"{path}, {manifest['hint_levels'][0]} hints: {n} questions; "
          f"sets reduced by policy {totals['reduced']}; singletons {totals['singleton']}; "
          f"mean candidates blind/ordinary/policy {totals['blind_sizes']/n:.2f}/"
          f"{totals['ordinary_sizes']/n:.2f}/{totals['policy_sizes']/n:.2f}; "
          f"uniform expected accuracy blind/ordinary/policy {100*totals['blind_expected']/n:.1f}%/"
          f"{100*totals['ordinary_expected']/n:.1f}%/{100*totals['policy_expected']/n:.1f}%")
    print(f"  final transfer has neither marker disclosed: ordinary randomized hints "
          f"{totals['regular_fully_hidden']}/{n}; deferred hints {totals['deferred_fully_hidden']}/{n}")
    print(f"  all-unknown lines {totals['unmarked_events']}/{totals['events']}; "
          f"last name on last all-unknown line {totals['unmarked_last_word']}/{n}; "
          f"last name on final line {totals['last_word']}/{n}")
    return totals


def main():
    analyze('experiments/tier4-deferred-dev.json')
    analyze('experiments/tier4-deferred-tuning.json')
    analyze('experiments/tier4-policy-audit.json')


if __name__ == '__main__':
    main()
