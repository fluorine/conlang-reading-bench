# Tier 4: one question at a time on final-state stories

Following the [midpoint focused-question diagnostic](TIER4-CHECKPOINT-DEV.md), we asked one end-of-story question per fresh call on the same 12 stories used in the earlier [observed-marker sample](TIER4-OBSERVED-FRESH.md). All four object questions were asked separately at each hint level. This is an adaptive development comparison on previously tested stories, not independent confirmation. The scoring, gold answers and hints were unchanged; focusing requires four times as many model requests.

| Hints | Focused questions | Original four-question call | Hint-aware tracker | Last-name shortcut |
|---|---:|---:|---:|---:|
| 1 | 11/48 (22.9%) | 11/48 (22.9%) | 7/48 (14.6%) | 12/48 (25%) |
| 5 | 15/48 (31.25%) | 12/48 (25%) | 18/48 (37.5%) | 12/48 (25%) |
| 30 | 46/48 (95.8%) | 47/48 (97.9%) | 48/48 (100%) | 12/48 (25%) |

The focused-minus-joint differences were 0.0, +6.25 and −2.1 percentage points; descriptive story-bootstrap 95% intervals were −20.8 to +22.9, −10.4 to +25.0, and −8.3 to +4.2, respectively. These intervals do not account for selection after exploring task variants. A low score is not evidence of meaningful comprehension: the one-hint score is below the last-name shortcut, and the five-hint score is below the hint-aware tracker. This remains an uncalibrated research prototype.

The 144 focused conlang calls had no empty or capped responses and cost approximately $0.09653 in recorded token value. No new focused English controls were run; earlier joint English controls are separate observations. Four frozen manifests and response archives are numbered 0–3: [0](tier4-final-focus-0-dev-responses.json), [1](tier4-final-focus-1-dev-responses.json), [2](tier4-final-focus-2-dev-responses.json), [3](tier4-final-focus-3-dev-responses.json). `python -m conlang.verify_tier4_final_focus` reconstructs, regrades and reproduces the paired comparisons without API calls. The independent full-grammar replay verifies gold consistency but does not attest provider provenance.
