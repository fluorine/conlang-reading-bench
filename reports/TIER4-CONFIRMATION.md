# Tier 4: independent ten-hint confirmation

We froze a new set of 12 stories before running Luna low. Each story has 30 transfers and four questions about final holders. The candidate, chosen after [adaptive tuning](TIER4-HINT-TUNING.md), discloses ten meanings of endings that actually occur in the story. Later stages reveal 20 and then all 30. The same questions are asked again without showing the model the correct answers.

| Condition | 10 meanings | 20 meanings | 30 meanings |
|---|---:|---:|---:|
| Fresh conlang context | 18/48 (37.5%) | 42/48 (87.5%) | 47/48 (97.9%) |
| Continued conversation, new hints | 17/48 (35.4%) | 44/48 (91.7%) | 47/48 (97.9%) |
| Continued conversation, no new hints | 14/48 (29.2%) | 13/48 (27.1%) | 13/48 (27.1%) |
| Fresh English control | 48/48 (100%) | 48/48 (100%) | 47/48 (97.9%) |
| Continued English control | 48/48 (100%) | 48/48 (100%) | 48/48 (100%) |

The no-new-hints condition repeats the initial information; the columns denote attempts, not additional meanings. English conditions use the same underlying events and questions, not conlang hints. Accuracy is the fraction of the 48 questions answered correctly in each condition.

The initial fresh score is below the 40% target, but choosing the last name mentioned scores **15/48 (31.25%)**. The paired difference is **+6.25 percentage points**, with a 95% bootstrap interval of **−12.5 to +22.9 points**, resampling stories rather than individual questions. Thus this sample does not establish that the model beats that shortcut. Uniform guessing among suffix-blind possible holders has 18.9% expected accuracy; choosing each object's initial holder scores 3/48 (6.25%). A low score alone does not establish useful measurement, so this is not yet a calibrated tier or a basis for ranking stronger models.

Fresh full disclosure improved over initial disclosure by 60.4 points (story bootstrap interval +39.6 to +81.2). On the last attempt, continued new hints exceeded repeated questions without new hints by 70.8 points (+54.2 to +85.4). These are exploratory comparisons, and a dozen stories cannot characterize the full space of possible stories. The full-hint English control also has one missed answer; controls need not be perfect to be reported.

The sample was generated with seed 430012, requiring at least 20 observed endings and formally determined answers; selection did not use model outputs. An independent decoder checks the fully disclosed text and gold answers, but formal checks do not replace human review. All 180 calls completed, with no empty or capped responses. Recorded token-valued cost was approximately **$0.09561** at the recorded rates; provider billing may differ. The model identifier was `gpt-6-luna`, reasoning effort `low`, with an 8,192-token output cap. Model aliases and sampling may change over time.

The [frozen manifest](../experiments/tier4-confirmation.json), [raw responses](tier4-confirmation-responses.json), and [generation and evaluation code](../conlang/tier4_dynamic.py) are available for inspection. Run `python -m conlang.verify_tier4_confirmation` from the repository root to reconstruct the prompts, independently audit answers, regrade saved outputs and reproduce the comparisons without API requests. Regrading checks arithmetic and consistency; it does not verify provider provenance.

Further development should improve separation from shortcuts while retaining unambiguous stories, then freeze and evaluate a new independent sample before making model comparisons. More stories and independently repeated runs would narrow uncertainty; changing hint counts after observing this sample would require another independent confirmation.
