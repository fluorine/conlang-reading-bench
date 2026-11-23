# Tier 4: midpoint questions (development)

This variant asks who held each of four objects immediately after transfer 15 of a 30-transfer story. It uses the original seeded randomized-observed hint ordering, rather than withholding hints based on final answers. Later lines remain available to constrain the language. The checkpoint is fixed in advance, and the same questions are asked in English. The [eight stories](../experiments/tier4-checkpoint-dev.json) were selected for formally unique answers, a suffix-blind ambiguity check covering the whole story, and independent full-grammar replay. Hint counts were chosen after inspecting shortcut performance, so this is adaptive development rather than an independent confirmation.

| Fresh context | 1 meaning | 3 meanings | 30 meanings |
|---|---:|---:|---:|
| Luna low, conlang | 4/32 (12.5%) | 15/32 (46.9%) | 29/32 (90.6%) |
| Disclosed-transfer tracker up to checkpoint | 10/32 (31.25%) | 15/32 (46.9%) | 32/32 (100%) |
| Luna low, English control | 32/32 (100%) | 30/32 (93.8%) | 32/32 (100%) |

The English text is identical across columns; these are independent requests, not different English hints. A last-name shortcut using the last word of transfer 15 scored 6/32 (18.75%); always choosing the initial holder scored 7/32 (21.9%). Uniform choice among suffix-blind possible holders has 20.2% expected accuracy. With one meaning, Luna is below the hint-aware tracker; with three, it ties the tracker and is above the desired 40% ceiling. Thus this format is not yet calibrated.

The test made 48 calls, with no empty or capped responses, for approximately $0.02057 in recorded token-valued costs. [Raw responses](tier4-checkpoint-dev-responses.json) retain exact prompts, outputs and usage. Run `python -m conlang.verify_tier4_checkpoint_dev` to reconstruct the prompts, independently replay the disclosed grammar, regrade and recalculate baselines without API calls. These checks do not attest provider provenance or replace human review.

## Procedural guidance follow-up

On the same stories, we added a brief instruction reminding the model to use legal transfers, consistent suffix meanings and later constraints. The questions, clues and gold answers remained unchanged. The guided model scored **3/32 (9.4%)**, **9/32 (28.1%)**, and **31/32 (96.9%)** at one, three and 30 meanings, respectively. The hint-aware tracker still scored 10/32, 15/32 and 32/32. The follow-up used fresh conlang requests only, not new English controls; its 24 calls had no empty or capped responses and cost approximately $0.01797 in recorded token value. These are adaptive results, not evidence about untouched stories. [Raw guided responses](tier4-checkpoint-guide-dev-responses.json); regrade with `python -m conlang.verify_tier4_checkpoint_guide`.

## Structured work follow-up

We also allowed a JSON `work` field before the scored `answers` array, using the same stories and new English controls. Luna scored **5/32 (15.6%)**, **4/32 (12.5%)**, and **23/32 (71.9%)** at one, three and 30 meanings; the new English controls scored 32/32, 30/32 and 32/32. The model did not beat the hint-aware tracker at any stage, and even full disclosure scored below the earlier answer-only run. All 48 responses were valid JSON objects; five had empty answer arrays, none was capped or completely empty. Recorded token-valued cost was approximately $0.02296. [Raw responses](tier4-checkpoint-work-dev-responses.json); regrade with `python -m conlang.verify_tier4_checkpoint_work`.

These comparisons used the same eight stories and are adaptive; model sampling also varies between calls. Neither procedural guidance nor structured written work produced a useful calibrated setting. Further development must change the task or experimental procedure and test a candidate on untouched stories.

The next adaptive diagnostic asks each of the four questions in its own fresh model call, while retaining the same story, hint counts and answers. This isolates whether answering four at once hurts performance, at the cost of four requests per story and hint stage. Its four frozen manifests identify the focused target. The diagnostic does not collect new focused English controls; an independent confirmation would need those before claiming the result is calibrated.
