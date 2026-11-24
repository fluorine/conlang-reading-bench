# Claude Haiku 5.5 and Sonnet 5.5, low effort

**Update:** The charts now use a uniform [final-array regrade](FINAL-ARRAY-REGRADE.md) across all models. The strict scores below are preserved as the original historical results; the new regrade also reports format compliance separately.

Claude Haiku 5.5 ran Tiers 1, 2 and 3. Claude Sonnet 5.5 ran Tiers 3 and 4. Both used `output_config.effort = low`. Each call was one user message in a fresh context, with no system prompt and no tools.

## Official scores (strict scorer)

| Tier | Haiku 5.5 low | Sonnet 5.5 low |
|---|---|---|
| 1, reference suite (96 calls) | headline 88.19%; minimal 82.29%, glossary 82.29%, grammar 100%, English 100% | not run |
| 2, four transfers (48 stories) | minimal 86.46% original, 94.79% fresh; English 100% on both | not run |
| 3, five objects (48 questions) | 21/48 (43.75%); English 48/48 | 0/48; English 0/48 |
| 4, zero hint (192 answers) | not run | 0/192; English 0/192 |

## Why Sonnet scores 0%

Every prompt says "Return only a JSON array". Sonnet writes its reasoning first and puts the array on the last line. The strict scorer needs the whole reply to be a JSON array, so each Sonnet answer counts as wrong. The scorer is unchanged.

A secondary score reads only the last JSON array in each reply. It is not protocol-comparable.

| Sonnet 5.5 low | Strict | Last array only |
|---|---:|---:|
| Tier 3 conlang | 0/48 | 21/48 |
| Tier 3 English | 0/48 | 48/48 |
| Tier 4, 0 hints | 0/192 | 128/192 (66.7%) |
| Tier 4, 1 hint | 0/192 | 157/192 (81.8%) |
| Tier 4, 10 hints | 0/192 | 192/192 |
| Tier 4 English | 0/192 | 192/192 |

## Settings

| Item | Value |
|---|---|
| Models | `claude-haiku-5-5`, `claude-sonnet-5-5` |
| Output cap | 2,048 tokens for Tiers 1 and 2. 4,096 tokens for Tiers 3 and 4. |
| Thinking tokens reported | 0 |
| Rates (USD per million tokens, input/output) | Haiku 0.1/0.5. Sonnet 2/10. Taken from third-party coverage, not the provider page. |
| Haiku Tier 3 requests at the cap | 3 of 96 |
| Total cost | about $3.42 |

The OpenAI runs used output caps of 8,192 to 16,384 tokens on Tiers 3 and 4. The caps differ, so treat cross-provider comparisons as preliminary.

## Provenance notes

- Tier 4 used `experiments/tier4-zero-confirm-*.json` for the requests. The archives list the matching `tier4-zero-sonnet-low-*.json` manifests. These differ only in name, `model_config` and `source_manifest`. The archive field `run_manifest_sha256` keeps the hash of the manifest used for the requests.
- Sonnet Tier 4 batches resumed after the first spending cap stopped them. Resumed requests used the same settings.

## Reproduce

```sh
python -m unittest discover -s tests -v
python -m conlang.verify_haiku_low_comparison
python -m conlang.verify_sonnet_low_comparison
python -m conlang.verify_sonnet_high_comparison
python -m conlang.verify_tier4_zero_comparison
python -m experiments.build_tier3_site
python -m experiments.build_tier4_site
```

To collect new responses, set `ANTHROPIC_API_KEY` and pass `--provider Anthropic` to `python -m conlang run`, `experiments.run_case_probes` or `experiments.run_tier4_probes`.

## Sonnet 5.5 high on Tier 3

Sonnet 5.5 ran Tier 3 again at high effort, with an 8,192-token output cap. It cost about $3.46. Tier 4 did not run at high effort. The estimate is about $15, which is more than the budget.

| Sonnet 5.5 high | Strict | Last array only |
|---|---:|---:|
| Tier 3 conlang | 17/48 (35.4%) | 17/48 |
| Tier 3 English | 0/48 | 48/48 |

- 30 of the 48 conlang replies reached the 8,192-token cap and have no answer. These count as wrong. The result is limited by the cap, not only by the model.
- The 17 answered conlang replies are all bare JSON arrays. The English replies still write text before the array, so the strict English score is 0.
- At low effort with a 4,096-token cap, Sonnet 5.5 had no capped replies and a last-array score of 21/48 on the Tier 3 conlang questions. High effort scores lower because many replies run out of tokens.
- The result does not show that high effort overcomes Tier 3. It scores below Haiku 5.5 low (21/48) and below Terra medium (40/48).
