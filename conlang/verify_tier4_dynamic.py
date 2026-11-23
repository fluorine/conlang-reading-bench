"""Rebuild, audit and score a frozen progressive-hint development run."""
import hashlib
import json
import math
from pathlib import Path

from conlang.runner import price, settings
from conlang.tier4_dynamic import LENGTH, OBJECTS, TARGETS, build_story, score
from conlang.tier4_audit import decode_full
from conlang.verify_tier3_search import suffix_blind_answers
from experiments.run_tier4_probes import MODES

ARCHIVE = Path('reports/tier4-dynamic-dev-responses.json')
MANIFEST = Path('experiments/tier4-dynamic-dev.json')


def verify_run(archive_path, manifest_path):
    archive = json.loads(archive_path.read_text(encoding='utf-8'))
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    scheme = manifest.get('scheme', 'shared')
    observed_hints = manifest.get('observed_hints', False)
    minimum_observed = manifest.get('min_observed_markers', 0)
    defer_target_final = manifest.get('defer_target_final', False)
    query_after = manifest.get('query_after')
    reasoning_guide = manifest.get('reasoning_guide', False)
    response_format = manifest.get('response_format', 'array')
    focus_index = manifest.get('focus_index')
    compact = manifest.get('variant') == 'compact-three'
    role_hints = manifest.get('role_hints', False)
    object_hint_counts = manifest.get('object_hint_counts')
    context_free = manifest.get('context_free', False)
    objects = ('coin', 'key', 'book') if compact else OBJECTS
    targets = objects if compact else TARGETS
    hint_levels = tuple(manifest.get('hint_levels', ()))
    maximum = (10 if context_free and scheme == 'unique' and not compact else
               18 if compact and scheme == 'unique' else 15 if scheme == 'shared' else 30 if scheme == 'unique' else 0)
    modes = tuple(manifest.get('modes', MODES))
    if (manifest.get('variant', 'standard') not in ('standard', 'compact-three')
            or type(role_hints) is not bool or (role_hints and not compact)
            or type(context_free) is not bool or (context_free and (compact or scheme != 'unique' or defer_target_final))
            or (object_hint_counts is not None and not compact)
            or (compact and (scheme != 'unique' or not observed_hints or defer_target_final
                             or query_after is not None or reasoning_guide or response_format != 'array'
                             or any(mode not in ('fresh_conlang', 'fresh_english') for mode in modes)))
            or manifest.get('length') != LENGTH or manifest.get('question_count') != len(targets)
            or type(observed_hints) is not bool or type(defer_target_final) is not bool
            or (defer_target_final and (not observed_hints or scheme != 'unique'))
            or (query_after is not None and (type(query_after) is not int or not 1 <= query_after <= LENGTH))
            or (query_after is not None and defer_target_final)
            or type(reasoning_guide) is not bool
            or response_format not in ('array', 'work_answers')
            or (focus_index is not None and (type(focus_index) is not int or not 0 <= focus_index < len(targets)))
            or (focus_index is not None and (response_format != 'array' or any(mode not in ('fresh_conlang', 'fresh_english') for mode in modes)))
            or (response_format == 'work_answers' and any(mode not in ('fresh_conlang', 'fresh_english') for mode in modes))
            or type(minimum_observed) is not int
            or minimum_observed < 0 or (minimum_observed and not observed_hints) or len(hint_levels) != 3
            or any(type(count) is not int or not 1 <= count <= maximum for count in hint_levels)
            or tuple(sorted(set(hint_levels))) != hint_levels
            or not modes or len(set(modes)) != len(modes) or any(mode not in MODES for mode in modes)):
        raise ValueError('manifest does not match Tier 4 prototype')
    metadata, rows = archive['metadata'], archive['responses']
    fingerprint = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    if (metadata.get('manifest_sha256') != fingerprint or metadata.get('model') != 'gpt-6-luna'
            or metadata.get('effort') != 'low' or metadata.get('max_output') != 8192
            or metadata.get('rates') != [0.1, 0.5] or metadata.get('modes') != list(modes)
            or metadata.get('hint_levels') != list(hint_levels)):
        raise ValueError('run metadata mismatch')
    pairs = {tuple(pair) for pair in manifest['pairs']}
    expected = {(w, l, mode, stage) for w, l in pairs for mode in modes for stage in range(len(hint_levels))}
    actual = {(r['world'], r['language'], r['mode'], r['stage']) for r in rows}
    if len(pairs) != len(manifest['pairs']) or actual != expected or len(rows) != len(expected):
        raise ValueError('missing, extra or repeated response')
    lookup = {(r['world'], r['language'], r['mode'], r['stage']): r for r in rows}
    conf = settings('gpt-6-luna', 'low', 8192, [0.1, 0.5])
    uniform, last, initial_holder, questions = 0.0, 0, 0, 0
    for world, language in sorted(pairs):
        if compact:
            from conlang.tier4_compact import build_story as build_compact
            case = build_compact(world, language, hint_levels=hint_levels,
                                 min_observed_markers=minimum_observed, focus_index=focus_index,
                                 role_hints=role_hints, object_hint_counts=object_hint_counts)
        else:
            case = build_story(world, language, scheme=scheme, observed_hints=observed_hints,
                               hint_levels=hint_levels, min_observed_markers=minimum_observed,
                               defer_target_final=defer_target_final, query_after=query_after,
                               reasoning_guide=reasoning_guide, response_format=response_format,
                               focus_index=focus_index, context_free=context_free)
        if scheme == 'unique':
            audit_case = case if hint_levels[-1] == maximum else build_compact(
                world, language, hint_levels=(hint_levels[0], maximum - 1, maximum),
                min_observed_markers=minimum_observed, focus_index=focus_index,
                role_hints=role_hints, object_hint_counts=object_hint_counts) if compact else build_story(
                world, language, scheme=scheme, observed_hints=observed_hints,
                hint_levels=(hint_levels[0], maximum - 1, maximum), min_observed_markers=minimum_observed,
                defer_target_final=defer_target_final, query_after=query_after,
                reasoning_guide=reasoning_guide, response_format=response_format, focus_index=focus_index,
                context_free=context_free)
            decoded = decode_full(audit_case['prompts'][2], query_after=query_after,
                                  objects=objects, targets=targets, context_free=context_free)
            if focus_index is not None:
                decoded = [decoded[focus_index]]
            if decoded != case['answers']:
                raise ValueError('independent fully disclosed replay disagrees with gold')
        english_story = case['english'].split('\n\n')[1].splitlines()[1:1 + len(objects)]
        starting = {line.split()[-1].removesuffix('.'): line.split()[0] for line in english_story}
        if query_after is not None:
            from conlang.tier4_checkpoint import suffix_blind_checkpoint
            checkpoint_possible = suffix_blind_checkpoint(case['prompts'][0], query_after)
        selected_targets = targets if focus_index is None else (targets[focus_index],)
        for i, target in enumerate(selected_targets):
            possible = (checkpoint_possible[OBJECTS.index(target)] if query_after is not None else
                        suffix_blind_answers(case['prompts'][0], objects, objects.index(target)))
            if len(possible) < 2 or case['answers'][i] not in possible:
                raise ValueError('invalid suffix-blind check')
            uniform += 1 / len(possible)
            lines = case['prompts'][0].split('\n\n')[2].splitlines()
            line = lines[1 + len(objects) + query_after - 1] if query_after is not None else lines[-1]
            name = line.split()[-1].split('-')[0]
            last += name == case['answers'][i]
            initial_holder += starting[target] == case['answers'][i]
            questions += 1
        for mode in modes:
            history = []
            for stage in range(len(hint_levels)):
                if mode == 'fresh_conlang':
                    messages = [{'role': 'user', 'content': case['prompts'][stage]}]
                elif mode == 'fresh_english':
                    messages = [{'role': 'user', 'content': case['english']}]
                else:
                    prompt = (case['english'] if mode == 'continued_english' else case['prompts'][0]) if stage == 0 else (case['continuation'][stage - 1] if mode == 'continued_hints' else case['repeat'])
                    history.append({'role': 'user', 'content': prompt})
                    messages = list(history)
                row = lookup[(world, language, mode, stage)]
                usage = row['usage']
                if (row['messages'] != messages or row['answers'] != case['answers']
                        or row['marks'] != score(row['raw'], case['answers'], response_format=response_format)
                        or row.get('requested_model') != 'gpt-6-luna' or row.get('effort') != 'low'
                        or row.get('max_output') != 8192
                        or not math.isclose(row['cost'], price(conf, usage['prompt_tokens'], usage['completion_tokens']), abs_tol=1e-10)):
                    raise ValueError(f'{mode} stage {stage}: transcript, score or cost mismatch')
                if mode not in ('fresh_conlang', 'fresh_english'):
                    history.append({'role': 'assistant', 'content': row['raw']})
    for mode in modes:
        summaries = []
        for stage in range(len(hint_levels)):
            selected = [row for row in rows if row['mode'] == mode and row['stage'] == stage]
            correct = sum(sum(row['marks']) for row in selected)
            total = sum(len(row['marks']) for row in selected)
            summaries.append(f'{correct}/{total} ({100 * correct / total:.1f}%)')
        print(mode, ' -> '.join(summaries))
    print(f'suffix-blind random expected {100 * uniform / questions:.1f}%; '
          f'last-name {last}/{questions}; initial-holder {initial_holder}/{questions}')
    print(f'capped {sum(row.get("finish_reason") == "length" for row in rows)}; '
          f'empty {sum(not row["raw"] for row in rows)}; '
          f'observed token-valued cost ${sum(row["cost"] for row in rows):.5f}')


def main():
    verify_run(ARCHIVE, MANIFEST)


if __name__ == '__main__':
    main()
