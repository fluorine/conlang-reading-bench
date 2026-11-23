# Replicating a Tier 4 model run

Tier 4's current comparison uses 48 public stories in four frozen 12-story manifests. Generation, provider requests and grading are separate. Each story is run in a fresh context at zero, one and ten disclosed suffix meanings, plus three fresh English-control requests. The primary score is the fraction of 192 zero-hint answers correct. These public items support corroboration, but they are not a private holdout; model aliases and provider behavior can change.

## Verify without an API key

From the repository root with Python 3.12:

```sh
python -m unittest discover -s tests -v
python -m conlang.verify_tier4_zero_comparison
```

The verifier rebuilds the visible prompts and answers, checks the full-grammar story with an independent decoder, checks completeness and saved outputs, and recomputes paired differences. It does not send model requests or prove that a provider produced the saved transcripts. The [model comparison](TIER4-MODEL-COMPARISON.md) explains the controls, missing answers and limitations.

## Run an independent replication

1. Check current provider prices and decide an overall budget. The example below uses standard Luna rates recorded in the published run; the `--budget` limit applies **per batch**, so divide your total allowance across all four batches and reserve for uncertain requests. Keep API credentials in your local environment and never commit them.
2. Use the same four frozen `experiments/tier4-zero-confirm-0.json` through `-3.json` manifests, the same model alias, low effort and output cap. Each batch contains 12 stories and 72 calls. Use a new output directory for each independent run; a copied transcript or regrade is not a rerun. The existing runner uses OpenAI Chat Completions and provider-default sampling when effort is specified.
3. For each batch, substitute its index into the following commands. A failed request stops the run; resuming with the same configuration and output directory preserves completed responses. If a request's outcome and billing are uncertain, inspect its `.pending` file and use `--retry-uncertain` only after accounting for the reserved cost.

```sh
python -m experiments.run_tier4_probes --manifest experiments/tier4-zero-confirm-0.json --out .work/my-tier4-0 --budget 0.60 --model gpt-6-luna --effort low --max-output 8192 --rates 0.1 0.5
python -m experiments.collect_tier4_dynamic --run .work/my-tier4-0 --out .work/my-tier4-0-responses.json
python -c "from pathlib import Path; from conlang.verify_tier4_dynamic import verify_run; verify_run(Path('.work/my-tier4-0-responses.json'), Path('experiments/tier4-zero-confirm-0.json'))"
```

Repeat for batches 1, 2 and 3 with distinct output directories and filenames. Preserve exact raw text, prompts, output-cap and effort settings, provider-returned model revision, request timestamps and usage. Report missing, invalid, empty or capped outputs and token-valued costs; do not silently fix answers. The published 48-story confidence intervals require combining all four batches and resampling **stories**, not individual questions.

## A different model or adapter

For a new model configuration, copy each manifest to a new path, change its name, and add a `model_config` object containing the actual `model`, `effort`, `max_output`, and two numeric `rates` per million tokens. The CLI arguments must match it. Do not change pairs, hints, question order or prompt generation if claiming a matched comparison. The [Luna medium](../experiments/tier4-zero-luna-medium-0.json) and [Terra medium](../experiments/tier4-zero-terra-medium-0.json) manifests are examples. Validate each collected batch with `verify_run` as above, then independently calculate paired story-level differences against the corresponding Luna low responses. Publish a new result identifier and describe any changed settings; do not overwrite existing archives.

A different provider adapter must send exactly each reconstructed visible prompt in an independent context, with no hidden demonstrations, tools, gold answers, prior model responses or feedback. Record verbatim responses and actual provider settings. Adapting the output to the checked archive format is the adapter's responsibility; do not silently repair responses. A new protocol, changed prompt or fresh seed set must be labeled separately and its generator and scorer published before results are compared.

## Prompt for a research agent

> Read `AGENTS.md`, this document, and the relevant Tier 4 reports in https://github.com/fluorine/conlang-reading-bench. Verify the published results offline first. Help me reproduce or extend the matched Tier 4 test using the model, effort, API access and spending limit I provide. Preserve exact prompts and independent contexts, record raw responses and usage, count missing answers as wrong, and report English and full-grammar controls, shortcut baselines, paired story-level intervals, model revision and limitations. Clearly distinguish regrading from new provider requests and an independent rerun from copied responses. Freeze any new test protocol before collecting results.
