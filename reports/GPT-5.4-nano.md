# GPT-5.4 nano on the Stage 1 reference suite

GPT-5.4 nano scored **46.88%** on the same 24 held-out stories as GPT-4.1 mini (65.63%) and GPT-4o mini (45.83%). English control accuracy was **62.50%**. This follow-up used the two-transfer suite selected in the exploratory pilot.

| Configuration | Minimal clues | Glossary | Full grammar | Overall | English |
|---|---:|---:|---:|---:|---:|
| GPT-5.4 nano | 44.79% | 48.96% | 46.88% | 46.88% | 62.50% |

**Paired differences**, expressed as nano minus the comparison model, were -18.75 points (95% interval -27.43 to -10.76) against GPT-4.1 mini and 1.04 points (95% interval -9.03 to 11.11) against GPT-4o mini. The scorer resamples whole stories to preserve dependence between questions and clue levels. These are individual pairwise intervals across the published story set.

**Run settings.** The snapshot was `gpt-5.4-nano-2026-03-17`, with default effort (none), temperature zero, and a 64-token completion cap. The suite, questions and scoring rules match the original held-out runs. The 96 completed responses used 18,266 input tokens and 1,152 output tokens, with 0 reported reasoning tokens. Token usage gives an estimated list-price cost of $0.00509320. [Model and pricing](https://developers.openai.com/api/docs/models/gpt-5.4-nano) · [Raw bundle](../results/holdout2/gpt-5.4-nano-2026-03-17.json)

## Reproduce the comparison

From a checkout containing this follow-up, run the following offline commands.

```sh
python -m conlang verify-results --index .work/regraded.json
python -m conlang compare results/holdout2/gpt-4.1-mini-2025-04-14.json results/holdout2/gpt-5.4-nano-2026-03-17.json
python -m conlang compare results/holdout2/gpt-4o-mini-2024-07-18.json results/holdout2/gpt-5.4-nano-2026-03-17.json
```
