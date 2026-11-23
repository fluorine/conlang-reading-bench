# Tier 4: fresh focused midpoint evaluation

We froze 32 fresh stories before collecting model outputs, assigning eight stories to each of four queried objects. Each request asked one question about the holder after transfer 15 of 30. The first stage revealed one randomly ordered observed ending. The design was chosen after earlier pilots; this is a fresh development evaluation of that candidate, not a final benchmark.

| Fresh context | One hint | Three hints | Full grammar |
|---|---:|---:|---:|
| Luna low | 8/32 (25.0%) | 7/32 (21.9%) | 27/32 (84.4%) |
| English control | 32/32 (100%) | 31/32 (96.9%) | 32/32 (100%) |

At one hint, the disclosed-transfer tracker scored **6/32 (18.75%)**, and the last name on the checkpoint transfer scored **7/32 (21.9%)**. Uniform guessing among suffix-blind possible holders has **20.8% expected accuracy**. Model minus tracker was +6.25 points, with a 95% target-stratified story-bootstrap interval of −12.5 to +25.0; model minus last-name was +3.125 points (−18.75 to +25.0). Target groups each contain only eight stories, so subgroup differences are especially uncertain.

The [predeclared plan](../experiments/tier4-focus-fresh-0.json) required a score below 40%, English at least 90%, no unexplained output failures and a positive lower confidence bound against both shortcuts. The score and English thresholds were met, but neither shortcut comparison cleared the required bound. Five one-hint responses did not yield a one-name array and were scored incorrect; there were no empty responses or output caps. Full-grammar accuracy was below 90%. This candidate is not calibrated, and collecting more results on the same weak design would not by itself establish useful separation.

The 192 calls cost approximately $0.06990 in recorded token value. All prompts, responses, metadata and usage are available for [coin](tier4-focus-fresh-0-responses.json), [key](tier4-focus-fresh-1-responses.json), [book](tier4-focus-fresh-2-responses.json) and [ring](tier4-focus-fresh-3-responses.json). `python -m conlang.verify_tier4_focus_fresh` rebuilds and regrades the records and produces target-stratified bootstrap intervals without model calls. The independent full-grammar replay and suffix-blind checks do not establish provider provenance or replace human clarity review.
