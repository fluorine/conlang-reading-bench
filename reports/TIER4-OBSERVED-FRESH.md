# Tier 4 observed-marker sample: Luna low

This is an independently seeded **research sample**, not an official tier or a general measure of comprehension. Twelve stories each contain 30 transfers and four final-holder questions. GPT-6 Luna with low reasoning answered the same questions through three stages, with one, five and then all 30 unique suffix meanings disclosed. Early hints were chosen from endings that actually appear in the story. The structural grammar rules were visible throughout. The 12 stories were selected from a frozen seed using answerability checks, before model responses; they use the same artificial grammar family as development.

| Condition | One suffix | Five suffixes | All 30 suffixes |
|---|---:|---:|---:|
| Fresh context: conlang and cumulative hints | 11/48 (22.92%) | 12/48 (25.00%) | 47/48 (97.92%) |
| Continued conversation: cumulative hints | 6/48 (12.50%) | 9/48 (18.75%) | 48/48 (100%) |
| Continued conversation: **no new hints** | 10/48 (20.83%) | 10/48 (20.83%) | 12/48 (25.00%) |
| Fresh context: English control | 47/48 (97.92%) | 48/48 (100%) | 48/48 (100%) |
| Continued conversation: English, no new hints | 48/48 (100%) | 48/48 (100%) | 48/48 (100%) |

The same questions recur at each stage. Fresh contexts contain the story and cumulative hints independently; continued conversations retain the model's prior answers and add either new hints or a no-new-hint repeat. No condition gives correct answers or feedback. English renders the same events and questions. Each score is the percentage of individual answers correct; malformed or missing answers count as wrong. Multiple questions in the same story are correlated.

The initial fresh score is below the requested 40%, but the **last-name shortcut scores 12/48 (25%)**, the initial-holder shortcut **6/48 (12.5%)**, and uniform guessing among suffix-blind possible holders has **18.1% expected accuracy**. Fresh initial accuracy minus the last-name shortcut is **−2.1 percentage points**, with a **−18.8 to +16.7 point** 95% story-bootstrap interval. This does not establish a reliable advantage over that shortcut, so the initial stage is **not yet a well-calibrated leaderboard test**.

Full disclosure is more informative in this sample. Fresh full-hint accuracy minus fresh initial accuracy is **+75.0 points**, with a **+62.5 to +87.5 point** 95% story-bootstrap interval. At the final stage, continued hints exceed the separate continued no-new-hint condition by **+75.0 points** (**+62.5 to +85.4**). Intervals resample whole stories 10,000 times, preserving within-story question dependence. These are exploratory comparisons with only 12 stories; the analysis was implemented while the run was in progress, not preregistered before all responses. The intervals do not capture all model sampling or grammar-family uncertainty. Full hints reveal the complete artificial suffix table, so the gain measures the combined effect of much more grammar information and may still include ordinary event-tracking effort.

The generator rejects any story if the least-disclosed stage leaves any of the four answers ambiguous, if suffix-free reading alone determines an answer, or if the search limit is exceeded. Later hints are cumulative. A separately implemented parser independently replays each fully disclosed text and checks its four final holders. This verifies the stated formal rules, not human clarity, naturalness, or freedom from every shortcut. The independent replay was added during the run; the generator and sample were frozen first.

All **180 calls** completed without empty or capped responses. Provider-reported token usage valued at the recorded standard rates is approximately **$0.08655**; this is an estimate, not an invoice. [Raw responses](tier4-observed-fresh-responses.json) contain the exact messages, outputs and usage. The [manifest](../experiments/tier4-observed-fresh.json) and generation protocol were committed before the requests. Regrade without paid calls:

```sh
python -m unittest discover -s tests -v
python -m conlang.verify_tier4_observed
```

The next useful investigation is to test intermediate hint levels and alternative question types on a new development set, then freeze a fresh confirmation sample. Do not choose a level solely because it produces a low model score; it should also outperform sensible shortcuts and preserve unambiguous answers. Stronger-model comparisons should wait until those conditions are met. [Earlier development runs](TIER4-DYNAMIC-DEV.md) · [Design and limitations](NEXT-TIER-DYNAMIC-DESIGN.md)
