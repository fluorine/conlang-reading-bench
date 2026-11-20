# Tier 3 calibration

Goal: approximately 25% accuracy for GPT-6 Luna at medium reasoning, with an English control. The candidates use longer alternating transfer stories. These are development results.

The objective is to measure how models interpret unfamiliar vocabulary and grammatical rules and reason about the resulting story. For each candidate, the English control uses the same events and questions. Prefer candidates where Luna completes the English control near 100%, then examine how the conlang score changes as language features become more demanding. Report both scores and completion rates, and verify each question is determined by the supplied clues.

| Transfers | Stories | Completion cap | Conlang accuracy | English accuracy | Empty at cap | Estimated USD |
|---|---:|---:|---:|---:|---:|---:|
| 12 | 12 | 2048 | 56.25% | 93.75% | 4 | $0.00811 |
| 24 | 8 | 4096 | 84.38% | 96.88% | 1 | $0.00768 |
| 48 | 6 | 8192 | 95.83% | 91.67% | 0 | $0.00727 |

None of these candidates achieved the 25% target. The candidates use different story samples and completion limits. The 12-transfer run had four empty outputs at the cap, and the 24-transfer run had one. These small development samples do not establish held-out performance or a calibrated Tier 3.

The existing verifier checks whether all allowed interpretations give the same answers. The generator retains the two-object, three-person task, and every story alternates the objects. The three possible answer names give a uniform-guess baseline of 33.33%, so a 25% accuracy target is below that baseline. A future candidate should use a larger answer space and a preregistered held-out suite to make 25% an informative target.

Run python -m conlang verify-results to regrade the saved answers. The manifests and prompts were frozen on main before each run.

## Six-person candidates

Six-person stories increase the answer space to six names, so uniform guessing gives 16.67%. The same deterministic checker validates the intended answers. The eight-story 24-transfer development run scored 93.75% in the conlang and 100% in English. The eight-story 48-transfer development run scored 100% in both. Neither produced empty responses. Both used GPT-6 Luna with medium reasoning and 4,096 and 8,192 completion-token caps, respectively. They cost $0.00496 and $0.00910 at list price. These exploratory candidates remain far from the 25% target.

A further six-story candidate with 96 transfers scored 100% in the conlang and 91.67% in English for Luna medium. It cost $0.00555. This remains a development run, and the 25% target is not met.

## Alternating grammar candidates

The six-person candidate supplies explicit rules whose word order and role suffix meanings reverse on alternating transfers. The 12-transfer development set scored 96.88% conlang and 100% English across eight stories. The 48-transfer set scored 93.75% conlang and 96.88% English across eight stories. Luna used medium reasoning with 4,096 and 8,192 completion-token caps. The runs cost $0.00711 and $0.01169 respectively. Neither candidate reached the low-score calibration target. The transformed text is independently decoded against the explicit grammar before admission.
