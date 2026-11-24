# Regrading saved answers: final-array scoring

The charts for Tiers 3 and 4 now use a **uniform final-array regrade** for every shown model. It reads the last complete JSON answer array only when it appears at the end of the reply, allowing preceding explanation and a matching Markdown code fence or bold wrapper. It does not infer answers from prose, accept trailing commentary after an array, or fill in missing answers. The same rule is applied to every model, including those whose strict scores were already nonzero.

This is a new, explicitly named analysis (`final-array-1.0`), not a new model run. The original response archives, recorded strict marks, historical reports, frozen protocols and preregistered conclusions remain unchanged. The chart's point details also show the original scorer's accuracy, the share of requests that returned a complete bare JSON array, and how many requests hit the output cap. The original scorer also tolerated a standalone code fence, so its score and the stricter bare-JSON compliance percentage measure different things.

## Tier 3: 48 stories, one answer each

| Model and effort | Regraded conlang | Regraded English | Original conlang score | Bare-JSON conlang responses |
|---|---:|---:|---:|---:|
| GPT-6 Luna, low | 14/48 (29.17%) | 48/48 (100%) | 14/48 | 47/48 |
| GPT-6 Luna, medium | 18/48 (37.50%) | 48/48 (100%) | 18/48 | 48/48 |
| GPT-6 Sol, low | 18/48 (37.50%) | 48/48 (100%) | 18/48 | 48/48 |
| GPT-6.1 Terra, medium | 40/48 (83.33%) | 48/48 (100%) | 40/48 | 48/48 |
| Claude Haiku 5.5, low | 21/48 (43.75%) | 48/48 (100%) | 21/48 | 9/48 |
| Claude Sonnet 5.5, low | 21/48 (43.75%) | 48/48 (100%) | 0/48 | 0/48 |
| Claude Sonnet 5.5, high | 17/48 (35.42%) | 48/48 (100%) | 17/48 | 17/48 |

Sonnet low placed reasoning before its final answer; the original scorer rejected those replies. Haiku often used standalone JSON code fences, which the original scorer accepted but the bare-JSON compliance measure does not. Sonnet high hit its 8,192-token cap on **30 of 48 conlang requests**, with no recoverable final answer in those requests. Those answers remain wrong in this regrade; its score cannot be treated as an unconstrained high-effort measurement. Haiku low hit its cap on three conlang requests. Sonnet low's conlang replies were not capped. See the [original Claude run report](CLAUDE-LOW.md) for settings and provenance.

## Tier 4: 48 stories, four answers each

| Model and effort | Regraded zero-hint conlang | Regraded English control | Original zero-hint score | Bare-JSON conlang responses |
|---|---:|---:|---:|---:|
| GPT-6 Luna, low | 75/192 (39.06%) | 189/192 (98.44%) | 75/192 | 40/48 |
| GPT-6 Luna, medium | 176/192 (91.67%) | 192/192 (100%) | 176/192 | 46/48 |
| GPT-6.1 Terra, medium | 191/192 (99.48%) | 192/192 (100%) | 191/192 | 48/48 |
| Claude Sonnet 5.5, low | 128/192 (66.67%) | 192/192 (100%) | 0/192 | 0/48 |

Sonnet's regraded one-hint and full-grammar results are 157/192 (81.77%) and 192/192 (100%). The other model scores above are unchanged by this extraction rule. Luna medium had one capped empty response at the separate one-hint stage, not in the zero-hint chart. Cross-provider runs used different completion caps (Sonnet low 4,096; the OpenAI Tier 3 and 4 runs used 8,192 or more), so comparisons remain preliminary. Four answers in a Tier 4 request share one story and are not independent samples. The accepted zero-hint calibration was evaluated using the original scoring rules; this regrade does not retroactively change that preregistration.

## Reproduce without model calls

From the repository root, `python -m unittest discover -s tests -v`, `python -m conlang.verify_final_array_regrade`, and `node tests/test_plot.js` reverify the saved responses and chart data without model calls. To regenerate the data after adding results, run `python -m experiments.build_tier3_site` and `python -m experiments.build_tier4_site`. Both builders first verify the original prompt, gold answer, recorded marks and cost, then apply `conlang.scoring.parse_final_answer` uniformly to the raw text. CI checks the reconstructed chart data against the committed files. Existing raw transcripts are not rewritten. A regrade cannot attest that a remote provider generated a submitted response, eliminate public-test contamination, or recover an answer that was never returned.
