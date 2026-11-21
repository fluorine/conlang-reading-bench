"""Rebuild Sol's matched runs and compare against the archived models."""
import hashlib
import json
import math
import random
from pathlib import Path

from conlang.runner import price, settings
from conlang.scoring import parse
from conlang.three_object_probe import build
from conlang.verify_tier3_comparison import ARCHIVE as BASE_ARCHIVE, SUITES, main as verify_base

ARCHIVE = Path('reports/sol-comparison-responses.json')


def main():
    verify_base()
    archive = json.loads(ARCHIVE.read_text(encoding='utf-8'))
    base = json.loads(BASE_ARCHIVE.read_text(encoding='utf-8'))
    if set(archive['runs']) != set(SUITES):
        raise ValueError('Sol comparison requires both frozen samples')
    differences = {'luna': [], 'terra': []}
    for suite, manifest_name in SUITES.items():
        manifest = json.loads(Path(f'experiments/{manifest_name}.json').read_text(encoding='utf-8'))
        pairs = {tuple(pair) for pair in manifest['pairs']}
        bundle = archive['runs'][suite]
        metadata, rows = bundle['metadata'], bundle['responses']
        fingerprint = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
        if (metadata.get('manifest_sha256') != fingerprint or metadata.get('model') != 'gpt-6-sol'
                or metadata.get('effort') != 'low' or metadata.get('max_output') != 16384
                or metadata.get('rates') != [2, 10]):
            raise ValueError(f'{suite}: manifest or configuration mismatch')
        expected = {(world, language, english) for world, language in pairs for english in (False, True)}
        actual = {(row['world'], row['language'], row['english']) for row in rows}
        if actual != expected or len(rows) != len(expected):
            raise ValueError(f'{suite}: incomplete or repeated items')
        conf = settings('gpt-6-sol', 'low', 16384, [2, 10])
        result = {}
        for row in rows:
            prompt, gold = build(row['world'], row['language'], length=manifest['length'],
                                 english=row['english'], syncretism=True,
                                 revealed=manifest['revealed'], objects=tuple(manifest['objects']))
            usage = row['usage']
            if (row['prompt'] != prompt or row['gold'] != gold
                    or row['correct'] != (parse(row['raw']) == [gold.casefold()])
                    or row.get('requested_model') != 'gpt-6-sol' or row.get('effort') != 'low'
                    or row.get('max_output') != 16384
                    or not math.isclose(row['cost'], price(conf, usage['prompt_tokens'], usage['completion_tokens']), abs_tol=1e-10)):
                raise ValueError(f'{suite}: response, configuration or cost mismatch')
            result[(row['world'], row['language'], row['english'])] = row['correct']
        print(f'sol-{suite}:', *(f'{sum(row["correct"] for row in rows if row["english"] == english)}/{len(pairs)}' for english in (False, True)))
        print(f'  capped: {sum(row.get("finish_reason") == "length" for row in rows)}; '
              f'empty: {sum(not row["raw"] for row in rows)}; '
              f'observed token-valued cost: ${sum(row["cost"] for row in rows):.5f}')
        for model in differences:
            other = {(row['world'], row['language']): row['correct']
                     for row in base['runs'][f'{model}-{suite}']['responses'] if not row['english']}
            if set(other) != pairs:
                raise ValueError(f'{suite}: base comparison does not match')
            differences[model].append([result[(world, language, False)] - other[(world, language)]
                                       for world, language in sorted(pairs)])
    for model, strata in differences.items():
        count = sum(map(len, strata))
        observed = sum(map(sum, strata)) / count
        rng = random.Random(492014)
        samples = sorted(sum(stratum[rng.randrange(len(stratum))] for stratum in strata for _ in stratum)
                         / count for _ in range(10000))
        print(f'Sol minus {model} paired accuracy: {observed:+.1%}; suite-stratified bootstrap '
              f'95% interval {samples[249]:+.1%} to {samples[9749]:+.1%}')


if __name__ == '__main__':
    main()
