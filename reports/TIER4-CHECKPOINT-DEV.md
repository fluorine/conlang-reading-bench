# Tier 4: midpoint questions (development)

This variant asks who held each of four objects immediately after transfer 15 of a 30-transfer story. It uses the original seeded randomized-observed hint ordering, rather than withholding hints based on final answers. Later lines remain available to constrain the language. The checkpoint is fixed in advance, and the same questions are asked in English. The [eight stories](../experiments/tier4-checkpoint-dev.json) were selected for formally unique answers, a suffix-blind ambiguity check covering the whole story, and independent full-grammar replay. Hint counts were chosen after inspecting shortcut performance, so this is adaptive development rather than an independent confirmation.

| Fresh context | 1 meaning | 3 meanings | 30 meanings |
|---|---:|---:|---:|
| Luna low, conlang | 4/32 (12.5%) | 15/32 (46.9%) | 29/32 (90.6%) |
| Disclosed-transfer tracker up to checkpoint | 10/32 (31.25%) | 15/32 (46.9%) | 32/32 (100%) |
| Luna low, English control | 32/32 (100%) | 30/32 (93.8%) | 32/32 (100%) |

The English text is identical across columns; these are independent requests, not different English hints. A last-name shortcut using the last word of transfer 15 scored 6/32 (18.75%); always choosing the initial holder scored 7/32 (21.9%). Uniform choice among suffix-blind possible holders has 20.2% expected accuracy. With one meaning, Luna is below the hint-aware tracker; with three, it ties the tracker and is above the desired 40% ceiling. Thus this format is not yet calibrated.

The test made 48 calls, with no empty or capped responses, for approximately $0.02057 in recorded token-valued costs. [Raw responses](tier4-checkpoint-dev-responses.json) retain exact prompts, outputs and usage. Run `python -m conlang.verify_tier4_checkpoint_dev` to reconstruct the prompts, independently replay the disclosed grammar, regrade and recalculate baselines without API calls. These checks do not attest provider provenance or replace human review.

One exploratory follow-up will test whether explicit procedural guidance improves use of the available information on these same stories. Since the stories and results are already known, any such comparison is adaptive and cannot establish a final benchmark; a fresh confirmation remains necessary.
