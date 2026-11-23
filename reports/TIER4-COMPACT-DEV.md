# Tier 4: three-object grammar (development)

This pilot keeps 30 transfers but reduces the number of objects from five to three and the number of unique fused endings from 30 to 18. Twelve fresh stories were frozen before model calls and checked for unique answers, suffix-blind ambiguity and independent full-grammar replay. Each request asks three end-of-story questions. Hint meanings are chosen by the existing seeded randomized-observed policy, not based on the answers.

| Fresh context | 1 meaning | 3 meanings | All 18 meanings |
|---|---:|---:|---:|
| Luna low, conlang | 8/36 (22.2%) | 9/36 (25.0%) | 35/36 (97.2%) |
| Disclosed-transfer tracker | 7/36 (19.4%) | 15/36 (41.7%) | 36/36 (100%) |
| English control | 36/36 (100%) | 36/36 (100%) | 36/36 (100%) |

The last-name shortcut scored 10/36 (27.8%); choosing the initial holder scored 5/36 (13.9%). Uniform choice among suffix-blind possible holders has **32.6% expected accuracy**. At one hint, Luna's +2.8-point advantage over the tracker has a descriptive 95% story-bootstrap interval of −13.9 to +22.2 points. The model is below the suffix-blind guessing expectation, so this is not a calibrated test despite its strong controls.

The run used 72 calls and cost approximately $0.03166 at the recorded token rates. No response was empty or capped; one one-hint and two three-hint outputs did not parse as answer arrays and were scored incorrect. [Raw responses](tier4-compact-dev-responses.json); reproduce all scores with `python -m conlang.verify_tier4_compact_dev`. Automated regrading does not attest provider provenance or replace human review.

The next adaptive check adds a role-only inventory: it discloses which endings mark givers and recipients, but not their object or reference context. The inventory is derived from the language table, not the answers, and independent full-grammar replay checks its correctness. A new role-aware shortcut must be measured because that information can itself help a simple rule. The same stories will be reused, so any result requires fresh confirmation before calibration.
