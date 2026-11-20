# Conlang Reading Bench

A small **conlang comprehension benchmark** for language models. Its research task is *machine reading comprehension in procedurally generated constructed languages under progressive grammatical disclosure*. Can a model read a new language, work out who gave what to whom, and track the result? Four short answers score an entire story. Generation and scoring run locally with Python 3.12 and its standard library.

**Stage 1 result.** On 24 paired, held-out stories, GPT‑4.1 mini scored **65.63%** and GPT‑4o mini scored **45.83%**. Both models fell below the planned English-control threshold during development. These are exploratory task results. The full two-model pilot used 408 calls and an estimated **$0.026** at the published token rates. [Pilot report](reports/PILOT.md) · [Raw responses](results) · [Machine-readable scores](reports/index.json)

## Try one story

Here is the first story from the smoke suite, with the sparse clues condensed. There are two objects, a coin and a key. Initial statements list the holder, predicate, and object. A transfer has four fixed positions and a suffix on each person's name. Only the current holder can give the object. The word **poma** means *gives*. The independent example **Ivy numa vema** means *Ivy starts with the coin*.

```text
Cy numa vema
Ada numa kato
Ada-ak kato Bo-es poma
Bo-ak kato Cy-es poma
```

Who received an object in the first transfer? Who held the coin just before the second transfer? Who holds the key at the end? Who holds the coin at the end?

<details><summary>Check the interpretation and answers</summary>

Cy starts with the coin, and Ada starts with the key. Ada gives the key to Bo. Bo gives it to Cy. The key changes hands twice while the coin stays put. The four answers are `["Bo","Cy","Cy","Cy"]`.

</details>

## How generation works

1. A manifest specifies the ordered world and language seeds and the transfer count. The simulator assigns two objects to three people, samples legal transfers, and saves an ownership snapshot after each event. The world seed and its manifest position control the people, events, and question choices. The language seed independently controls roots, role suffixes, and transfer order.
2. Two renderers express the same event history in English and the conlang. A finite checker reads the conlang text, applies the visible clues, and enumerates the possible role interpretations. Admission requires every legal interpretation to produce the simulator's four answers. The generator exports model prompts and evaluator data into separate directories.
3. Each model gets four fresh contexts per story. **Minimal** supplies the grammar family, one lexical clue, and one worked initial statement. **Glossary** adds every root meaning. **Grammar** adds the order and both role suffixes. **English** supplies the same story in plain English. The same four English questions follow each passage. Each tier is measured, so a later answer never receives feedback from an earlier one.

## What a percentage means

Each of the three conlang levels counts correct answers divided by scheduled questions. The headline is the arithmetic mean of those three percentages. A model scoring 50%, 75%, and 100% earns **75%**. The reference suite has 96 questions per level, giving 288 scored conlang answers and a separate 96-answer English control.

The scorer matches names by position after trimming whitespace and ignoring case. It accepts one JSON array, optionally inside a single Markdown code fence. Missing answer positions and invalid entries receive zero. Invalid JSON or an overlong array receives zero for the item. A missing model response makes the entire run incomplete. A format error returned by the model counts as an observed response. The report also shows how often all four answers are correct and the English minus full-grammar gap. Use English accuracy to interpret how much of a model difference can be attributed to the conlang.

## Reproduce the results for free

From the root of a clone, run the following commands. One model comparison resamples whole stories jointly, retaining the dependence between answers and tiers.

```sh
python -m unittest discover -s tests -v
python -m conlang generate --suite smoke --out .work/smoke
python -m conlang verify-results --index .work/regraded.json
python -m conlang score results/holdout2/gpt-4.1-mini-2025-04-14.json
python -m conlang compare results/holdout2/gpt-4o-mini-2024-07-18.json results/holdout2/gpt-4.1-mini-2025-04-14.json
```

To collect fresh responses, follow the [agent and contributor instructions](AGENTS.md). They cover corpus size, model effort, budget estimates, saved-response imports, and result pull requests.

## Research scope and roadmap

The pilot tests role interpretation, temporal order, and persistence of ownership in one regular grammar family. The language changes between items; the family and the public seed lists can become familiar. A held-out reference item is held out from this pilot's development phase. Future validation needs unseen families and fresh seeds. A targeted search found substantial precedent for the ingredients and no reviewed description of this exact combination. [Related-work review](RELATED_WORK.md)

- **Stage 1** ships the paired generator, verifier, explicit scoring protocol, two-model pilot, and offline regrading.
- **Next experiment** tests a clearer English control and checks whether a smaller set of clues still separates models. Freeze any revised prompts and scores as a new protocol and use fresh held-out worlds.
- **Adaptive disclosure** would stop after apparent success and verify it on a second, equivalent story. Compare cost, ranking stability, and guessing with the fixed-tier reference.
- **Broader coverage** would introduce held-out grammar families, then add narrative depth or irregular and fusional morphology one axis at a time. Keep changes that yield a reproducible distinction or lower the cost per reliable comparison.
