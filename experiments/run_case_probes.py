"""Run a frozen three-object development manifest with a capped budget.

Example: python -m experiments.run_case_probes --manifest experiments/syncretic-one-clue-dev.json --out .work/my-probe --budget 0.20 --rates 0.1 0.5
"""
import argparse
import hashlib
import json
import math
import os
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from conlang.runner import bound, price, settings
from conlang.scoring import parse
from conlang.suite import read, write
from conlang.three_object_probe import build


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--budget', type=float, required=True)
    parser.add_argument('--model', default='gpt-6-luna')
    parser.add_argument('--effort', default='medium')
    parser.add_argument('--max-output', type=int, default=16384)
    parser.add_argument('--rates', nargs=2, type=float, required=True, metavar=('INPUT', 'OUTPUT'))
    parser.add_argument('--retry-uncertain', action='store_true',
                        help='preserve pending attempts and reserve their maximum cost before retrying')
    args = parser.parse_args()
    if (not all(math.isfinite(value) and value >= 0 for value in [args.budget, *args.rates])
            or args.max_output < 1):
        parser.error('budget and rates must be non-negative; max-output must be positive')
    manifest = read(args.manifest)
    if not manifest.get('syncretism') or not manifest.get('pairs'):
        parser.error('expected a nonempty shared-ending manifest')
    if len({tuple(pair) for pair in manifest['pairs']}) != len(manifest['pairs']):
        parser.error('manifest contains repeated seed pairs')
    conf = settings(args.model, args.effort, args.max_output, args.rates)
    directory = Path(args.out)
    directory.mkdir(parents=True, exist_ok=True)
    metadata = {'manifest_sha256': hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest(),
                'model': args.model, 'effort': args.effort, 'max_output': args.max_output,
                'rates': args.rates}
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
        expected = {f'{world}-{language}-{int(english)}' for world, language in manifest['pairs']
                    for english in (False, True)}
        if any(path.stem not in expected for path in pending_paths):
            raise ValueError('unknown pending request in output directory')
        uncertain = directory / 'uncertain'
        uncertain.mkdir(exist_ok=True)
        for path in pending_paths:
            path.rename(uncertain / f'{path.stem}-{uuid.uuid4().hex}.json')
    work = []
    committed = sum(read(path)['reservation'] for path in (directory / 'uncertain').glob('*.json'))
    for world, language in manifest['pairs']:
        for english in (False, True):
            prompt, gold = build(world, language, length=manifest['length'], english=english,
                                 syncretism=True, revealed=manifest.get('revealed', 0))
            path = directory / f'{world}-{language}-{int(english)}.json'
            if path.with_suffix('.pending').exists():
                raise ValueError(f'uncertain request requires manual reconciliation: {path}')
            if path.exists():
                row = read(path)
                if (row['prompt'], row['gold'], row.get('requested_model'), row.get('effort'),
                    row.get('max_output')) != (prompt, gold, args.model, args.effort, args.max_output):
                    raise ValueError(f'existing file does not match this run: {path}')
                committed += row['cost']
            else:
                work.append((world, language, english, prompt, gold, path))
                committed += bound(conf, prompt)
    if committed > args.budget:
        raise ValueError(f'completed costs plus worst-case remaining requests ${committed:.4f} exceed budget')

    def run(item):
        world, language, english, prompt, gold, path = item
        body = {'model': args.model, 'reasoning_effort': args.effort,
                'max_completion_tokens': args.max_output, 'messages': [{'role': 'user', 'content': prompt}]}
        request = urllib.request.Request('https://api.openai.com/v1/chat/completions',
                                         data=json.dumps(body).encode(),
                                         headers={'Authorization': 'Bearer ' + os.environ['OPENAI_API_KEY'],
                                                  'Content-Type': 'application/json'})
        started = datetime.now(timezone.utc).isoformat()
        pending = path.with_suffix('.pending')
        write(pending, {'started_utc': started, 'reservation': bound(conf, prompt)})
        with urllib.request.urlopen(request, timeout=240) as response:
            result = json.load(response)
        raw = result['choices'][0]['message'].get('content') or ''
        usage = result['usage']
        row = {'world': world, 'language': language, 'english': english, 'prompt': prompt,
               'gold': gold, 'raw': raw, 'correct': parse(raw) == [gold.casefold()],
               'requested_model': args.model, 'model': result['model'], 'effort': args.effort,
               'max_output': args.max_output, 'started_utc': started,
               'finish_reason': result['choices'][0].get('finish_reason'), 'usage': usage,
               'cost': price(conf, usage['prompt_tokens'], usage['completion_tokens'])}
        write(path, row)
        pending.unlink()
        print(path, 'correct' if row['correct'] else 'incorrect', flush=True)

    with ThreadPoolExecutor(max_workers=3) as pool:
        for offset in range(0, len(work), 3):
            list(pool.map(run, work[offset:offset + 3]))


if __name__ == '__main__':
    main()
