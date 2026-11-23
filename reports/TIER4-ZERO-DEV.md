# Tier 4: zero-hint regular grammar (development)

The earlier [48-story one-hint evaluation](TIER4-REGULAR-CONFIRM.md) cleared two shortcut comparisons but Luna low scored 45.8%, above the preset 40% ceiling. This adaptive candidate begins with **no disclosed suffix meanings** and reveals one and then all ten. The grammar structure, initial holdings, chronological transfer rule and names remain visible. Each of the 12 fresh stories was checked to have a unique answer even before suffix meanings are disclosed; full-grammar replay is independently checked.

| Fresh context | No meanings | One meaning | All ten meanings |
|---|---:|---:|---:|
| Luna low, conlang | 18/48 (37.5%) | 20/48 (41.7%) | 47/48 (97.9%) |
| Disclosed-transfer tracker | 7/48 (14.6%) | 17/48 (35.4%) | 48/48 (100%) |
| English control | 48/48 (100%) | 48/48 (100%) | 48/48 (100%) |

At zero hints, last-name guessing scored 11/48 (22.9%), and uniform guessing among suffix-blind possible holders had 18.6% expected accuracy. Luna minus the initial-holder tracker was +22.9 percentage points (95% descriptive story bootstrap −4.2 to +50.0); Luna minus last-name was +14.6 points (−2.1 to +35.4). The small sample and adaptive selection leave both advantages uncertain; this is not calibrated.

There were 72 requests, no empty or capped responses and approximately $0.03531 recorded token-valued cost. At both zero and one hint, two responses each supplied no parseable answers; missing answers count wrong. The [manifest](../experiments/tier4-regular-zero-dev.json) and [raw responses](tier4-regular-zero-dev-responses.json) are available. Run `python -m conlang.verify_tier4_regular_zero_dev` to reconstruct and regrade without API calls. Formal checks do not attest provider provenance or replace human review.

The [48-story confirmation](../experiments/tier4-zero-confirm-0.json) was frozen after the pilot and before collection. It requires zero-hint accuracy below 40%, initial English and full grammar at least 90%, no empty or capped requests, and positive lower 95% paired story-bootstrap bounds against both the initial-holder and last-name baselines. Invalid or missing answers count wrong. The remaining three batches have the same preregistered criteria. If these gates are not met, the tier remains experimental.
