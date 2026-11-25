# Proposed Tier 5: progressive rule disclosure over a richer grammar

**Status: generator and offline checks built.** No runner, manifests or model runs exist yet. Tier 5 will be a new comparison group. Do not mix its scores with earlier tiers.

## Why a new tier

Tier 4 zero-hint is near saturation for the strongest models. With the final-array regrade, Terra medium scores 99.5% and Luna medium scores 91.7%. Tier 4 has one grammar family: a fixed role order with a few suffix meanings to infer. It cannot show *which* linguistic skill a model lacks. It also cannot show *how much* help a model needs.

Tier 5 changes the question. Earlier tiers ask "can the model read this language?" Tier 5 asks "**how many grammar rules must we reveal before the model reads this language, and which rules does it need?**"

## Core idea

1. Generate a story in a conlang. The grammar uses several real linguistic phenomena: case, noun-class agreement, declension, word order, tense, negation, irrealis and anaphora.
2. Always show the lexicon (the word stems and their meanings) and the **grammar family**. The family names the feature types, for example "the verb has a tense suffix; one tense marks an event that happened just before the line above". It never gives their values, for example which suffix is that tense.
3. Reveal one **rule card** at each stage. A card gives the value of one feature. Ask the same questions at each stage. Give no feedback.
4. Score each stage. A model with more linguistic capacity needs fewer rules before its answers become correct and stay correct.

The design target is a **probe model that scores between 10% and 90%**. Then the tier has room for comparison on both sides: it is not too hard and not too easy. The [difficulty target](#difficulty-target-10-to-90) section defines this, and the [calibration gates](#calibration-gates) enforce it.

The test is **relativistic**. The main result compares models on the same stories, the same stages and the same denominators. It does not claim an absolute ceiling. The verifier reports which questions a perfect reader could answer at each stage (see [Answerability](#answerability)).

## Grammar modules

Each module is one linguistic phenomenon with one rule card. A language seed samples the value of each module.

| Module | What the seed samples | What the model must do without the card |
|---|---|---|
| **Case** | Two case suffixes on names: one marks the agent (who gives or takes), the other marks the other person. | Infer which suffix marks the agent. Use the rule "only the holder can give". |
| **Declension** (part of the case card) | The case meaning depends on noun class. The same two suffixes have opposite meanings in different classes. | Learn the classes first, then read case per class. |
| **Word order** | A fixed order of agent, other person, object and verb. Or free order with the verb first or last. | Do not use position as a role cue when order is free. |
| **Agreement** | Two or three noun classes over the names. A verb prefix agrees with the class of the agent or of the other person. | Infer the classes and the agreement target. Use them to read declined case. |
| **Tense** | A past suffix and a pluperfect suffix. A pluperfect line happened just before the line above it, so the text is not in chronological order. | Rebuild the true event order. |
| **Negation** | A particle that marks an event that did not happen. | Exclude these events from the history. |
| **Irrealis** | A second particle that marks an event that was only reported. | Exclude these events as well. A third particle has no meaning. |
| **Anaphora** | One pronoun for each class. A pronoun refers to the most recently mentioned person of its class. | Resolve the pronoun through the class. |

The lexicon has two verbs: *give* (the agent loses the object) and *take* (the agent gains the object). This lexical role inversion has no card, because the lexicon gives it. It is tagged in the question analysis.

Changes from the first draft:
- **Ergative alignment is dropped.** All events are transfers with two persons. Alignment only shows with intransitive verbs, so it cannot be seen here. Declension takes its place as the case-ambiguity mechanism.
- **Negation and irrealis are particles**, not verb suffixes. With one verb suffix slot, the second card of tense and negation gave no new information. Separate particles, plus one particle with no meaning, keep each card informative.

### Example: L4 stage 0 (from the generator)

```text
Word meanings: kama = coin; ripa = key; poma = book; kaki = give; mima = take; nuto = hold.

Dee kama nuto
Bo ripa nuto
Cy poma nuto
ga Dee-ul Bo-ul ripa pe-mima-pu
te-ko kama Ada-ko so-mima-pu
nu Ada-ul kama Eli-ko na-mima-pu
...
```

## Disclosure ladder

One card per enabled module. A level with *n* modules has *n* + 1 stages, from stage 0 (no cards) to stage *n* (all cards). L1 has 5 stages. L4 and L5 have 8.

**Card order.** Each level has four orders: four rotations of one seeded base order, used as a Latin square. Story *i* gets order *i* mod 4. Every model sees the same order for the same story. This keeps model comparisons paired, and it averages out the effect of one fixed order.

**Card content.** A card states a rule. It never names an event or an answer. The agreement card lists the names in each class, because class membership is lexical information about the names.

## Questions

Each story has six questions. Answers are names. The generator selects them from a pool of 21 candidates:

- Who holds the X at the end?
- Who was the first person to receive the X?
- Who had the X just before its final transfer?
- Who held the X just before the final transfer of the Y?
- Who held the X just after the first transfer of the Y?

**Load-bearing check.** For each candidate, the generator reads the story again with one module ignored, for example with negated events counted as real or with the text taken in narrative order. A question is tagged with every module that changes its answer. The selection must cover every load-bearing module of the level, or the story is rejected. Then it prefers questions that need tense, negation, irrealis, anaphora or declension. No name may answer more than two of the six questions.

The tags make the per-module profile possible.

The scorer is `conlang.tier5.score`. It uses `parse_final_answer` (`final-array-1.0`) with six items, so a model can reason before its final array. Record bare-JSON compliance as a separate number.

## Answerability

At each stage, the verifier (`conlang/tier5_verify.py`) enumerates every grammar consistent with three inputs: the visible text, the revealed cards and the holder rule. It collects each question's answers across these grammars. A question with one answer is *uniquely answerable* at that stage. A search that passes its node cap marks the stage *unknown*.

**Offline result:** 97.6%–100% of questions are uniquely answerable already at stage 0, at every level. The holder rule is enough information to recover the grammar in principle. A unit test confirms that the verifier does report ambiguity when it exists.

This changes what the cards measure. A card does not add missing information. It removes inference work. The tier measures how much explicit help a model needs to do grammar induction that is possible in principle. This is the Tier 4 result in a richer grammar: zero hints were enough for the strongest models. The relativistic comparison stays valid, because every model has the same stories and denominators.

Report two numbers for each stage:

1. **Raw accuracy** = correct / all questions. This is the main number.
2. **Answerable accuracy** = correct / uniquely answerable questions. Offline, this is almost the same as raw accuracy.

## Metrics

| Metric | Definition | Use |
|---|---|---|
| **Disclosure capacity score (DCS)** | Mean raw accuracy over all stages of the level (normalized area under the curve). | Main ranking number. Higher is better. |
| **Rules to solve (RTS)** | For each story, the first stage *k* where all six answers are correct at *k* and at every later stage. If this never happens, the value is the number of stages (censored). | Median and survival curve. Lower is better. |
| **Module profile** | Accuracy on questions tagged with a module, before and after that module's card. | Shows *which* linguistic skill is missing. |
| **Retention** | Share of correct answers at stage *k* that stay correct at *k*+1. | Measures stability. A guessing model flips often. |
| **English gap** | English accuracy minus final-stage accuracy. | Separates language skill from event tracking. |

**Uncertainty.** Bootstrap over stories, not questions. Model comparisons are paired by story: report the paired DCS difference with a 95% interval and the per-story win rate.

**Baselines.** Five readers use only visible information. They do not read cards, so their score is the same at every stage.

| Reader | Rule |
|---|---|
| `last_name`, `first_name`, `most_frequent` | Give one name for every question. |
| `english_order` | The first person in a line is the agent. Read in text order, count every event, and resolve a pronoun to the last person. |
| `suffix_blind` | Like `english_order`, but swap the two persons when the holder rule requires it. |

## Difficulty target: 10 to 90

A score near 0% or near 100% tells us little: the models cannot be separated there. Tier 5 must put its probe model inside the band, with margin.

**Probe model.** Claude Haiku 5.5 low. It is cheap (a 48-story run costs about $0.60), and its earlier scores are in the middle of the field (88% on Tier 1, 44% on Tier 3). One probe keeps calibration cheap and repeatable.

**Target band on DCS**:

| Band | Probe DCS | Meaning |
|---|---|---|
| Hard limit | 10%–90% | Outside this band, the tier fails calibration. |
| Tuning target | 30%–70% on dev | Margin for noise from a small dev sample and for stronger and weaker models. |
| Ideal | about 50% | Equal room above and below. |

Two more conditions make the band meaningful:

- **The ladder must matter.** Probe accuracy at the final stage must be at least 30 points above stage 0. If the cards do not change the score, the tier measures something other than rule learning.
- **The band must hold at both ends of the field.** Report DCS for the strongest model (now Terra medium) and the weakest model (now Luna low). The strongest should stay below 90% and the weakest above 10%. This is a check, not a gate: a failure here is reported, and it starts a new difficulty level. It does not invalidate the probe calibration.

### Difficulty levels

The levels are defined in `conlang/tier5_grammar.py`. From one level to the next, no knob gets easier.

| Knob | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| Modules (cards) | case, order, tense, negation | + agreement | + irrealis | + anaphora | same as L4 |
| Transfers per story | 12 | 16 | 20 | 25 | 30 |
| Declension | no | no | yes | yes | yes |
| Distractor events (negated or irrealis) | 1 | 2 | 3 | 4 | 5 |
| Out-of-order share of events | 10% | 17% | 25% | 32% | 40% |
| People / noun classes | 4 / – | 4 / 2 | 5 / 2 | 6 / 3 | 6 / 3 |
| Word order | fixed | fixed | free | free | free |

The levels were fixed before the first model call. Do not tune knobs one by one on model results: that overfits the tier to the probe.

### Tuning procedure

1. Generate 8 dev stories at each level, L1 to L5. Use dev seeds only.
2. Run the probe on all five levels: 272 conlang calls and 40 English calls, about $0.50 at most.
3. Pick the level with probe DCS closest to 50% and inside 30%–70%. Only levels that pass gate 1 are eligible. If no level is inside the band, add a level between the two nearest ones and repeat steps 1–3 for that level only.
4. Freeze the level, prompts, card orders and scorer.
5. Make a new held-out manifest of 48 stories with fresh seeds. Run the probe. Its DCS must be in 10%–90%, and the final-stage minus stage-0 gap must be at least 30 points.
6. If step 5 fails, do not tune on the held-out stories. Go back to step 1, change the level, and make a **new** held-out manifest.

## Protocol

- **Fresh context only in v1.** Each stage is one user message in a new context, with no system prompt and no tools. This matches the earlier runs. Continued context is a v2 condition.
- **Full ladder in v1.** Run every stage. Do not stop early when a model succeeds. DCS needs every stage, and the curve may not be monotonic. When the dev data shows monotonic curves, consider adaptive stopping (stop after two passed stages in sequence) to cut cost.
- **One output cap for all providers.** Use 32,768 tokens and record each request that reaches the cap. Sonnet high reached an 8,192 cap on 30 of 48 Tier 3 requests, which made that run hard to interpret. The dev sweep used 16,384, and Haiku low reached it on 7 of 312 requests. Haiku returns its thinking as omitted blocks, so a capped reply has no text and scores zero. At 32,768, no held-out request reached the cap.
- **Calls per story:** one per stage and one English control. At L4 and L5 this is 9 calls.

## Implementation status

| Step | Files | Status |
|---|---|---|
| 1. Levels, languages, cards, family text | `conlang/tier5_grammar.py` | Done |
| 2. Events, narration, rendering, questions, ablated readers | `conlang/tier5_world.py` | Done |
| 3. Verifier | `conlang/tier5_verify.py` | Done |
| 4. Builder, baselines, scorer | `conlang/tier5.py` | Done |
| 5. Offline checks | `conlang/verify_tier5_offline.py`, `tests/test_tier5.py` | Done |
| 6. Runner | `experiments/run_tier5_probes.py` | Done. Uses `conlang/provider.py`, a hard budget with per-request reservations, resume, and `--estimate`. Records raw text, usage, cost and cap hits. |
| 7. Dev and held-out manifests | `experiments/make_tier5_dev.py`, `experiments/tier5-dev-L{1..5}.json`, `experiments/tier5-heldout-L4.json` | Done. 8 dev stories per level and 48 held-out L4 stories from a separate seed. Each manifest stores a hash of every prompt, so generator drift stops a run. |
| 8. Run report and gate checks | `conlang/tier5_report.py` | Done. Stage curve, DCS with a story-bootstrap interval, rules to solve, retention, module profile, baselines and the gate checks. `--archive` bundles a run into one file, and the report reads that file the same way as a run folder. |
| 9. Site and CI | `experiments/build_tier5_site.py`, CI step | To do |

### Run the dev sweep

```sh
python -m experiments.run_tier5_probes --manifest experiments/tier5-dev-L4.json \
  --out .work/tier5-dev-haiku-L4 --budget 0.70 --model claude-haiku-5-5 \
  --provider Anthropic --effort low --rates 0.1 0.5
python -m conlang.tier5_report --manifest experiments/tier5-dev-L4.json --run .work/tier5-dev-haiku-L4
```

Add `--estimate` to the first command to print the worst-case cost without a call. With the 16,384-token cap, the worst case for all five levels is $2.64 (312 calls). The sweep cost $1.05.

### Run the held-out probe

```sh
python -m experiments.make_tier5_dev --heldout L4 --count 48
python -m experiments.run_tier5_probes --manifest experiments/tier5-heldout-L4.json \
  --out .work/tier5-heldout-haiku-L4 --budget 2.50 --model claude-haiku-5-5 \
  --provider Anthropic --effort low --rates 0.1 0.5 --max-output 32768 --workers 4
python -m conlang.tier5_report --manifest experiments/tier5-heldout-L4.json \
  --run .work/tier5-heldout-haiku-L4 --archive reports/tier5-heldout-haiku-low-L4-responses.json
```

To score an archived run again, pass the archive file to `--run`.

## Offline results

`python -m conlang.verify_tier5_offline --count 200`, 200 stories per level:

| Level | Built / rejected | Stage-0 answerable | Final stage unique | Strongest baseline | Time |
|---|---|---:|---|---|---:|
| L1 | 200 / 0 | 97.6% | 100% | `suffix_blind` 46.1% | 0.3 s |
| L2 | 200 / 0 | 99.2% | 100% | `english_order` 42.9% | 0.4 s |
| L3 | 200 / 0 | 98.8% | 100% | `suffix_blind` 36.3% | 0.8 s |
| L4 | 200 / 0 | 100% | 100% | `english_order` 28.7% | 7.8 s |
| L5 | 200 / 0 | 100% | 100% | `suffix_blind` 27.4% | 9.1 s |

No verifier search reached its node cap.

## Dev sweep results

Haiku 5.5, effort low, 16,384-token cap, 8 stories per level, 312 calls, $1.05. Replies: `reports/tier5-dev-haiku-low-L{1..5}-responses.json`.

| Level | DCS (95% interval) | Stage 0 | Final stage | English | Strongest baseline | Capped | Failed checks |
|---|---|---:|---:|---:|---|---:|---|
| L1 | 90.0 (80.8–97.1) | 85.4 | 97.9 | 100.0 | `suffix_blind` 58.3 | 0 | tuning band, ladder gap |
| L2 | 86.5 (75.4–95.1) | 70.8 | 93.8 | 100.0 | `suffix_blind` 43.8 | 1 | tuning band, ladder gap |
| L3 | 79.8 (72.0–86.9) | 54.2 | 95.8 | 91.7 | `first_name` 31.2 | 1 | tuning band |
| **L4** | **61.5 (52.6–71.9)** | 39.6 | 91.7 | 97.9 | `suffix_blind` 37.5 | 3 | cap share |
| L5 | 49.0 (37.5–60.7) | 27.1 | 85.4 | 100.0 | `suffix_blind` 33.3 | 2 | English gap, cap share, baseline margin |

L4 is frozen as the Tier 5 level. It is the only level in the tuning band whose single failed check was the cap share, and a higher cap removes that failure. L5 fails three checks. L1–L3 are too easy for the probe and fail the offline baseline limit.

**Frozen settings:** level L4, protocol `tier5-0.1`, 6 questions per story, card-order seed 5, output cap 32,768, effort low for the probe.

## Held-out result

Haiku 5.5, effort low, 32,768-token cap, 48 L4 stories (`experiments/tier5-heldout-L4.json`), 432 calls, $1.75. Replies: `reports/tier5-heldout-haiku-low-L4-responses.json`.

| Metric | Value |
|---|---|
| DCS (95% interval) | **61.8 (58.1–65.5)** |
| Stage curve, stages 0–7 | 36.5, 37.2, 46.2, 52.1, 62.2, 79.5, 87.9, 93.1 |
| English control | 94.8 |
| Rules to solve, median | 6 of 7 |
| Retention | 79.9% |
| Strongest baseline | `suffix_blind` 27.8 |
| Capped replies | 0 |

Module profile, accuracy on questions that depend on the module, before and after its card:

| Module | Before | After |
|---|---:|---:|
| Agreement | 43.2 | 87.6 |
| Negation | 37.7 | 78.5 |
| Role (case) | 51.1 | 76.8 |
| Irrealis | 42.6 | 72.6 |
| Tense | 46.7 | 71.2 |
| Pronoun | 36.3 | 66.0 |

All six checks pass: hard band, tuning band, ladder gap 56.6 points, final stage 1.7 points below English, no capped reply, and DCS 34.0 points above the strongest baseline. The held-out DCS agrees with the dev DCS (61.5) within 0.4 points.

Retention below 100% means a model sometimes loses a correct answer when one more card appears. Pronoun resolution gains the least from its card.

## Calibration gates

Run these in order. Stop and revise the design if a gate fails.

1. **Offline, at every level.** Every final-stage question must be uniquely answerable. The strongest baseline must be below 30%. Report stage-0 answerability, but do not gate on it (see [Answerability](#answerability)). **Current result: L4 and L5 pass. L1, L2 and L3 fail the baseline limit,** so they are run in the dev sweep for the curve shape, but they are not eligible.
2. **Dev sweep.** Run the [tuning procedure](#tuning-procedure) steps 1–4 with the probe. Probe final-stage accuracy must be within 10 points of its English score. Fewer than 2% of requests may reach the cap. The probe's DCS must be at least 20 points above the strongest baseline of the chosen level. **Result: L4 chosen.** It passed every check except the cap share (3 of 72), which the 32,768 cap fixed. See [Dev sweep results](#dev-sweep-results).
3. **Held-out probe.** Tuning procedure step 5: probe DCS in 10%–90%, and a stage gap of at least 30 points. **Result: pass.** DCS 61.8, stage gap 56.6 points. See [Held-out result](#held-out-result).
4. **Model comparison.** Only after gate 3 passes, run other models on the same frozen held-out manifest. Report the strongest and weakest models against the band.

## Cost estimate

A 48-story run at L4 or L5 is 432 calls. One prompt is about 2,000 input tokens. Assume a mean output of 2,000 tokens; reasoning models can use more.

| Model | Input | Output | Estimate |
|---|---:|---:|---:|
| Haiku 5.5 low ($0.10 / $0.50 per M) | ~0.9 M | ~0.9 M | about $0.55 |
| Sonnet 5.5 low ($2 / $10 per M) | ~0.9 M | ~0.9 M | about $11 |
| Dev sweep, 5 levels × 8 stories on the probe | | | $1.05 (actual) |
| Held-out probe run (gate 3) | | | $1.75 (actual) |

Calibration cost $2.80 in total, with the probe only. Haiku low used more output than the 2,000-token assumption, so the Haiku row is low by about 3×. Scale the other model rows the same way before a run.

The Claude rates come from third-party coverage and are not verified. Check the current provider pages before a run.

## Open questions

- Should a rule card state a rule in grammatical terms ("`-ru` marks the agent") or give a worked example ("`Ada-ru` = Ada does the action")? v1 uses rules. A later matched comparison can test examples.
- Stage-0 answerability is nearly 100%. Should a v2 add real information loss, for example events whose object is not named? This would make some answers unrecoverable before a card, as the first draft expected.
- Should the six questions per story stay fixed? Fewer questions cost the same per call but give a noisier module profile.
