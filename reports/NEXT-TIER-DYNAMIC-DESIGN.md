# Proposed next tier: progressive hints on a longer story

**Status: development prototype.** A frozen four-story sample uses 30 transfers, four final-holder questions, and three stages revealing 1, 5 and 15 suffix meanings. Each suffix has two possible meanings. The grammar family and structural rules are given throughout; "minimal" means one disclosed suffix, not an absence of grammar information. The prototype is not an official tier or a calibrated benchmark. Its scores form a new comparison group rather than being mixed with earlier tiers.

## Core task

1. Generate a longer story and its complete event history from a seed. Ask several questions about that same story, covering different events, entities and kinds of inference. Generate the questions and gold answers from the history before calling a model.
2. Show the story and questions with minimal initial clues. Then progressively reveal a predeclared sequence of hints, such as word meanings, role markings, grammatical patterns or worked examples. Ask the same questions at each stage; provide no correct answers or feedback.
3. Score every stage separately as **correct answers divided by questions asked**, including invalid or missing responses as incorrect. Show the resulting accuracy curve and English-control score. The number of calls, story length, question count, hints, model effort, output cap and measured cost must accompany it.

The story and questions remain fixed across hint stages. Hints may explain the language but must not reveal answers or events that are absent from the story. Use multiple independent stories and language seeds: many questions about one story are correlated and do not replace multiple independent stories.

## Separate hint effects from memory and practice

Run two explicitly labeled conditions on the same story and questions:

- **Fresh context:** each stage receives the story, the cumulative hints and the questions in a new context. This isolates the information available at that stage from the model's earlier answers.
- **Continued context:** the model is asked again in the same conversation as hints accumulate. Record the full prior conversation and all answers. This measures the combined effects of hints, memory, repetition and any anchoring on its own earlier responses.

Neither condition gets answer feedback. Their results are not interchangeable. Compare hint types using matched stories, question sets, hint budgets and disclosure stages; randomize or counterbalance hint order across stories. Include a no-new-hint repeat in the continued-context condition to estimate changes caused by repetition alone. An additional, counterbalanced set of comparable new questions can help test whether gains transfer beyond the repeated questions. A same-length neutral-text control can help distinguish useful clues from added context, but cannot by itself equalize the information content of different hints.

## Answerability and scoring

The generator must preserve a machine-checkable event history and reject contradictions or missing information. At each hint stage, a verifier should enumerate the answers consistent with the visible story and clues. If a question has multiple possible answers at an early stage, do not call a single hidden answer objectively identifiable. Either exclude it from that stage's uniquely answerable accuracy and report the denominator, or use a separately specified set-valued/abstention task. Report how many questions are uniquely answerable at every stage. Avoid hints that simply encode the answer.

Keep **story generation, model execution and scoring** separate. Freeze seeds, questions, hint order and prompts before the model run. Store every raw response and stage, then score it with a versioned deterministic scorer. Check that the matched English control asks the same questions about the same events. Record cap failures and cost separately from wrong completed answers; use enough output tokens for the selected number of answers.

## Measuring efficiency and reliability

- Report stage accuracy and changes between adjacent stages, with uncertainty calculated by resampling **stories**, not treating questions about the same story as independent.
- Report per-question and per-story outcomes, the number of unambiguously answerable questions, and whether a correct response was retained or changed at the next stage.
- Compare no-language and shallow-pattern baselines, including last-mentioned entities where applicable. Report a random or suffix-blind baseline where it is defined; it may not be the strongest shortcut.
- Vary story length and hint type in separate, predeclared matched comparisons. A long story can also test working memory and ordinary event tracking, so use the paired English control and avoid attributing every failure to the invented language.
- Estimate worst-case spend before each run. Repeatedly sending the whole story may be costly; measure actual token usage and any provider-reported cache discounts. Caching is an execution optimization, not permission to change the visible prompt.

## Suggested first experiment

Start with a small development sample of several seeded stories, one long-story length, a fixed handful of questions and three disclosure stages: minimal clues, a glossary, and explicit grammar. Confirm answerability and output format locally, then run both fresh-context and continued-context variants on one affordable model with matched English controls. Choose or revise the protocol using development data; freeze a new held-out sample before comparing models. Only promote it to a numbered tier once the questions, ambiguity checks, baselines, scoring and costs are reproducible.

The current prototype explores a different three-stage sequence: it keeps the structural rules visible and increases the number of disclosed suffix meanings from one to five to fifteen. Its frozen manifest is [`tier4-dynamic-dev.json`](../experiments/tier4-dynamic-dev.json). It includes fresh-context hints, continued-context hints, a continued-context no-new-hint repeat, and both fresh and continued English controls. The runner is `python -m experiments.run_tier4_probes`; it uses a hard bundle budget and records every request. Four stories are an economical diagnostic, not sufficient evidence of calibration. A human review and an independently seeded holdout remain necessary.
