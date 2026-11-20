# Four-transfer follow-up

Luna's minimal-clue accuracy on the original stories was **85.42%** with the 512-token cap and **100.00%** with the 2,048-token cap. GPT-4.1 mini scored **35.42%** on those prompts. On fresh stories, Luna scored **100.00%** and GPT-4.1 mini scored **43.75%** with minimal clues.

The two suites each pair 24 minimal-clue prompts with 24 English prompts. The fresh suite samples new stories and languages from the same generator. The English version uses the same four questions. All Luna runs used low reasoning with the cap shown below. GPT-4.1 mini used its earlier temperature-zero configuration. The token caps refer to completions and include reasoning tokens where the model uses them.

Each requested question counts toward accuracy. A completed story has four valid names. “Answered only” uses just questions with a valid name. An empty response at the cap returned no visible answer and recorded the full completion allowance.

## Original four-transfer stories

| Configuration | Clues | Correct / 96 | Wrong answers | Unanswered | Completed stories / 24 | Empty at cap | Answered only |
|---|---|---:|---:|---:|---:|---:|---:|
| Luna low, 512 tokens | Minimal | 82 (85.42%) | 2 | 12 | 21 | 3 | 97.62% |
| Luna low, 512 tokens | English | 96 (100.00%) | 0 | 0 | 24 | 0 | 100.00% |
| Luna low, 2,048 tokens | Minimal | 96 (100.00%) | 0 | 0 | 24 | 0 | 100.00% |
| Luna low, 2,048 tokens | English | 95 (98.96%) | 1 | 0 | 24 | 0 | 98.96% |
| GPT-4.1 mini, 64 tokens | Minimal | 34 (35.42%) | 62 | 0 | 24 | 0 | 35.42% |
| GPT-4.1 mini, 64 tokens | English | 69 (71.88%) | 27 | 0 | 24 | 0 | 71.88% |

The last-person shortcut guesses the final name appearing in the passage for every question. It scored **28/96** with minimal clues and **47/96** in English.

## Fresh four-transfer stories

| Configuration | Clues | Correct / 96 | Wrong answers | Unanswered | Completed stories / 24 | Empty at cap | Answered only |
|---|---|---:|---:|---:|---:|---:|---:|
| Luna low, 2,048 tokens | Minimal | 96 (100.00%) | 0 | 0 | 24 | 0 | 100.00% |
| Luna low, 2,048 tokens | English | 96 (100.00%) | 0 | 0 | 24 | 0 | 100.00% |
| GPT-4.1 mini, 64 tokens | Minimal | 42 (43.75%) | 50 | 4 | 23 | 0 | 45.65% |
| GPT-4.1 mini, 64 tokens | English | 74 (77.08%) | 22 | 0 | 24 | 0 | 77.08% |

The last-person shortcut guesses the final name appearing in the passage for every question. It scored **37/96** with minimal clues and **37/96** in English.

Luna returned four valid names on every higher-cap request. Its longest completion used 793 tokens across the two suites, and its total cost on the original stories differed by less than $0.00002 between caps. GPT-4.1 mini beat the minimal-clue shortcut by 6 questions on the original stories and 5 on the fresh stories.

## Cost and reproducibility

The four follow-up runs collected 192 responses at an estimated list-price cost of **$0.02117**. Individual input, output, and reasoning-token totals follow.

| Suite | Configuration | Input tokens | Completion tokens | Reasoning tokens | Estimated USD |
|---|---|---:|---:|---:|---:|
| transfer4 | Luna low, 512 tokens | 8,209 | 11,390 | 10,577 | $0.00652 |
| transfer4 | Luna low, 2,048 tokens | 8,209 | 11,425 | 10,540 | $0.00653 |
| transfer4 | GPT-4.1 mini, 64 tokens | 8,257 | 492 | 0 | $0.00409 |
| transfer4fresh | Luna low, 2,048 tokens | 8,236 | 11,286 | 10,395 | $0.00647 |
| transfer4fresh | GPT-4.1 mini, 64 tokens | 8,284 | 478 | 0 | $0.00408 |

One run per configuration and seed set gives a descriptive comparison. Sampling can vary across reruns. The last-person shortcut checks one source of leakage. Both suites use the same regular grammar family.

Run these commands from a checkout containing the follow-up bundles to reproduce the counts and baselines.

```sh
python -m conlang.transfer_diagnostics transfer4 results/transfer4/gpt-6-luna-low.json results/transfer4/gpt-6-luna-low-2048.json results/transfer4/gpt-4.1-mini-2025-04-14.json
python -m conlang.transfer_diagnostics transfer4fresh results/transfer4fresh/gpt-6-luna-low-2048.json results/transfer4fresh/gpt-4.1-mini-2025-04-14.json
```
