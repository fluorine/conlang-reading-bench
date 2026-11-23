"""Run a bounded progressive-hint development sample with saved transcripts."""
import argparse
import hashlib
import json
import math
import os
import threading
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from conlang.runner import price, settings
from conlang.suite import read, write
from conlang.tier4_dynamic import LENGTH, TARGETS, build_story, score

MODES = ('fresh_conlang', 'continued_hints', 'continued_nohint', 'fresh_english', 'continued_english')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--budget', required=True, type=float)
    parser.add_argument('--model', default='gpt-6-luna')
    parser.add_argument('--effort', default='low')
    parser.add_argument('--max-output', type=int, default=8192)
    parser.add_argument('--rates', required=True, nargs=2, type=float)
    parser.add_argument('--retry-uncertain', action='store_true',
                        help='retain uncertain attempts and reserve their costs before retrying')
    args = parser.parse_args()
    if (not all(math.isfinite(x) and x >= 0 for x in [args.budget, *args.rates])
            or args.max_output < 1):
        parser.error('invalid budget, rates or output limit')
    manifest = read(args.manifest)
    scheme = manifest.get('scheme', 'shared')
    observed_hints = manifest.get('observed_hints', False)
    minimum_observed = manifest.get('min_observed_markers', 0)
    defer_target_final = manifest.get('defer_target_final', False)
    query_after = manifest.get('query_after')
    reasoning_guide = manifest.get('reasoning_guide', False)
    response_format = manifest.get('response_format', 'array')
    focus_index = manifest.get('focus_index')
    hint_levels = tuple(manifest.get('hint_levels', ()))
    maximum = 15 if scheme == 'shared' else 30 if scheme == 'unique' else 0
    modes = tuple(manifest.get('modes', MODES))
    if (manifest.get('length') != LENGTH or manifest.get('question_count') != len(TARGETS)
            or type(observed_hints) is not bool or type(defer_target_final) is not bool
            or (defer_target_final and (not observed_hints or scheme != 'unique'))
            or (query_after is not None and (type(query_after) is not int or not 1 <= query_after <= LENGTH))
            or (query_after is not None and defer_target_final)
            or type(reasoning_guide) is not bool
            or response_format not in ('array', 'work_answers')
            or (focus_index is not None and (type(focus_index) is not int or not 0 <= focus_index < len(TARGETS)))
            or (focus_index is not None and (response_format != 'array' or any(mode not in ('fresh_conlang', 'fresh_english') for mode in modes)))
            or (response_format == 'work_answers' and any(mode not in ('fresh_conlang', 'fresh_english') for mode in modes))
            or type(minimum_observed) is not int
            or minimum_observed < 0 or (minimum_observed and not observed_hints) or len(hint_levels) != 3
            or any(type(count) is not int or not 1 <= count <= maximum for count in hint_levels)
            or tuple(sorted(set(hint_levels))) != hint_levels
            or not modes or len(set(modes)) != len(modes) or any(mode not in MODES for mode in modes)):
        parser.error('manifest does not match the frozen Tier 4 prototype')
    pairs = [tuple(pair) for pair in manifest['pairs']]
    if not pairs or len(set(pairs)) != len(pairs):
        parser.error('manifest must contain distinct seed pairs')
    directory = Path(args.out)
    directory.mkdir(parents=True, exist_ok=True)
    metadata = {'manifest_sha256': hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest(),
                'model': args.model, 'effort': args.effort, 'max_output': args.max_output,
                'rates': args.rates, 'modes': list(modes), 'hint_levels': list(hint_levels)}
    metadata_path = directory / 'run.json'
    if metadata_path.exists():
        if read(metadata_path) != metadata:
            raise ValueError('output directory belongs to a different run configuration')
    elif any(directory.iterdir()):
        raise ValueError('output directory must be empty for a new run')
    else:
        write(metadata_path, metadata)
    pending_paths = list(directory.glob('*.pending'))
    if pending_paths and not args.retry_uncertain:
        raise ValueError('uncertain requests require manual reconciliation or an explicit reserved retry')
    if pending_paths:
        expected = {f'{world}-{language}-{mode}-{stage}' for world, language in pairs
                    for mode in modes for stage in range(len(hint_levels))}
        if any(path.stem not in expected for path in pending_paths):
            raise ValueError('unknown pending request in output directory')
        uncertain = directory / 'uncertain'
        uncertain.mkdir(exist_ok=True)
        for path in pending_paths:
            path.rename(uncertain / f'{path.stem}-{uuid.uuid4().hex}.json')
    conf = settings(args.model, args.effort, args.max_output, args.rates)
    existing = [read(p) for p in directory.glob('*.json') if p.name != 'run.json']
    spent = (sum(row['cost'] for row in existing)
             + sum(read(p)['reservation'] for p in (directory / 'uncertain').glob('*.json')))
    if spent > args.budget:
        raise ValueError('recorded and uncertain costs exceed budget')
    reserved = 0.0
    ledger_lock = threading.Lock()

    def episode(item):
        nonlocal spent, reserved
        (world, language), mode = item
        case = build_story(world, language, scheme=scheme, observed_hints=observed_hints,
                           hint_levels=hint_levels, min_observed_markers=minimum_observed,
                           defer_target_final=defer_target_final, query_after=query_after,
                           reasoning_guide=reasoning_guide, response_format=response_format,
                           focus_index=focus_index)
        history = []
        for stage in range(len(hint_levels)):
            if mode == 'fresh_conlang':
                messages = [{'role': 'user', 'content': case['prompts'][stage]}]
            elif mode == 'fresh_english':
                messages = [{'role': 'user', 'content': case['english']}]
            else:
                if stage == 0:
                    prompt = case['english'] if mode == 'continued_english' else case['prompts'][0]
                else:
                    prompt = case['continuation'][stage - 1] if mode == 'continued_hints' else case['repeat']
                history.append({'role': 'user', 'content': prompt})
                messages = list(history)
            path = directory / f'{world}-{language}-{mode}-{stage}.json'
            if path.exists():
                row = read(path)
                if row['messages'] != messages or row['answers'] != case['answers']:
                    raise ValueError(f'existing transcript mismatch: {path}')
            else:
                body = {'model': args.model, 'reasoning_effort': args.effort,
                        'max_completion_tokens': args.max_output, 'messages': messages}
                body_bytes = json.dumps(body, ensure_ascii=True).encode('utf-8')
                # UTF-8 JSON bytes conservatively bound text tokens; allow one envelope per message.
                reservation = price(conf, len(body_bytes) + 128 * len(messages), args.max_output)
                pending = path.with_suffix('.pending')
                started = datetime.now(timezone.utc).isoformat()
                with ledger_lock:
                    if spent + reserved + reservation > args.budget:
                        raise ValueError('budget cannot cover the next maximum-cost request')
                    write(pending, {'reservation': reservation, 'started_utc': started})
                    reserved += reservation
                request = urllib.request.Request('https://api.openai.com/v1/chat/completions', data=body_bytes,
                    headers={'Authorization': 'Bearer ' + os.environ['OPENAI_API_KEY'], 'Content-Type': 'application/json'})
                with urllib.request.urlopen(request, timeout=240) as response:
                    result = json.load(response)
                raw = result['choices'][0]['message'].get('content') or ''
                usage = result['usage']
                row = {'world': world, 'language': language, 'mode': mode, 'stage': stage,
                       'messages': messages, 'answers': case['answers'], 'raw': raw,
                       'marks': score(raw, case['answers'], response_format=response_format), 'requested_model': args.model,
                       'model': result['model'], 'effort': args.effort, 'max_output': args.max_output,
                       'started_utc': started,
                       'finish_reason': result['choices'][0].get('finish_reason'), 'usage': usage,
                       'cost': price(conf, usage['prompt_tokens'], usage['completion_tokens'])}
                write(path, row)
                with ledger_lock:
                    spent += row['cost']
                    reserved -= reservation
                    pending.unlink()
                print(mode, world, stage, sum(row['marks']), f"/{len(row['answers'])}", flush=True)
            if mode not in ('fresh_conlang', 'fresh_english'):
                if not row['raw'] and stage < len(hint_levels) - 1:
                    raise ValueError(f'empty response prevents continued-context replay: {path}')
                history.append({'role': 'assistant', 'content': row['raw']})

    episodes = [(pair, mode) for pair in pairs for mode in modes]
    with ThreadPoolExecutor(max_workers=3) as pool:
        for offset in range(0, len(episodes), 3):
            list(pool.map(episode, episodes[offset:offset + 3]))


if __name__ == '__main__':
    main()
