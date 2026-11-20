# Tier 3 calibration

Goal: approximately 25% accuracy for GPT-6 Luna at medium reasoning, with an English control. The candidates use longer alternating transfer stories. These are development results.

| Transfers | Stories | Completion cap | Conlang accuracy | English accuracy | Empty at cap | Estimated USD |
|---|---:|---:|---:|---:|---:|---:|
| 12 | 12 | 2048 | 56.25% | 93.75% | 4 | $0.00811 |
| 24 | 8 | 4096 | 84.38% | 96.88% | 1 | $0.00768 |
| 48 | 6 | 8192 | 95.83% | 91.67% | 0 | $0.00727 |

None of these candidates achieved the 25% target. The candidates use different story samples and completion limits. The 12-transfer run had four empty outputs at the cap, and the 24-transfer run had one. These small development samples do not establish held-out performance or a calibrated Tier 3.

The existing verifier checks whether all allowed interpretations give the same answers. The generator retains the two-object, three-person task, and every story alternates the objects. The three possible answer names give a uniform-guess baseline of 33.33%, so a 25% accuracy target is below that baseline. A future candidate should use a larger answer space and a preregistered held-out suite to make 25% an informative target.

Run python -m conlang verify-results to regrade the saved answers. The manifests and prompts were frozen on main before each run.
