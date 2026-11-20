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

The 18-transfer shared-ending run with none disclosed included two empty responses at the output cap; its 1/8 accuracy combines those failures with wrong answers. Its score should not be interpreted as a pure measure of comprehension. Increasing or decreasing the number of transfers is not necessarily monotonic in difficulty. All development cases were selected for formal answer uniqueness; the three- and higher-object probes additionally reject stories whose answer is determined after erasing all suffixes.

Two seeded generations of six sound-rule mutations each were also explored on one story. All 12 were correct. That search did not establish a generally difficult sound-change construction; its candidate rules and responses are in the archive.

The 24-transfer, one-disclosure candidate has been selected for a separately frozen 24-story fresh evaluation. Until that matched conlang and English run is complete, the development result is not a calibrated Tier 3 score.

## How the shared-ending probe works

Three objects start with known holders. Each later sentence records a legal transfer using two participant names with artificial endings in arbitrary order. Each ending represents exactly two combinations of the moved object, the participant's role, and who holds a reference object immediately beforehand. One ending and both its meanings are disclosed in the selected candidate; the other meanings must be inferred from the story. The final question asks who holds the coin.

The generator tracks the actual events, then independently enumerates legal histories and marker assignments consistent with the visible information. It rejects a story if the possible final answers differ or the search exceeds its limit. A separate check erases all endings and rejects stories whose answer remains uniquely determined. This is a finite formal guarantee under the specified rules, not a guarantee that the artificial grammar is natural or that humans find the instructions easy to understand. The meanings were designed abstractly; no claim is made that they are attested or unattested in natural languages.

## Reproduce and regrade

Run `python -m conlang.verify_tier3_search` to rebuild prompts, verify answer uniqueness and suffix-blind ambiguity, and rescore the archived responses. This checks the saved data and arithmetic; it does not attest that the provider produced the transcripts. `python -m unittest discover -s tests -v` checks the protocol and ambiguity rejection. CI runs these checks against the submitted code; the separate base-protocol regrader for official result PRs does not independently regrade these research probes.

For a new paid run, install Python 3.12, set `OPENAI_API_KEY` locally, check current provider rates, and use an empty output directory. For example:

```sh
python -m experiments.run_case_probes --manifest experiments/syncretic-24-one-clue-dev.json --out .work/my-probe --budget 0.20 --rates 0.1 0.5
```

The two rates are USD per million input and output tokens, and the budget covers a conservative upper bound for all remaining requests plus recorded completed costs. The runner sends only the visible prompt in a fresh context. It records new transcripts and usage; the provider's actual bill can differ. It creates a pending marker before each request and refuses to resume if a request may have been billed but did not complete locally. Reconcile such requests manually before proceeding; never silently delete a pending marker and retry as though no request occurred. Use a new output directory for an independent rerun, retain the repository commit and model settings, and do not expose API keys. These research files are not official suite submissions.
