# Tier 4 progressive-hint prototype: first development run

This is a **development experiment**, not a calibrated tier or model leaderboard. Four generated stories each contain 30 transfers and four questions about final object holders. The same story and questions are presented through three stages that disclose one, five, and then all 15 suffix meanings. Each suffix still has two possible meanings. The abstract grammar family and its structural rules are stated from the start; minimal means one disclosed suffix, not no grammar instructions. Each question is graded as a correct or incorrect name, with missing or malformed answers counted wrong.

GPT-6 Luna at **low** reasoning and an 8,192 completion-token cap produced these results:

| Condition | One suffix | Five suffixes | All 15 suffixes |
|---|---:|---:|---:|
| Fresh context: conlang and cumulative hints | 1/16 (6.25%) | 5/16 (31.25%) | 1/16 (6.25%) |
| Continued conversation: cumulative hints | 2/16 (12.50%) | 2/16 (12.50%) | 1/16 (6.25%) |
| Continued conversation: **no new hints** | 2/16 (12.50%) | 2/16 (12.50%) | 2/16 (12.50%) |
| Fresh context: English control | 16/16 (100%) | 16/16 (100%) | 16/16 (100%) |
| Continued conversation: English, no new hints | 16/16 (100%) | 16/16 (100%) | 16/16 (100%) |

Fresh attempts use independent contexts. Continued attempts include the model's own earlier responses and repeat the same questions; no condition gives correct answers or answer feedback. English tells the same events and asks the same questions. The no-new-hint condition estimates changes from repetition and retained context without adding language clues. Repeated fresh English calls are separate attempts at the identical English prompt.

The suffix-blind uniform-random baseline for these 16 questions has **18.3% expected accuracy**; repeating the last name mentioned gives **2/16 (12.5%)**, and always choosing each object's initial holder gives **5/16 (31.25%)**. Suffix-blind baselines ignore even the disclosed marker meanings and are not exhaustive shortcuts. The fresh initial and full-hint results are below the random baseline and the initial-holder shortcut, and this sample does not show a reliable improvement from hints. **A score below 40% alone is not sufficient evidence that this is a useful calibrated tier.** Only four stories were sampled; their four questions are correlated, and selecting among candidate designs based on these development results adds further uncertainty.

The simulator and finite search require every one of the four answers to be unique under the least disclosed stage. Another check requires every answer to have at least two possibilities when suffixes are removed. Later hints are nested and checked against the same story and answers. This is a guarantee under the implemented formal rules, not proof of naturalness, human clarity, or resistance to all shortcuts.

All **60 requests** finished without empty or capped responses. At the recorded standard token rates, reported usage is valued at approximately **$0.03020**; this is an estimate, not an invoice. The [raw responses](tier4-dynamic-dev-responses.json) retain exact messages, prior model responses for continued conversations, answers, provider identifiers, usage and scores. The frozen prototype and manifest were committed before calls. Regrade without API requests:

```sh
python -m unittest discover -s tests -v
python -m conlang.verify_tier4_dynamic
```

## Matched unique-marker variant

We then reused the same four event histories and questions, but gave each suffix a single distinct meaning instead of two. The visible word order can differ between the variants. The hint stages disclose one, five, and all 30 suffix meanings. This is a deliberately simpler artificial grammar, not a claim about natural languages.

| Condition | One suffix | Five suffixes | All 30 suffixes |
|---|---:|---:|---:|
| Fresh context: conlang and cumulative hints | 3/16 (18.75%) | 5/16 (31.25%) | 16/16 (100%) |
| Continued conversation: cumulative hints | 3/16 (18.75%) | 4/16 (25%) | 16/16 (100%) |
| Continued conversation: **no new hints** | 3/16 (18.75%) | 3/16 (18.75%) | 3/16 (18.75%) |
| Fresh context: English control | 16/16 (100%) | 16/16 (100%) | 16/16 (100%) |
| Continued conversation: English, no new hints | 16/16 (100%) | 16/16 (100%) | 16/16 (100%) |

This variant shows a promising response to full disclosure in development, but its first-stage score is at the **18.3% expected suffix-blind random baseline**. The last-name heuristic scores **7/16 (43.75%)**, and the initial-holder heuristic **5/16 (31.25%)** on these same four stories. Those shortcuts outperform the first-stage model score; the sample is too small to decide whether the gap reflects the generator or chance. One story's initially disclosed suffix never appeared in its text, and some other disclosed suffixes were also unused. They still constrain the complete one-to-one mapping, but may be less immediately useful to a reader. The conditions use independent model calls, and their 16 questions are grouped within just four stories. Do not infer a reliable hint effect, calibrated ranking, or general language capability from this pilot.

All 60 calls completed without caps or empty responses, for about **$0.03077** in estimated token-valued usage. [Raw unique-marker responses](tier4-unique-dev-responses.json) can be regraded with `python -m conlang.verify_tier4_unique`; `python -m conlang.verify_tier4_dynamic` separately regrades the shared-marker pilot. Both require no API keys. The [frozen manifest](../experiments/tier4-unique-dev.json) uses the same four development seed pairs as the shared-marker run.

The unique-marker variant is a candidate for an independently seeded holdout and story-level uncertainty analysis, not an established Tier 4. Human review, stronger shortcut checks, and a fresh sample remain necessary before adding stronger models or presenting it as a leaderboard. [Design and replication considerations](NEXT-TIER-DYNAMIC-DESIGN.md)
