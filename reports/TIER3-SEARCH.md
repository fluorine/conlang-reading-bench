# Tier 3 search: shared grammatical endings

These are exploratory one-question probes, **not official Tier 3 scores**. Their grammars, story lengths, and disclosed clues differ. They cannot be compared as if they were repeated runs of the same test. We selected variants after inspecting development outcomes; fresh stories from the same generator help measure overfitting to particular stories, but do not test transfer to different grammar families.

All listed model results use the `gpt-6-luna` alias at medium effort and independent contexts. Each conlang story has a matched English control describing the identical transfers and asking the identical question. Each accuracy is the fraction of stories with a correct, parsed answer; blank or malformed answers count as incorrect. English measures whether the model can track this story in familiar wording, not conlang comprehension. The alias may change, and the small samples are noisy.

The [raw response archive](tier3-search-responses.json) records prompts, model-returned identifiers, raw answers, token usage and estimated cost. Older development scripts did not record precise start timestamps or provider finish reasons, and do not independently prove provider provenance. Costs are token usage valued at the then-used list rates, not invoices. The 48-transfer and object-induction probes used a 16,384 completion-token limit; earlier probes and the evolutionary search used 8,192. Some reasoning responses consume most of this limit. The full earlier sound-change experiment is documented separately in [Single-question sound-change probe](SINGLE-PROBE.md).

## Development findings

| Construction | Conlang | English |
|---|---:|---:|
| Abstract state-dependent case, 12 transfers | 5/6 | 6/6 |
| Three contextual case classes, 12 transfers | 6/6 | 6/6 |
| Fully disclosed fused case, 12 transfers | 8/8 | 8/8 |
| Undisclosed fused case, 12 transfers | 7/8 | 8/8 |
| Undisclosed fused case, 24 transfers | 6/8 | 8/8 |
| Undisclosed fused case, 48 transfers | 6/6 | 6/6 |
| Unique fused markers, 3 objects, 18 transfers | 7/8 | 8/8 |
| Unique fused markers, 4 objects, 18 transfers | 7/8 | 8/8 |
| Unique fused markers, 5 objects, 18 transfers | 8/8 | 8/8 |
| Shared endings, none disclosed, 18 transfers | 1/8 | 8/8 |
| Shared endings, none disclosed, 12 transfers | 5/8 | 8/8 |
| Shared endings, three disclosed, 12 transfers | 6/8 | 8/8 |
| Shared endings, three disclosed, 18 transfers | 6/8 | 8/8 |
| Shared endings, one disclosed, 18 transfers | 6/8 | 8/8 |
| Shared endings, one disclosed, 24 transfers | 4/8 | 8/8 |
| Shared endings, five objects, one disclosed, 18 transfers | 3/8 | 8/8 |
| Shared endings, five objects, five disclosed, 18 transfers | 7/8 | 8/8 |

The 18-transfer shared-ending run with none disclosed included two empty responses at the output cap; its 1/8 accuracy combines those failures with wrong answers. Its score should not be interpreted as a pure measure of comprehension. Increasing or decreasing the number of transfers is not necessarily monotonic in difficulty. All development cases were selected for formal answer uniqueness; the three- and higher-object probes additionally reject stories whose answer is determined after erasing all suffixes.

Two seeded generations of six sound-rule mutations each were also explored on one story. All 12 were correct. That search did not establish a generally difficult sound-change construction; its candidate rules and responses are in the archive.

The 24-transfer, one-disclosure candidate was selected for a separately frozen 24-story fresh evaluation. On its development sample, a model-free heuristic that always chooses the last name mentioned also scores 4/8; a uniform random choice among holders still possible after erasing suffixes has expected accuracy 32.3%. The fresh evaluation below checks a new sample from the same generator.

## Fresh evaluation of the three-object candidate

Luna medium answered **14/24 (58.3%)** conlang questions and **24/24 (100%)** matched English controls correctly. The conlang score has a 95% Wilson interval of approximately **38.8–75.5%**; this is an interval for this generator and configuration, not a measure of overall model capability. Three of the 24 conlang responses exhausted the 16,384-token completion limit and were empty. Among the 21 that produced an answer, 14 were correct; this conditional rate is descriptive and must not replace the 14/24 score.

On these same fresh stories, the last-name heuristic scores **6/24 (25%)**, the first alphabetically sorted suffix-blind possibility scores **7/24 (29.2%)**, and a uniform random choice among suffix-blind possible holders has **33.3% expected accuracy**. The random baseline ignores the one disclosed meaning and is therefore not the strongest possible shortcut. These scores and the wide interval make this a promising but preliminary candidate, not proof of robust discrimination or the desired roughly 25% Luna calibration. Fresh stories share the development grammar family.

The 48 completed requests used approximately **$0.1200** at the stated rates. One additional request returned HTTP 520 without a usable response; the cause and any charge are unknown. Its retry is included among the 48 completed responses. The raw archive separately preserves that failed attempt and a **$0.00834** maximum-cost reservation, so $0.1200 is observed-usage valuation rather than a complete verified bill.

The three-object holdout manifest was committed at `6a23c2b`; the initial requests used runner revision `1d7b1f9`, with the failed request and remaining calls resumed using `b20ca64`. The change between these runner revisions added explicit recovery of uncertain attempts; it did not change the generated prompts.

## Five-object development candidate

The five-object variant scored **3/8 (37.5%)** on the conlang and **8/8** on its English control, with no completion-limit failures. A uniform random choice among suffix-blind possible holders has **17.9% expected accuracy**; the last-name heuristic scored **2/8**, and the alphabetical suffix-blind heuristic scored **1/8**. With five endings disclosed, another sample scored 7/8 with 8/8 English; because the stories differ, this is not a paired estimate of the effect of disclosing more grammar. The expanded language also increases the number of distinct marker meanings, not just story length.

### Fresh five-object evaluation

On the separately frozen 24-story one-disclosure sample, Luna medium scored **9/24 (37.5%)**, with **24/24 (100%)** on the English controls. All conlang responses completed within the 16,384-token cap. The 95% Wilson interval for the conlang percentage is approximately **21.2–57.3%**. The 48 completed calls used about **$0.08864** at the stated token rates. The manifest and runner were frozen at `43ac3b6` before the calls.

The suffix-blind uniform random baseline is **18.8% expected accuracy**. The alphabetical suffix-blind heuristic scores **5/24 (20.8%)**, and the last-name-mentioned heuristic scores **7/24 (29.2%)**. On paired stories, Luna and the last-name heuristic were both right on six; Luna alone was right on three, and the heuristic alone was right on one. The difference is too small and the sample too limited to establish a reliable advantage over this shortcut. The uniform baseline also ignores the disclosed ending.

This is a **preliminary candidate** in the intended low-score range with a strong English control and no capped outputs. It is not yet an established Tier 3 calibration: the interval is wide, the difference from the strongest checked shortcut is small, and fresh stories use the same grammar family. A subsequent [paired comparison](TIER3-COMPARISON.md) adds Terra and another 24 fresh stories. Additional shortcut checks and grammar families are still needed before making broad claims about model rankings or general language comprehension. Keep these research results distinct from the earlier official tier scores.

## How the shared-ending probe works

Three objects start with known holders. Each later sentence records a legal transfer using two participant names with artificial endings in arbitrary order. Each ending represents exactly two combinations of the moved object, the participant's role, and who holds a reference object immediately beforehand. One ending and both its meanings are disclosed in the selected candidate; the other meanings must be inferred from the story. The final question asks who holds the coin.

The five-object variant applies the same rules to five tracked objects; the key remains the reference except when the key itself moves, when the book is used. Its complete set of possible object, context and role meanings is larger.

The generator tracks the actual events, then independently enumerates legal histories and marker assignments consistent with the visible information. It rejects a story if the possible final answers differ or the search exceeds its limit. A separate check erases all endings and rejects stories whose answer remains uniquely determined. This is a finite formal guarantee under the specified rules, not a guarantee that the artificial grammar is natural or that humans find the instructions easy to understand. The meanings were designed abstractly; no claim is made that they are attested or unattested in natural languages.

## Reproduce and regrade

Run `python -m conlang.verify_tier3_search` to rebuild prompts, verify answer uniqueness and suffix-blind ambiguity, and rescore the archived responses. This checks the saved data and arithmetic; it does not attest that the provider produced the transcripts. `python -m unittest discover -s tests -v` checks the protocol and ambiguity rejection. CI runs these checks against the submitted code; the separate base-protocol regrader for official result PRs does not independently regrade these research probes.

For a new paid run, install Python 3.12, set `OPENAI_API_KEY` locally, check current provider rates, and use an empty output directory. For example:

```sh
python -m experiments.run_case_probes --manifest experiments/syncretic-24-one-clue-dev.json --out .work/my-probe --budget 0.20 --rates 0.1 0.5
```

The two rates are USD per million input and output tokens, and the budget covers a conservative upper bound for all selected requests plus recorded completed costs. By default all remaining prompts are selected; `--max-new-requests N` permits a smaller batch, and a later invocation with the same directory and configuration can continue it. A budget applies to that directory, so account separately for other runs and uncertain charges. The runner sends only the visible prompt in a fresh context. It records new transcripts and usage; the provider's actual bill can differ. It creates a pending marker before each request and refuses to resume if a request may have been billed but did not complete locally. Reconcile such requests manually, or explicitly pass `--retry-uncertain`: this preserves the earlier attempt under `uncertain/` and reserves its full estimated cost as well as the retry before proceeding. Never silently delete a pending marker and retry as though no request occurred. Use a new output directory for an independent rerun, retain the repository commit and model settings, and do not expose API keys. These research files are not official suite submissions.

To ask an agent to corroborate the saved evidence without paid calls, use:

> Clone https://github.com/fluorine/conlang-reading-bench and read `reports/TIER3-SEARCH.md`. Record the checked-out commit, run the unit tests and `python -m conlang.verify_tier3_search`, then report each development accuracy, shortcut baseline, incomplete or capped response, and any verification failure. Explain that regrading saved answers is not a new independent model run. Do not send API requests or expose credentials.
