# Tier 4: deferred final-transfer markers (development)

We tested an exploratory modification to the unique-marker grammar. The first ten disclosed markers are chosen from observed markers other than those on the final transfer of each questioned object. Later hints reveal the rest. This suppresses a heuristic that tracks directly disclosed transfers, but the policy itself is correlated with hidden story structure and may provide other shortcuts; it must not be treated as neutral random disclosure. Answers still pass the existing uniqueness search at the first hint level and an independent full-grammar replay.

The six stories and selection rules were [frozen before collection](../experiments/tier4-deferred-dev.json), but this design followed inspection of previous results and is developmental. The sample is too small for calibration.

| Fresh context | 10 hints | 20 hints | 30 hints |
|---|---:|---:|---:|
| Luna low, conlang | 2/24 (8.3%) | 10/24 (41.7%) | 23/24 (95.8%) |
| Luna low, matched English | 24/24 (100%) | 23/24 (95.8%) | 23/24 (95.8%) |
| Disclosed-transfer heuristic | 2/24 (8.3%) | 18/24 (75%) | 24/24 (100%) |

The same English text was asked three independent times; English does not receive conlang hints. At the initial level, last-name guessing scored **7/24 (29.2%)**, initial-holder guessing 2/24, and uniform guessing among suffix-blind possible holders had 19.4% expected accuracy. Luna was below last-name and tied the hint-aware heuristic. Thus the initial task is too hard to serve as a useful calibrated score; suppressing one heuristic did not establish meaningful comprehension. At 20 hints the hint-aware heuristic substantially outperformed Luna.

There were 36 calls, no empty or capped responses, and approximately $0.01644 in recorded token-valued cost. Responses, exact prompts and model settings are [available](tier4-deferred-dev-responses.json). Regrade with `python -m conlang.verify_tier4_deferred_dev`; no API requests are needed. Formal uniqueness and full-disclosure checks do not replace human review, and the results do not establish performance on new stories.
