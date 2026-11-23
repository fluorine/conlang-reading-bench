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

The suffix-blind uniform-random baseline for these 16 questions has **18.3% expected accuracy**; repeating the last name mentioned gives **2/16 (12.5%)**. Suffix-blind baselines ignore even the disclosed marker meanings and are not exhaustive shortcuts. The fresh initial and full-hint results are below that random baseline, and this sample does not show a reliable improvement from hints. **A score below 40% alone is not sufficient evidence that this is a useful calibrated tier.** Only four stories were sampled; their four questions are correlated, and selecting among candidate designs based on these development results adds further uncertainty.

The simulator and finite search require every one of the four answers to be unique under the least disclosed stage. Another check requires every answer to have at least two possibilities when suffixes are removed. Later hints are nested and checked against the same story and answers. This is a guarantee under the implemented formal rules, not proof of naturalness, human clarity, or resistance to all shortcuts.

All **60 requests** finished without empty or capped responses. At the recorded standard token rates, reported usage is valued at approximately **$0.03020**; this is an estimate, not an invoice. The [raw responses](tier4-dynamic-dev-responses.json) retain exact messages, prior model responses for continued conversations, answers, provider identifiers, usage and scores. The frozen prototype and manifest were committed before calls. Regrade without API requests:

```sh
python -m unittest discover -s tests -v
python -m conlang.verify_tier4_dynamic
```

The next development step is to try a less opaque, fully reversible marker scheme and compare hint levels on matched stories. A promising candidate still needs independent fresh stories, a story-level uncertainty analysis, human review, and shortcut checks before testing stronger models or adding an official tier. [Design and replication considerations](NEXT-TIER-DYNAMIC-DESIGN.md)
