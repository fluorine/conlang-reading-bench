# Tier 4: 48-story zero-hint confirmation

The [zero-hint pilot](TIER4-ZERO-DEV.md) motivated this independently seeded 48-story evaluation. The protocol and acceptance criteria were frozen before any model calls. In the primary condition, the model sees the structural grammar and initial state but no suffix meanings. It answers four questions after a 30-transfer story; each accepted story has a unique answer under the visible rules. Subsequent fresh-context calls disclose one and then all ten suffix meanings.

| Fresh context | Zero meanings | One meaning | All ten meanings |
|---|---:|---:|---:|
| GPT-6 Luna, low effort | 75/192 (39.1%) | 96/192 (50.0%) | 184/192 (95.8%) |
| English control | 189/192 (98.4%) | 192/192 (100%) | 189/192 (98.4%) |

The initial-holder rule scored **31/192 (16.1%)** and last-name guessing scored **43/192 (22.4%)**. Luna's paired advantage was **+22.9 percentage points** over initial-holder guessing (95% story bootstrap +9.9 to +36.5) and **+16.7 points** over last-name guessing (+3.6 to +29.7). The bootstrap resamples stories, preserving their four correlated questions.

The result **passed the predeclared gates**: the observed zero-hint score is below 40%; initial English and full-grammar accuracy exceed 90%; no response was empty or capped; and both shortcut difference intervals have positive lower bounds. This is a provisional basis for matched model comparisons, not a universal intelligence score. The observed score lies close to 40%, and its descriptive 95% story-bootstrap interval is **27.6% to 50.5%**, so the exact difficulty is uncertain and may vary on fresh stories or repeat runs. The two shortcuts are not exhaustive, and the uniqueness checker and decoder do not substitute for human clarity review.

There were 288 requests at approximately **$0.13751** in recorded token-valued cost. The model supplied 32 fewer than 192 parseable conlang answers at zero hints and 20 fewer at one hint; missing or invalid answers count wrong. At full disclosure all answers parsed. The [four frozen manifests](../experiments/tier4-zero-confirm-0.json) and raw response archives ([0](tier4-zero-confirm-0-responses.json), [1](tier4-zero-confirm-1-responses.json), [2](tier4-zero-confirm-2-responses.json), [3](tier4-zero-confirm-3-responses.json)) include exact prompts, responses and usage. `python -m conlang.verify_tier4_zero_confirm` reconstructs prompts, independently replays the full grammar, regrades and reproduces the comparisons without API calls. Regrading does not attest provider provenance.

Comparisons with other model-and-effort configurations should use the same stories, prompts, stages and output cap, report English and full-grammar controls, exact settings, cost and paired story-level uncertainty. Since these stories and generator are public and models may change, fresh seeds and independent reruns remain necessary to assess generalization and possible contamination. The earlier progressive-conversation condition has not yet been measured for this particular grammar; the results above are fresh-context calls, not evidence about learning across turns.
