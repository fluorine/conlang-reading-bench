# Proposed Tier 5: progressive rule disclosure over a richer grammar

**Status: design plan.** No code, manifests or model runs exist yet. Tier 5 will be a new comparison group. Do not mix its scores with earlier tiers.

## Why a new tier

Tier 4 zero-hint is near saturation for the strongest models. With the final-array regrade, Terra medium scores 99.5% and Luna medium scores 91.7%. Tier 4 has one grammar family: a fixed role order with a few suffix meanings to infer. It cannot show *which* linguistic skill a model lacks. It also cannot show *how much* help a model needs.

Tier 5 changes the question. Earlier tiers ask "can the model read this language?" Tier 5 asks "**how many grammar rules must we reveal before the model reads this language, and which rules does it need?**"

## Core idea

1. Generate a story in a conlang. The grammar uses several real linguistic phenomena: case, agreement, free word order, tense, negation and anaphora.
2. Always show the lexicon: the word stems and their meanings. Hide every grammar rule at stage 0.
3. Reveal one **rule card** at each stage. Ask the same questions at each stage. Give no feedback.
4. Score each stage. A model with more linguistic capacity needs fewer rules before its answers become correct and stay correct.

The design target is a **probe model that scores between 10% and 90%**. Then the tier has room for comparison on both sides: it is not too hard and not too easy. The [difficulty target](#difficulty-target-10-to-90) section defines this, and the [calibration gates](#calibration-gates) enforce it.

The test is **relativistic**. At early stages, a story can be truly ambiguous, so even a perfect reader cannot recover every answer. The verifier measures this when it can (see [Answerability](#answerability-relativistic-by-design)). The main result compares models on the same stories, the same stages and the same denominators. It does not claim an absolute ceiling.

## Grammar modules

Each module is one linguistic phenomenon. Each module has one or two rule cards. A language seed samples a value for each module. Every story must depend on every enabled module (see the load-bearing check below).

| Module | What the seed samples | What the model must do without the card |
|---|---|---|
| **Case** | Nominative-accusative or ergative-absolutive alignment. A suffix for each case. A dative or ablative case for the other person. | Infer which suffix marks the agent and which marks the recipient or source. Use the rule "only the holder can give". |
| **Word order** | Free order with the verb in a fixed position, or a basic order (SOV, VSO and so on) with scrambling for topic. | Ignore position as a role cue. Rely on case and agreement. |
| **Agreement** | Two or three noun classes over the names. A verb prefix agrees with one argument. The alignment decides which argument. | Use agreement to identify the agent when the case suffix is not clear (syncretism). |
| **Lexical role inversion** | Two verbs: *give* (agent loses the object) and *take* (agent gains the object). | Map case roles to the transfer direction for each verb. |
| **Tense** | A past suffix and a pluperfect suffix. The story text is not in chronological order. | Rebuild the true event order. |
| **Negation and irrealis** | A negation suffix and an irrealis or reported-speech particle. These events did not happen. | Exclude these events from the history. |
| **Anaphora** | Class-marked pronouns. A pronoun refers to the last name of its class. | Resolve the pronoun through class agreement. |

Morphophonology, for example vowel harmony with allomorphs, is a candidate v2 module. Keep it out of v1 so that each card stays one rule.

The world model stays the same as before: people pass objects, and only the current holder can give. This lets Tier 5 reuse `conlang/world.py`, the answer checker and the English renderer. It adds *take*, negated events, irrealis events and non-chronological narration.

### Illustration (not generated)

Lexicon (always shown): `molo` coin, `pek` key, `ti` give, `rasu` take, `hosa` hold.

```text
Ada molo hosa.  Bo pek hosa.
molo Bo-mi Ada-ru na-ti-ke
Cy-ru pek Bo-mi na-rasu-lo
Eli-mi Bo-ru molo so-ti-ke-nu
```

<details><summary>Hidden rules and meaning</summary>

`-ru` marks the agent and `-mi` marks the other person. The verb is last. `na-` agrees with a class-I agent (Ada, Cy, Eli) and `so-` agrees with a class-II agent (Bo, Dee, Fay). `-ke` is past and `-lo` is pluperfect. `-nu` means the event did not happen.

So: Ada gave the coin to Bo. *Before that*, Cy took the key from Bo. Bo did **not** give the coin to Eli. The order of events is Cy's take, then Ada's give.

</details>

## Disclosure ladder

v1 uses **eight cards**, so there are nine stages (0 to 8). Stage 0 shows the lexicon, the world rules and the instruction "this is a language with grammar to discover". Each later stage adds one card:

1. Agent case suffix
2. Recipient or source case suffix
3. Word order rule
4. Agreement classes and the verb prefix
5. Past and pluperfect tense
6. Negation
7. Irrealis particle
8. Pronoun reference

**Card order.** Use four predeclared orders in a Latin square. Each story gets one order. Every model sees the same order for the same story. This keeps model comparisons paired, and it averages out the effect of one fixed order.

**Card content.** A card states a rule. It never names an event, a person in the story or an answer. A static check rejects any card that contains a story name.

## Questions

Use six questions per story, so that one story tests several modules:

- Who holds the X at the end?
- Who held the X just after event *n* in true chronological order?
- Who gave the X to Y? (This needs case and inversion.)
- Who held the X before the first event? (This needs tense, because the text is not in order.)
- One question whose answer changes if a negated or irrealis event is counted. (This catches a model that ignores negation.)
- One question that goes through a pronoun.

Answers are names, so the existing JSON-array format works. The scorer is `conlang.scoring.parse_final_answer` (`final-array-1.0`) from the start. This prevents the problem where the strict parser gave Sonnet 0%. Record bare-JSON compliance as a separate number.

**Load-bearing check.** For each question, the verifier ablates each module. For example, it removes negation and counts negated events as real. If no question changes when a module is ablated, the story is rejected. This gives each question a **module tag set**, and this makes the per-module profile possible.

## Answerability: relativistic by design

At each stage, the verifier enumerates the grammars consistent with three inputs: the visible text, the revealed cards and the world rule (only the holder gives). For each question, it collects the answers across all consistent grammars.

- **One answer:** the question is *uniquely answerable* at that stage.
- **More than one answer:** the information may not be recoverable at that stage.
- **Too many grammars to enumerate** (over a fixed cap): the stage is *ceiling unknown*.

Report two numbers for each stage:

1. **Raw accuracy** = correct / all questions. This is the main, relativistic number. It is comparable between models because every model has the same denominator.
2. **Answerable accuracy** = correct / uniquely answerable questions, where the verifier knows the set.

The generator requires that at stage 8 (all cards) every question is uniquely answerable. It also requires that the English control gives the same gold answers.

## Metrics

| Metric | Definition | Use |
|---|---|---|
| **Disclosure capacity score (DCS)** | Mean raw accuracy over stages 0–8 (normalized area under the curve). | Main ranking number. Higher is better. |
| **Rules to solve (RTS)** | For each story, the first stage *k* where all six answers are correct at *k* and at every later stage. If this never happens, the value is 9 (censored). | Median and survival curve. Lower is better. |
| **Module profile** | Accuracy on questions tagged with a module, before and after that module's card. | Shows *which* linguistic skill is missing. |
| **Retention** | Share of correct answers at stage *k* that stay correct at *k*+1. | Measures stability. A guessing model flips often. |
| **English gap** | English accuracy minus stage-8 accuracy. | Separates language skill from event tracking. |

**Uncertainty.** Bootstrap over stories, not questions. Model comparisons are paired by story: report the paired DCS difference with a 95% interval and the per-story win rate.

**Baselines.** Compute these at every stage: last-mentioned name, first-mentioned name, most frequent name, an English-order reader (SVO, ignores suffixes) and a suffix-blind reader. Show the strongest baseline on the chart.

## Difficulty target: 10 to 90

A score near 0% or near 100% tells us little: the models cannot be separated there. Tier 5 must put its probe model inside the band, with margin.

**Probe model.** Claude Haiku 5.5 low. It is cheap (a 48-story run costs about $0.60), and its earlier scores are in the middle of the field (88% on Tier 1, 44% on Tier 3). One probe keeps calibration cheap and repeatable.

**Target band on DCS** (mean raw accuracy over stages 0–8):

| Band | Probe DCS | Meaning |
|---|---|---|
| Hard limit | 10%–90% | Outside this band, the tier fails calibration. |
| Tuning target | 30%–70% on dev | Margin for noise from a small dev sample and for stronger and weaker models. |
| Ideal | about 50% | Equal room above and below. |

Two more conditions make the band meaningful:

- **The ladder must matter.** Probe accuracy at stage 8 must be at least 30 points above stage 0. If the cards do not change the score, the tier measures something other than rule learning.
- **The band must hold at both ends of the field.** Report DCS for the strongest model (now Terra medium) and the weakest model (now Luna low). The strongest should stay below 90% and the weakest above 10%. This is a check, not a gate: a failure here is reported, and it starts a v2 difficulty level. It does not invalidate the probe calibration.

### Difficulty knobs

These parameters change difficulty without a change to the task. The generator takes them from a named **difficulty level**. One level is frozen for each comparison group.

| Knob | Easier | Harder |
|---|---|---|
| Enabled modules | 4 (case, order, tense, negation) | 7 (all) |
| Transfers per story | 12 | 30 |
| Case syncretism | Each case has its own suffix | Two cases share one suffix, so agreement must decide |
| Distractor events (negated or irrealis) | 1 | 5 |
| Out-of-order narration | 10% of events | 40% of events |
| People and noun classes | 4 people, 2 classes | 6 people, 3 classes |

Predeclare five levels, L1 (all easy) to L5 (all hard), before the first model call. Each level moves every knob one step toward hard. Do not tune knobs one by one on model results: that overfits the tier to the probe.

### Tuning procedure

1. Generate 8 dev stories at each level, L1 to L5. Use dev seeds only.
2. Run the probe on all five levels: 400 calls, about $0.50.
3. Pick the level with probe DCS closest to 50% and inside 30%–70%. If no level is inside the band, add a level between the two nearest ones and repeat steps 1–3 for that level only.
4. Freeze the level, prompts, card orders and scorer.
5. Make a new held-out manifest of 48 stories with fresh seeds. Run the probe. Its DCS must be in 10%–90%, and the stage 8 minus stage 0 gap must be at least 30 points.
6. If step 5 fails, do not tune on the held-out stories. Go back to step 1, change the level, and make a **new** held-out manifest.

## Protocol

- **Fresh context only in v1.** Each stage is one user message in a new context, with no system prompt and no tools. This matches the earlier runs. Continued context is a v2 condition.
- **Full ladder in v1.** Run all nine stages. Do not stop early when a model succeeds. DCS needs every stage, and the curve may not be monotonic. When the dev data shows monotonic curves, consider adaptive stopping (stop after two passed stages in sequence) to cut cost.
- **One output cap for all providers.** Use 16,384 tokens and record each request that reaches the cap. Sonnet high reached an 8,192 cap on 30 of 48 Tier 3 requests, which made that run hard to interpret.
- **Calls per story:** 9 conlang stages and 1 English control = 10 calls.

## Implementation plan

Follow the flat module layout that the repository already uses.

| Step | Files | Done when |
|---|---|---|
| 1. Grammar | `conlang/tier5_grammar.py` | A seed and a difficulty level (L1–L5) give a grammar. The renderer gives conlang lines and English lines. Unit tests cover each module. |
| 2. World extensions | `conlang/tier5_world.py` | *Take*, negated events, irrealis events and non-chronological narration exist. Gold answers come from the true history only. |
| 3. Rule cards | `conlang/tier5_cards.py` | Card text comes from the grammar. The static check passes: no story names in any card. |
| 4. Verifier | `conlang/tier5_verify.py` | Enumeration with pruning by the holder rule. Per-stage answerability, module tags and the enumeration cap work. |
| 5. Builder | `conlang/tier5.py` | Manifest to prompts for every stage, the English control, gold answers, the card order and baselines. The load-bearing check rejects weak stories. |
| 6. Runner | Generalize `experiments/run_tier4_probes.py` or add `experiments/run_tier5_probes.py` | Uses `conlang/provider.py`, the hard bundle budget and resume. Records raw text, usage and cap hits. |
| 7. Verification and site | `conlang/verify_tier5_*.py`, `experiments/build_tier5_site.py`, CI step | Saved responses regrade offline. The chart shows the curve, DCS and the strongest baseline. |

## Calibration gates

Run these in order. Stop and revise the design if a gate fails.

1. **Offline, at every level.** Generate 200 stories. At stage 8, 100% must be uniquely answerable. At stage 0, the median answerable share must be below 60%. The strongest baseline must be below 40% at stage 8. Its DCS must be below 25%, so that a shortcut cannot reach the band by itself.
2. **Dev sweep.** Run the [tuning procedure](#tuning-procedure) steps 1–4 with the probe. Probe stage-8 accuracy must be within 10 points of its English score. Fewer than 2% of requests may reach the cap.
3. **Held-out probe.** Tuning procedure step 5: probe DCS in 10%–90%, and a stage gap of at least 30 points.
4. **Model comparison.** Only after gate 3 passes, run other models on the same frozen held-out manifest. Report the strongest and weakest models against the band.

## Cost estimate

A 48-story run is 480 calls. One prompt is about 2,000 input tokens. Assume a mean output of 2,000 tokens; reasoning models can use more.

| Model | Input | Output | Estimate |
|---|---:|---:|---:|
| Haiku 5.5 low ($0.10 / $0.50 per M) | ~1.0 M | ~1.0 M | about $0.60 |
| Sonnet 5.5 low ($2 / $10 per M) | ~1.0 M | ~1.0 M | about $12 |
| Dev sweep, 5 levels × 8 stories on the probe | ~0.8 M | ~0.8 M | about $0.50 |
| Held-out probe run (gate 3) | | | about $0.60 |

Calibration costs about $1.10 in total, with the probe only. The cost for other models applies only after the tier passes calibration.

The Claude rates come from third-party coverage and are not verified. Check the current provider pages before a run.

## Open questions

- Should a rule card state a rule in grammatical terms ("`-ru` marks the agent") or give a worked example ("`Ada-ru` = Ada does the action")? v1 uses rules. A later matched comparison can test examples.
- How large is the hypothesis space when all seven modules are on? If enumeration is too slow for the cap, drop anaphora from v1 and move it to v2.
- Should the six questions per story stay fixed? Fewer questions cost the same per call but give a noisier module profile.
