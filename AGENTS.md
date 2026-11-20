# Replicating a model run

Use Python 3.12 from a checkout of the v0.1.0 tag. Run commands from the repository root. Code, seeds, prompts, and scores are versioned. Fork the repository for a new submission and use a new filename for every independent run.

## Verify the protocol first

Run `python -m unittest discover -s tests -v`. Generate a smoke suite with `python -m conlang generate --suite smoke --out .work/smoke`. Inspect the worked story in the README. Run `python -m conlang verify-results --index .work/regraded.json` to recompute the published scores without keys or paid requests.

## Collect an independent run

1. Select a **suite**. `smoke` has two stories and eight calls. `reference` aliases the frozen `holdout2` manifest with 24 stories and 96 calls. `dev2`, `dev3`, and `questions` reproduce the exploratory selection runs. Custom suites can be exported with `generate --manifest file.json`. A new protocol or suite needs its own comparison group.
2. Select a **model and effort**. Use a pinned model identifier when available. The pilot used default effort, temperature zero and at most 64 completion tokens. The official OpenAI adapter accepts a provider-native `--effort` value and `--max-output`; with explicit reasoning effort it omits temperature. Use the identical options for estimate and run. Two native effort levels on the same reference suite are separate configurations. Give reasoning models enough completion capacity for their internal tokens and disclose any change.
3. Estimate costs with `python -m conlang estimate --suite reference --model gpt-4.1-mini-2025-04-14`. Estimates bound input by UTF-8 bytes plus a one-message allowance and charge the full output cap. Check current provider rates. Pass `--rates INPUT OUTPUT` in USD per million tokens for a new model or a price change. The runner targets the official OpenAI chat completions endpoint.
4. Set `OPENAI_API_KEY` through your local environment. Run `python -m conlang run --suite reference --model gpt-4.1-mini-2025-04-14 --budget 0.25 --out .work/my-run.json`. A budget applies to one bundle, including reservations for uncertain requests. Split any overall spending limit across the planned bundles before starting. Resume with the same file, suite and configuration. A failed provider request stops the run and saves its status. Retrying means rerunning the command. The runner sends just the visible prompt in a fresh context.
5. Score your bundle using `python -m conlang score .work/my-run.json --out .work/my-score.json`. Confirm completeness and inspect usage and per-question outcomes. Use `compare` with an existing bundle to obtain a paired difference and a 95% bootstrap interval. Model sampling can vary between runs even at temperature zero.

## Use a different model adapter

For a fresh seed set, run `python -m conlang sample --name fresh --seed 1234 --count 24 --length 2 --out .work/fresh.json`, then `python -m conlang generate --manifest .work/fresh.json --out .work/fresh`. To run or grade it by name in your research checkout, place the manifest at `suites/fresh.json`. Publish a new suite through a protocol PR before submitting scores for it, so that the trusted base scorer can load the manifest.

Export `reference` into a fresh directory. An external adapter receives only `public/prompts.json`, which maps item IDs to the exact user prompts. Send each prompt in an independent context, with no additional demonstrations, tools, gold answers or answer feedback. Copy `adapter-template.json` and replace the provider, model, effort, temperature and output cap with the actual settings. Record the actual start timestamp, benchmark commit, adapter/version, any additional decoding settings, and provider-reported revision and usage where available. Store each model's verbatim text in the matching `raw` field, retaining the prompt hash. Remove entries for unexecuted calls. Report unavailable billing or token data as unknown. A word processor, human, or model silently repairing answers invalidates the comparison.

Import using `python -m conlang run --suite reference --import .work/external.json --out .work/accepted.json`. Reuse the standard scorer. Generation, provider invocation, and grading are separate modules and an adapter can be published independently.

## Submit and corroborate

Copy a completed bundle to `results/<canonical-suite>/<unique-run-id>.json`. For the reference suite the directory is `results/holdout2/`. For a fresh rerun of an existing configuration, set the optional top-level field `independent_rerun_of` to the prior path relative to `results/`. A copied response file is a regrade. An independent rerun requires new model requests.

Regenerate the checked index with `python -m conlang verify-results --index reports/index.json`. Commit the bundle and updated index on a branch in your fork, push, and open a results PR. Include the model revision, settings, measured cost or unknown billing status, and linked prior run if applicable. Include only benchmark responses and reproducibility metadata. CI checks coverage and recomputes scores from submitted responses with the base revision's code, using no API keys. The CI artifact is the independently regraded index. An independent rerun link is a contributor declaration that maintainers check against timestamps, provenance and new raw responses. CI regrading verifies arithmetic; it cannot attest that a remote provider produced a submitted transcript.

## Project maps for the maintainer workspace

Follow the workspace's project-map instructions when its custom agent and configuration are available. Keep local dashboards under the ignored `.project-map/` directory. Refresh after milestones. A public contributor can reproduce, compare or submit results using the CLI alone.
