# Tier 4: three-object grammar (development)

This pilot keeps 30 transfers but reduces the number of objects from five to three and the number of unique fused endings from 30 to 18. Twelve fresh stories were frozen before model calls and checked for unique answers, suffix-blind ambiguity and independent full-grammar replay. Each request asks three end-of-story questions. Hint meanings are chosen by the existing seeded randomized-observed policy, not based on the answers.

| Fresh context | 1 meaning | 3 meanings | All 18 meanings |
|---|---:|---:|---:|
| Luna low, conlang | 8/36 (22.2%) | 9/36 (25.0%) | 35/36 (97.2%) |
| Disclosed-transfer tracker | 7/36 (19.4%) | 15/36 (41.7%) | 36/36 (100%) |
| English control | 36/36 (100%) | 36/36 (100%) | 36/36 (100%) |

The last-name shortcut scored 10/36 (27.8%); choosing the initial holder scored 5/36 (13.9%). Uniform choice among suffix-blind possible holders has **32.6% expected accuracy**. At one hint, Luna's +2.8-point advantage over the tracker has a descriptive 95% story-bootstrap interval of −13.9 to +22.2 points. The model is below the suffix-blind guessing expectation, so this is not a calibrated test despite its strong controls.

The run used 72 calls and cost approximately $0.03166 at the recorded token rates. No response was empty or capped; one one-hint and two three-hint outputs did not parse as answer arrays and were scored incorrect. [Raw responses](tier4-compact-dev-responses.json); reproduce all scores with `python -m conlang.verify_tier4_compact_dev`. Automated regrading does not attest provider provenance or replace human review.

## Role-only inventory follow-up

On the same 12 stories, we disclosed which endings mark givers and recipients, but not their object or reference context. The inventory is derived from the language table, not the answers, and independent full-grammar replay checks it. Luna scored **5/36 (13.9%)**, **21/36 (58.3%)**, and **36/36 (100%)** with one, three and all 18 full meanings. A role-aware shortcut that always chooses the last recipient scored **15/36 (41.7%)**, irrespective of hint stage. The one-hint model score is below this shortcut; the three-hint score is above the desired ceiling. These results are adaptive and do not calibrate a tier.

The 36 follow-up calls cost approximately $0.03037 at recorded token rates; no responses were empty or capped. No new English controls were run. See [raw responses](tier4-compact-roles-dev-responses.json) and reproduce scores and the role-aware baseline with `python -m conlang.verify_tier4_compact_roles`.

The next development check tests a different disclosure: a small, seeded list tells the model which object some endings refer to, while leaving role and context unstated. Its 2/4/18 object-only inventory sizes were chosen after inspecting shortcut performance on these same stories, so they are adaptive. It will be compared with a tracker that uses this new partial information. This uses the same stories and cannot substitute for independent confirmation.

The object-only follow-up scored **8/36 (22.2%)**, **13/36 (36.1%)**, and **36/36 (100%)** across the three stages. A tracker that uses the object-only inventories and assumes its last tracked holder is the giver scored 10/36, 15/36 and 36/36. Hence neither sparse stage beats this shortcut. The 36 calls cost approximately $0.02927 at recorded token rates; there were no empty or capped outputs and no new English controls. [Raw responses](tier4-compact-objects-dev-responses.json); reproduce with `python -m conlang.verify_tier4_compact_objects`.

The next [frozen development sample](../experiments/tier4-regular-dev.json) returns to five objects and 30 transfers but uses ten regular object-and-role suffixes rather than encoding the additional reference context. It is generated independently of model responses, and each answer must remain uniquely determined. This tests whether reducing arbitrary morphological distinctions improves discrimination while retaining a longer story. A successful development score would still require new stories and controls for confirmation.
