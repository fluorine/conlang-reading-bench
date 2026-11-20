# Tier 3 calibration

Goal: approximately 25% accuracy for GPT-6 Luna at medium reasoning, with an English control. The candidates use longer alternating transfer stories. These are development results.

The objective is to measure how models interpret unfamiliar vocabulary and grammatical rules and reason about the resulting story. For each candidate, the English control uses the same events and questions. Prefer candidates where Luna completes the English control near 100%, then examine how the conlang score changes as language features become more demanding. Report both scores and completion rates, and verify each question is determined by the supplied clues.

Future calibration should vary linguistic difficulty as well as narrative length. Candidate features include fused markers that encode more than one grammatical property, productive sound changes inspired by language evolution, and explicitly evidenced irregular forms. Generate each form from a deterministic grammar and provide enough rules or examples to determine each scored answer. Verify possible interpretations against the clues before admitting an item. Compare changes on development stories with matched English controls, then freeze new held-out stories for the selected design. Report unresolved ambiguity, token exhaustion, and chance or shortcut baselines alongside accuracy.

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

## Fusional markers and an irregular name

A six-person candidate uses endings that jointly encode giver or recipient and the object transferred. Fay has irregular endings, and worked examples establish all endings. An independent decoder derives the marker meanings from those examples and checks the event history and answers. On eight 12-transfer development stories, GPT-6 Luna at medium effort scored 100% on the conlang and 100% on the matched English control. All 16 requests produced answers. The run used a 4,096-token completion cap and cost $0.00337 at list price. This candidate remains above the calibration target.

## Individually irregular and opaque names

A 24-transfer candidate assigns each of six names four unique role-and-object endings, all evidenced in examples. Luna medium scored 100% on both conditions across eight development stories. A second candidate also replaces the names with invented words and supplies a name dictionary. It scored 100% in both conditions on eight stories. Both used an 8,192-token cap and had no empty outputs. Costs were $0.00378 and $0.00575 at list price. These development candidates did not reach the target.

## Historical questions with opaque names

A 48-transfer development candidate combines individually irregular endings, invented names, and four questions about holders at different points within the story. The eight-story Luna medium run scored 100% conlang and 90.625% English, with no empty outputs, at $0.00715 list price. The target remains unmet and the English control fell below near-ceiling accuracy.

## Matched grammar-feature experiment

Six development stories were rendered in four matched versions: fused role-and-object endings, the same endings with a context-dependent internal vowel change, an irregular class for one name, and all three features combined. The English control used the same stories and questions. The complete examples and sound-change rule were supplied, and an independent decoder checked the answers. GPT-6 Luna at medium effort answered 24/24 questions in each grammar version and 24/24 in English. All 30 responses were complete. The five runs cost $0.00877 at list price. None entered the 25–50% target range, so no held-out suite was selected for this experiment. These scores do not establish performance for sparse or ambiguous clue settings.
