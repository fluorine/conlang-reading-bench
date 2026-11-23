# Conlang Reading Bench

[Explore the benchmark and results on GitHub Pages](https://fluorine.github.io/conlang-reading-bench/).

A small **conlang comprehension benchmark** for language models. Its research task is *machine reading comprehension in procedurally generated constructed languages under progressive grammatical disclosure*. Can a model read a new language, work out who gave what to whom, and track the result? Four short answers score an entire story. Generation and scoring run locally with Python 3.12 and its standard library.

**Stage 1 result.** On 24 paired, held-out stories, GPT‑4.1 mini scored **65.63%** and GPT‑4o mini scored **45.83%**. Both models fell below the planned English-control threshold during development. These are exploratory task results. The full two-model pilot used 408 calls and an estimated **$0.026** at the published token rates. [Pilot report](reports/PILOT.md) · [Raw responses](results) · [Machine-readable scores](reports/index.json)

**Follow-up comparison.** GPT-5.4 nano scored **46.88%** on the same reference stories, with **62.50%** on the English control. [Paired comparisons and reproduction commands](reports/GPT-5.4-nano.md)

**Luna follow-up.** GPT-6 Luna with low reasoning scored **98.61%** overall and **100.00%** on the English control. [Run settings and paired comparisons](reports/GPT-6-Luna-low.md)

**Tier 2 uses 48 four-transfer stories.** All four models ran both the minimal-clue and English control conditions. [Combined results and run details](reports/FOUR-TRANSFERS-FOLLOWUP.md)

**Tier 3 research** explores harder artificial grammar with formally checked answers and matched English controls. On the same 48 five-object questions, Luna medium and Sol low each scored **37.5%**, and Terra medium scored **83.3%**; all scored **100%** on English controls. The result is preliminary: a last-name shortcut scored 31.25%, the effort settings differ, and the stories share one grammar family. These runs are separate from the earlier published tiers. [Sol comparison](reports/SOL-LOW-COMPARISON.md) · [Paired comparison and replication](reports/TIER3-COMPARISON.md) · [Search history](reports/TIER3-SEARCH.md)

## Replicate the benchmark

### Copy a prompt for your AI agent

**Reproduce the published scores for free.** Paste this into an agent with Git and Python 3.12:

```text
Reproduce the Stage 1 pilot from https://github.com/fluorine/conlang-reading-bench at tag v0.1.0. Read AGENTS.md at that tag. Run the offline tests, regenerate the smoke suite, and regrade the saved responses. Compare your regenerated index against reports/index.json and recompute the paired held-out comparison. Report each model's headline and English scores, the difference in percentage points with its 95% interval, and whether the files match. Use only the saved responses. This task has a $0 API budget.
```

**Collect new responses.** Fill in the three bracketed fields before giving this prompt to an agent:

```text
Run the reference suite from https://github.com/fluorine/conlang-reading-bench at tag v0.1.0 using model [pinned model ID], effort [provider setting or default], and a total API budget of [USD amount]. Follow AGENTS.md. Check the offline fixture first, estimate the 96 calls using current rates, and proceed only if the estimate fits my budget. Save the raw answers and settings, score the bundle, and compare it with the matching published configuration if one exists. Report the English control, usage, cost, and bundle path. Prepare the result files locally so I can review them for a pull request.
```

### Run it yourself

With Git and Python 3.12 installed, paste these commands into a terminal. Regrading uses the standard library and needs no API key.

```sh
git clone --branch v0.1.0 --depth 1 https://github.com/fluorine/conlang-reading-bench.git
cd conlang-reading-bench
python -m unittest discover -s tests -v
python -m conlang generate --suite smoke --out .work/smoke
python -m conlang verify-results --index .work/regraded.json
python -c "from conlang.suite import read; assert read('.work/regraded.json') == read('reports/index.json'); print('Published score index reproduced')"
python -m conlang compare results/holdout2/gpt-4o-mini-2024-07-18.json results/holdout2/gpt-4.1-mini-2025-04-14.json
```

You should see six passing tests, eight regraded bundles, and the message `Published score index reproduced`. The final command should give GPT‑4.1 mini a **19.79 percentage-point lead** over GPT‑4o mini, with a 95% interval of **11.46 to 28.13 points**.

To collect fresh answers yourself, start with the free estimate below. The [replication guide](AGENTS.md#collect-an-independent-run) gives the budget-capped run command. The [submission instructions](AGENTS.md#submit-and-corroborate) explain how to link an independent rerun and open a results PR for GitHub to regrade.

```sh
python -m conlang estimate --suite reference --model gpt-4.1-mini-2025-04-14
```

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

## Research scope and roadmap

The pilot tests role interpretation, temporal order, and persistence of ownership in one regular grammar family. The language changes between items; the family and the public seed lists can become familiar. A held-out reference item is held out from this pilot's development phase. Future validation needs unseen families and fresh seeds. A targeted search found substantial precedent for the ingredients and no reviewed description of this exact combination. [Related-work review](RELATED_WORK.md)

- **Stage 1** ships the paired generator, verifier, explicit scoring protocol, two-model pilot, and offline regrading.
- **Next experiment** tests a clearer English control and checks whether a smaller set of clues still separates models. Freeze any revised prompts and scores as a new protocol and use fresh held-out worlds.
- **Adaptive disclosure** would stop after apparent success and verify it on a second, equivalent story. Compare cost, ranking stability, and guessing with the fixed-tier reference.
- **Broader coverage** would introduce held-out grammar families, then add narrative depth or irregular and fusional morphology one axis at a time. Keep changes that yield a reproducible distinction or lower the cost per reliable comparison.
