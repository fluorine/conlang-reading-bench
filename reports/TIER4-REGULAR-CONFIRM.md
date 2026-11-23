# Tier 4: 48-story regular-grammar confirmation

Following the [12-story pilot](TIER4-REGULAR-DEV.md), we froze 48 new stories and acceptance criteria before collecting responses. The grammar has five objects, 30 transfers and ten endings encoding an object and a role. At each level the same four final-holder questions are asked in independent fresh contexts. English controls use the same underlying stories.

| Fresh context | One meaning | Three meanings | All ten meanings |
|---|---:|---:|---:|
| Luna low, conlang | 88/192 (45.8%) | 133/192 (69.3%) | 182/192 (94.8%) |
| English control | 191/192 (99.5%) | 191/192 (99.5%) | 192/192 (100%) |

At one hint, the disclosed-transfer tracker scored **65/192 (33.9%)** and the last-name shortcut scored **37/192 (19.3%)**. Luna minus tracker was **+12.0 percentage points** (95% paired story-bootstrap interval +1.0 to +22.9); Luna minus last-name was **+26.6 points** (+15.1 to +38.0). Bootstrap resampling uses 48 stories rather than treating the four questions per story as independent. Both shortcut intervals cleared zero, English and full disclosure exceeded 90%, and no request was empty or capped.

The predeclared acceptance rule also required one-hint accuracy **below 40%**. The observed **45.8%** misses that target, so the candidate is not accepted as calibrated under that rule. The result nevertheless supports a measurable advantage over the two tested shortcuts on this sample; it is not a general measure of model intelligence or evidence against all possible shortcuts.

All 288 requests were completed at approximately **$0.13501** in recorded token-valued cost. Responses supplied 32 fewer than the required 192 conlang answers at one hint, 20 fewer at three hints, and none fewer with all ten meanings; missing or invalid answers count wrong. The [four frozen manifests](../experiments/tier4-regular-confirm-0.json) and response archives ([0](tier4-regular-confirm-0-responses.json), [1](tier4-regular-confirm-1-responses.json), [2](tier4-regular-confirm-2-responses.json), [3](tier4-regular-confirm-3-responses.json)) contain seeds, exact prompts, raw outputs and usage. Run `python -m conlang.verify_tier4_regular_confirm` to reproduce the answers, controls and preregistered comparisons offline. Regrading cannot verify provider provenance and does not replace human review.

The next adaptive candidate removes the initial meaning entirely while still requiring all answers to be uniquely determined from the visible story and grammar. Its [development sample](../experiments/tier4-regular-zero-dev.json) is fresh but was selected after seeing this outcome; it is not an independent confirmation of a new threshold. A new candidate would need its own frozen confirmation.
