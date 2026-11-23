# Tier 4: regular object-and-role grammar (development)

This candidate retains five objects and a 30-transfer story but reduces the grammar from 30 fused object/context/role endings to ten endings that encode object and role only. The middle field of each shown meaning is a fixed placeholder. Each story has four end-of-story questions. The [12 development stories](../experiments/tier4-regular-dev.json) were independently generated and checked for unique answers, suffix-blind ambiguity and full-grammar replay. The candidate arose after previous adaptive research, so this is development rather than a final benchmark.

| Fresh context | One meaning | Three meanings | All ten meanings |
|---|---:|---:|---:|
| Luna low, conlang | 18/48 (37.5%) | 28/48 (58.3%) | 47/48 (97.9%) |
| Disclosed-transfer tracker | 13/48 (27.1%) | 28/48 (58.3%) | 48/48 (100%) |
| English control | 48/48 (100%) | 47/48 (97.9%) | 47/48 (97.9%) |

The same English story is asked in independent calls; its columns are attempts, not English hints. The last-name shortcut scored 12/48 (25%); choosing the initial holder scored 4/48 (8.3%); uniform guessing among suffix-blind possible holders has 18.6% expected accuracy. At one hint, Luna minus the disclosed-transfer tracker is +10.4 points (descriptive 95% story bootstrap −10.4 to +35.4); Luna minus the last-name shortcut is +12.5 points (−10.4 to +35.4). Both intervals include no advantage, so the pilot does not establish calibration.

No requests were empty or capped. Three one-hint responses supplied fewer than four parseable answers, as did one three-hint response; missing answers count as incorrect. The 72 requests had recorded token-valued cost approximately $0.03323. [Raw responses](tier4-regular-dev-responses.json) and the [manifest](../experiments/tier4-regular-dev.json) support offline regrading with `python -m conlang.verify_tier4_regular_dev`. Automated verification cannot attest provider provenance or replace human review.

The promising but uncertain one-hint result motivated a [predeclared 48-story evaluation](../experiments/tier4-regular-confirm-0.json), frozen before collection. The acceptance criteria require below 40% conlang accuracy, at least 90% on both the initial English and full-grammar controls, no empty or capped requests, and positive lower bounds on 95% paired story-bootstrap intervals against both shortcuts. Invalid or missing answers count wrong and their rates must be disclosed. The other three manifest batches have the same criteria. This evaluation uses fresh seeds and keeps failed outcomes, not only favorable stories.
