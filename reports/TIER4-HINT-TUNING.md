# Tier 4: adaptive intermediate-hint tuning

The [previous 12-story sample](TIER4-OBSERVED-FRESH.md) showed that one or five disclosed endings left Luna low near a simple shortcut, while all 30 made the test much easier. To find an intermediate starting point, we ran **new fresh-context requests on the same 12 stories and four questions**, disclosing 10, 15 and 20 unique suffix meanings. These are **adaptive development results**: the stories and grammar were already inspected, and the hint counts were chosen after seeing the earlier outcome. They are not an independent confirmation.

| Disclosed suffix meanings | Luna low, correct answers | Accuracy |
|---|---:|---:|
| 10 | 19/48 | 39.58% |
| 15 | 21/48 | 43.75% |
| 20 | 36/48 | 75.00% |

On these same questions, always choosing the last name mentioned scores **12/48 (25%)**, and uniform guessing among suffix-blind possible holders has **18.1% expected accuracy**. Ten meanings exceeds the last-name score by **14.6 percentage points**; a descriptive story-bootstrap interval is **+2.1 to +27.1 points**. Because we tried several disclosure levels and selected one after inspecting the results, this interval is not confirmatory evidence of an advantage. Model sampling and the shared grammar family add further uncertainty.

The 36 calls used fresh contexts, low reasoning and the same 8,192 completion-token cap; none was empty or capped. They cost approximately **$0.03251** at the recorded token rates, not including the earlier runs. No new English controls or continuing-conversation trials were made for these intermediate levels; the earlier study's English and no-new-hint responses remain separate observations, not new trials.

Ten disclosed meanings is a **candidate**, not a calibrated tier. Before testing stronger models, freeze untouched stories and check Luna low, paired English controls, repeated-question and no-new-hint conditions, story-level uncertainty, and shortcuts. A score below 40% without an advantage over simple baselines is insufficient. The accepted story must remain unambiguous under the visible grammar and pass the independent fully disclosed replay.

The [manifest](../experiments/tier4-hint-tuning.json) and code were frozen before these calls; its seed pairs intentionally point back to the previously evaluated sample. [Raw responses](tier4-hint-tuning-responses.json) include exact prompts, outputs, scores, usage and metadata. Run `python -m conlang.verify_tier4_tuning` to regrade and reproduce the descriptive story-level comparisons without API calls. It also verifies the earlier sample; regrading cannot attest provider provenance. [Full design](NEXT-TIER-DYNAMIC-DESIGN.md)
