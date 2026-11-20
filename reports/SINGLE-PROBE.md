# Single-question sound-change probe

The experiment holds one story and one question fixed while adding reversible rules to a generated language. GPT-6 Luna at medium effort answered levels 0–4 correctly. At level 5 it exhausted the 4,096-token limit without an answer. A separate 8,192-token retry was correct. It then answered levels 6–23 correctly at the 8,192-token cap and gave an incorrect answer at level 24.

The original level-12 run had an inactive rule. The generator was corrected and levels 12–24 were run again with each rule applying to at least one transfer. The earlier result is retained in the raw data as development history. The transformations are artificial repeated vowel rotations. Their difficulty does not establish difficulty for natural linguistic evolution.

Six new stories with the 24-rule version and the same one-question format were evaluated alongside six matched English controls. Luna answered all six conlang questions and all six English questions correctly. The one incorrect development answer has not replicated on this small validation sample. The model alias and inference sampling may change over time.

The 39 requests cost about $0.04627 at list price, including the failed capped response, the retry, and both versions of level 12. Completion limits, output tokens, prompts, model responses, correct answers and per-request costs are preserved in [the raw bundle](single-probe-responses.json). The 24-rule validation source was frozen before evaluation.

Run `python -m conlang.verify_single_probe` to regenerate the prompts, verify the reversible sound transformations and recheck the saved answers. The checker preserves the original inactive-rule level-12 response as historical evidence. No final Tier 3 is selected from this experiment.
