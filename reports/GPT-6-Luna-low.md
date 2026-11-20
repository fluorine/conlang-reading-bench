# GPT-6 Luna with low reasoning

GPT-6 Luna scored **98.61%** overall on the published 24-story reference suite and **100.00%** on the English control. Accuracy by clue level was 98.96% with minimal clues, 97.92% with the glossary, 98.96% with full grammar.

The paired differences below are Luna minus each earlier configuration. The scorer resamples whole stories.

- GPT-4.1 mini — 32.99 percentage points (95% interval 26.39 to 39.58).
- GPT-4o mini — 52.78 percentage points (95% interval 45.83 to 60.07).
- GPT-5.4 nano — 51.74 percentage points (95% interval 44.44 to 59.38).

The model ID was `gpt-6-luna`, with `reasoning_effort=low`, a 512-token completion cap including reasoning, and provider-default sampling. The questions, prompts and scoring rules matched the earlier runs. The 96 responses used 18,266 input tokens and 17,022 completion tokens, including 15,284 reasoning tokens. Estimated list-price cost was $0.01034. [Model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna) · [Raw responses](../results/holdout2/gpt-6-luna-low.json)

Run `python -m conlang verify-results --index .work/regraded.json` to regrade the responses. For example, compare Luna with the earlier leading model using:

```sh
python -m conlang compare results/holdout2/gpt-4.1-mini-2025-04-14.json results/holdout2/gpt-6-luna-low.json
```
