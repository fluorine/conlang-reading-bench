"""Rebuild, audit and score a frozen progressive-hint development run."""
import hashlib
import json
import math
from pathlib import Path

from conlang.runner import price, settings
from conlang.tier4_dynamic import HINT_LEVELS, SIMPLE_HINT_LEVELS, LENGTH, OBJECTS, TARGETS, build_story, score
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
    hint_levels = HINT_LEVELS if scheme == 'shared' else SIMPLE_HINT_LEVELS if scheme == 'unique' else ()
    if (manifest.get('length') != LENGTH or manifest.get('question_count') != len(TARGETS)
            or type(observed_hints) is not bool or not hint_levels
            or manifest.get('hint_levels') != list(hint_levels)):
        raise ValueError('manifest does not match Tier 4 prototype')
    metadata, rows = archive['metadata'], archive['responses']
    fingerprint = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    if (metadata.get('manifest_sha256') != fingerprint or metadata.get('model') != 'gpt-6-luna'
            or metadata.get('effort') != 'low' or metadata.get('max_output') != 8192
            or metadata.get('rates') != [0.1, 0.5] or metadata.get('modes') != list(MODES)
            or metadata.get('hint_levels') != list(hint_levels)):
        raise ValueError('run metadata mismatch')
    pairs = {tuple(pair) for pair in manifest['pairs']}
    expected = {(w, l, mode, stage) for w, l in pairs for mode in MODES for stage in range(len(hint_levels))}
    actual = {(r['world'], r['language'], r['mode'], r['stage']) for r in rows}
    if len(pairs) != len(manifest['pairs']) or actual != expected or len(rows) != len(expected):
        raise ValueError('missing, extra or repeated response')
    lookup = {(r['world'], r['language'], r['mode'], r['stage']): r for r in rows}
    conf = settings('gpt-6-luna', 'low', 8192, [0.1, 0.5])
    uniform, last, initial_holder, questions = 0.0, 0, 0, 0
    for world, language in sorted(pairs):
        case = build_story(world, language, scheme=scheme, observed_hints=observed_hints)
        if scheme == 'unique' and decode_full(case['prompts'][2]) != case['answers']:
            raise ValueError('independent fully disclosed replay disagrees with gold')
        english_story = case['english'].split('\n\n')[1].splitlines()[1:1 + len(OBJECTS)]
        starting = {line.split()[-1].removesuffix('.'): line.split()[0] for line in english_story}
        for i, target in enumerate(TARGETS):
            possible = suffix_blind_answers(case['prompts'][0], OBJECTS, OBJECTS.index(target))
            if len(possible) < 2 or case['answers'][i] not in possible:
                raise ValueError('invalid suffix-blind check')
            uniform += 1 / len(possible)
            name = case['prompts'][0].split('\n\n')[2].splitlines()[-1].split()[-1].split('-')[0]
            last += name == case['answers'][i]
            initial_holder += starting[target] == case['answers'][i]
            questions += 1
        for mode in MODES:
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
                        or row['marks'] != score(row['raw'], case['answers'])
                        or row.get('requested_model') != 'gpt-6-luna' or row.get('effort') != 'low'
                        or row.get('max_output') != 8192
                        or not math.isclose(row['cost'], price(conf, usage['prompt_tokens'], usage['completion_tokens']), abs_tol=1e-10)):
                    raise ValueError(f'{mode} stage {stage}: transcript, score or cost mismatch')
                if mode not in ('fresh_conlang', 'fresh_english'):
                    history.append({'role': 'assistant', 'content': row['raw']})
    for mode in MODES:
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
