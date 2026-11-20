# Stage 1 two-model pilot

**A two-transfer story separated the two configurations at a measured list-price cost of about half a cent per ten paired stories.** On 24 held-out stories GPT‑4.1 mini led by **19.79 percentage points**, with a paired story-bootstrap 95% interval of **11.46 to 28.13 points**. Both models also made mistakes in the English control. The observed difference combines language interpretation and ordinary story tracking.

| Pinned model | Minimal clues | Glossary | Full grammar | Headline | English control |
|---|---:|---:|---:|---:|---:|
| GPT‑4o mini, 2024-07-18 | 43.75% | 43.75% | 50.00% | 45.83% | 69.79% |
| GPT‑4.1 mini, 2025-04-14 | 48.96% | 69.79% | 78.13% | 65.63% | 84.38% |

Each cell for a single condition covers 96 questions. The all-four-correct rate on full grammar was 0/24 for GPT‑4o mini and 9/24 for GPT‑4.1 mini. The English minus full-grammar gap was 19.79 and 6.25 points, respectively. These results describe two model snapshots at default effort, temperature zero, and a 64-token completion cap. The public suite contains one regular grammar family and two object types.

## Development and selection

Twelve paired development worlds were evaluated with both two and three transfers, in all four conditions. The same twelve question-only prompts were sent once per model. For each form, those responses were evaluated against that form's gold answers. A second baseline always picked the last person mentioned in the conlang passage. Model comparisons used the same seed pairs and ordering.

The selection rule required a consistent direction in both six-story halves, at least 90% English accuracy for each model, and performance above both shortcuts for the stronger model. The two-transfer English scores were 66.67% and 83.33%. The three-transfer scores were 62.50% and 81.25%. **Neither candidate passed.** The shorter form therefore became the exploratory reference. The held-out interval measures variability across these stories and does not establish that this is the optimal or shortest possible language test. [Selection evidence](selection.json)

World seeds were selected to balance answer names within question positions across both candidate forms. At each position, a seeded sampler chose from 600 candidate worlds using existing answer frequencies. Language seeds were then drawn separately. Master seeds were 145 for development, 920 for held-out evaluation, and 238 for smoke. Initial ownership sentences always introduce the coin before the key, which supplies a potential positional shortcut. Treat the bootstrap interval as descriptive of this balanced set and test fresh rendering orders in future protocols.

## Scoring amendment before held-out evaluation

The first scorer accepted only bare JSON. GPT‑4o mini's development responses enclosed the answers in a Markdown code fence, causing a strict headline of 0% on both forms. We inspected the development transcripts and revised the scorer to accept one enclosing fence for every model. Content, answer order, and matching rules stayed identical. The original results are archived in `strict_development` in the selection file. Run `score --strict` on any saved bundle to audit the effect. Commit `5841776` froze the amended scorer, selection decision, and held-out manifest before either held-out run began. The generator and development prompts were frozen at `b813649`.

## Cost and reproducibility

The pilot completed 408 requests in 408 attempts, using 75,730 input and 5,256 output tokens. Reported reasoning tokens were zero. Development, question-only controls and held-out evaluation together cost **$0.02597135 at list price**, against a $10 ceiling. These figures use returned token counts and the dated rates recorded in each bundle. They are estimates of API charges and exclude taxes, credits and any account-specific pricing.

The two held-out runs cost $0.00367590 and $0.00883280. One story across all four conditions therefore cost about $0.000153 per GPT‑4o mini evaluation and $0.000368 per GPT‑4.1 mini evaluation. The paired reference suite took 192 calls. [GPT‑4o mini pricing](https://developers.openai.com/api/docs/models/gpt-4o-mini) · [GPT‑4.1 mini pricing](https://developers.openai.com/api/docs/models/gpt-4.1-mini)

The comparison uses 10,000 bootstrap samples of 24 story-level differences, retaining all three conlang tiers and four questions within a story. It measures sampling variation across generated items. Independent model sampling, new grammar families, and independent contributor replication remain separate questions. [Paired comparison](comparison.json) · [Full index](index.json) · [Raw bundles](../results)

Run `python -m conlang calibrate` to reproduce form selection and `python -m conlang compare` with the two reference bundles to reproduce the held-out interval. The next experiment should check why the short English control remains difficult and introduce a newly frozen held-out sample for any revised protocol.
