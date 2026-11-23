# Tier 4: paired hint-policy development comparison

We ran Luna low on 12 fresh stories under two hint-selection policies, with the same underlying events, language and four questions. The regular policy orders observed endings randomly; the deferred policy initially withholds endings appearing on the final transfer of each queried object. Each story was required to pass the existing uniqueness and suffix-blind ambiguity checks under both policies before model calls. The two sets of hints differ, so this comparison combines the effects of hint content and selection; it does not isolate whether a model knows or exploits the policy. See the [offline policy audit](TIER4-HINT-POLICY-AUDIT.md).

| Fresh-context condition | 10 meanings | 20 meanings | 30 meanings |
|---|---:|---:|---:|
| Luna low, randomized | 21/48 (43.8%) | 42/48 (87.5%) | 48/48 (100%) |
| Luna low, deferred | 7/48 (14.6%) | 21/48 (43.8%) | 46/48 (95.8%) |
| Disclosed-transfer heuristic, randomized | 35/48 (72.9%) | 46/48 (95.8%) | 48/48 (100%) |
| Disclosed-transfer heuristic, deferred | 6/48 (12.5%) | 32/48 (66.7%) | 48/48 (100%) |
| English control | 48/48 (100%) | 47/48 (97.9%) | 47/48 (97.9%) |

English rows are independent requests with the same English text; the column names indicate corresponding attempts, not English hints. Each percentage is the fraction of 48 questions answered correctly. The last-name shortcut scored **11/48 (22.9%)**, the initial-holder rule **6/48 (12.5%)**, and uniform guessing among suffix-blind possible holders had **18.6% expected accuracy**. These baselines use the same story events and therefore apply to both policies.

Deferred minus randomized Luna accuracy was **−29.2 percentage points** at ten hints (95% story-bootstrap interval −43.8 to −14.6), **−43.8 points** at twenty (−68.8 to −18.8), and **−4.2 points** with the full grammar (−10.4 to 0.0). These intervals resample the twelve stories, not their four questions independently. The study is developmental; twelve stories, model sampling and selection of stories that work under both policies limit generalization. At ten hints, Luna is below the disclosed-transfer heuristic under randomized hints, and below the last-name rule under deferred hints. Neither is a calibrated tier suitable for ranking models.

The model was `gpt-6-luna` with `low` reasoning and an 8,192-token output cap. The paired runs made 108 requests: 72 randomized-policy and English, and 36 deferred-policy. None was empty or capped. Recorded token-valued costs were approximately **$0.03209** and **$0.02926**, respectively ($0.06135 total); provider billing can differ. The original prompt did not tell the model the deferred selection policy; knowing that policy is a separate condition that was not tested here.

The [randomized manifest](../experiments/tier4-paired-random.json), [deferred manifest](../experiments/tier4-paired-deferred.json), and corresponding [randomized and English](tier4-paired-random-responses.json) and [deferred](tier4-paired-deferred-responses.json) transcripts were retained. Run `python -m conlang.verify_tier4_paired` to rebuild prompts, independently replay fully disclosed stories, regrade answers, compute heuristics and reproduce the paired story-bootstrap intervals without API calls. Regenerate the manifests with `python -m experiments.make_tier4_paired_hints`. Regrading cannot attest provider provenance.

Future development should seek a hint policy that is independent of the answer and makes the model's result distinguishable from explicit-hint shortcuts; withholding based on final events introduces a documented correlation. A genuinely new candidate should be frozen before evaluation on another independently seeded sample. Human review of story clarity and broader baselines remain necessary.
