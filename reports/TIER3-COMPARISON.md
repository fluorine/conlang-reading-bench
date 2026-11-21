# Exploratory Tier 3: paired five-object comparison

GPT-6 Luna and GPT-6.1 Terra were each tested at **medium** reasoning effort on the same 48 constructed-language stories and their matched English versions. Each condition has one question per story. The test measures success at inferring and applying this particular artificial grammar while tracking object transfers. It is not a general measure of language comprehension, and these results are not directly comparable to the earlier two- and four-transfer tiers.

| Model and effort | Conlang: all 48 | English control | Original 24 | Fresh 24 |
|---|---:|---:|---:|---:|
| GPT-6 Luna (medium) | 18/48 (37.50%) | 48/48 (100%) | 9/24 (37.50%) | 9/24 (37.50%) |
| GPT-6.1 Terra (medium) | 40/48 (83.33%) | 48/48 (100%) | 18/24 (75.00%) | 22/24 (91.67%) |

Both models were correct on 16 stories, Terra alone on 24, Luna alone on two, and neither on six. Terra's paired advantage is **45.8 percentage points**, with a **29.2 to 62.5 percentage-point** 95% paired bootstrap interval, resampling stories within each 24-story set (10,000 samples, seed 492014). The interval describes sampling uncertainty for this synthetic generator and does not cover all sources of model or benchmark uncertainty. The individual 95% Wilson intervals are approximately **25.2–51.6%** for Luna and **70.4–91.3%** for Terra. Terra's 22/24 on the second set suggests this task may approach saturation for that configuration, but a small sample cannot establish a ceiling.

The English control checks whether the model can track the same events when stated in ordinary English; it does not measure conlang comprehension. All 192 calls completed without empty answers or output-cap failures. Accuracy is exact parsed-name correctness; failed, empty or malformed responses would count as wrong. Model aliases can change and a single sample from an API can vary. Equal provider-native effort labels do not imply equal internal compute.

## Shortcut baselines and limits

Across the same 48 stories, choosing the last name mentioned scores **15/48 (31.25%)**. Uniformly choosing among final holders possible after erasing suffixes has **18.8% expected accuracy**; choosing the alphabetically first such holder scores **5/48 (10.42%)**. The suffix-blind strategies ignore even the one disclosed marker meaning, so they are not exhaustive shortcut tests. The 48 stories are independent seeds within one grammar family, filtered to require a unique answer and an ambiguous suffix-blind outcome. Their sampling interval does not demonstrate transfer to other grammar families or natural languages. The original candidate was selected after adaptive development, while the second 24-story set was frozen before either model was run on it.

## Generation, execution and scoring

The generator starts five objects with known holders, simulates 18 legal transfers, and encodes the transferred object, a person's role and a state-dependent reference relation in shared suffixes. Each suffix represents two distinct combinations; one suffix and its two meanings are disclosed. A finite search enumerates legal histories and compatible suffix assignments, rejecting stories unless their visible information determines one final coin holder. A second search rejects stories where ignoring all suffixes already determines the answer. This verifies uniqueness under the implemented formal rules; it does not independently establish that a human finds the instructions clear or that the grammar resembles a natural language. [Detailed search history](TIER3-SEARCH.md)

Each request received only its visible prompt in a fresh context, with no tools, answer feedback or demonstrations. The OpenAI Chat Completions adapter requested `gpt-6-luna` or `gpt-6.1-terra`, `medium` reasoning, and a 16,384 completion-token limit, with no temperature specified. Model aliases and provider-returned identifiers are in the raw responses. The official [Terra model documentation](https://developers.openai.com/api/docs/models/gpt-6.1-terra) lists its supported settings and standard rates; its [AWS model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-6-1-terra.html) gives the October 26, 2026 launch date used on the release-date plot.

Completed calls total approximately **$0.17711 for Luna** and **$0.87956 for Terra**, or **$1.05667 combined**, valuing provider-reported token usage at the supplied standard rates rather than reconstructing an invoice or cache discounts. Two requests were interrupted locally with unknown provider outcomes and billing; each was retried, and both earlier attempts are retained with a combined maximum-cost reservation of approximately **$0.09164**. Those uncertain charges are not included in the completed-call valuation.

## Reproduce and corroborate

The frozen manifests are [`syncretic-five-object-holdout.json`](../experiments/syncretic-five-object-holdout.json) and [`syncretic-five-object-fresh2.json`](../experiments/syncretic-five-object-fresh2.json). [Raw responses and run metadata](tier3-comparison-responses.json) include the prompts, answers, provider model identifiers, usage, settings and uncertain attempts. Regrade without credentials or paid requests:

```sh
python -m unittest discover -s tests -v
python -m conlang.verify_tier3_comparison
python -m experiments.build_tier3_site
```

The comparison regrader checks manifest hashes, coverage, model and effort settings, prompt and gold regeneration, parsed answers, token-price arithmetic and the paired statistics. It cannot attest that the provider produced a transcript; CI runs the checker against the submitted revision. The site data is generated from the checked archive. For an independent rerun or another adapter, retain the exact prompts and settings, use fresh output files, disclose provenance and costs, and follow the budget and uncertain-request safeguards in [the search report](TIER3-SEARCH.md). Regrading saved answers is not an independent model run.
