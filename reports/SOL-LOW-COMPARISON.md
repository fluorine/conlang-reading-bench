# GPT-6 Sol, low reasoning: matched five-object test

GPT-6 Sol with **low** reasoning was evaluated on the same 48 stories and matched English controls used in the [Luna and Terra comparison](TIER3-COMPARISON.md). Sol scored **18/48 (37.50%)** in the invented language and **48/48 (100%)** on English. It completed all responses without a token-limit failure. The conlang accuracy was **9/24** on each frozen story set.

| Configuration | Conlang | English control |
|---|---:|---:|
| GPT-6 Luna (medium) | 18/48 (37.50%) | 48/48 (100%) |
| GPT-6 Sol (low) | 18/48 (37.50%) | 48/48 (100%) |
| GPT-6.1 Terra (medium) | 40/48 (83.33%) | 48/48 (100%) |

Sol and Luna had the same total, but answered different questions correctly: both were right on nine stories, Sol alone on nine, Luna alone on nine, and neither on 21. Sol minus Luna was **0 percentage points**, with a **−16.7 to +16.7 point** suite-stratified paired bootstrap interval. Sol minus Terra was **−45.8 points**, with a **−62.5 to −29.2 point** interval. The 10,000 bootstrap samples resample stories within each 24-story set using seed 492014.

These are **model-and-effort configurations**: Sol used low effort while the others used medium. The result does not establish an ordering of the underlying models at equal effort. It is one run per configuration, on one artificial grammar family, and does not establish general language comprehension. The last-name-mentioned shortcut scores **15/48 (31.25%)** on these stories; random choice among suffix-blind possible holders has **18.8% expected accuracy**. Those baselines make the similar Sol and Luna scores particularly important to interpret cautiously.

Each call used a fresh context, no tools, `gpt-6-sol`, low reasoning and a 16,384-token completion limit; no temperature was specified. The 96 completed calls cost approximately **$0.81110** when provider-reported usage is valued at the listed standard rates of $2 per million input and $10 per million output tokens. No pending or uncertain attempts remain for these two runs. These estimates are not an invoice and do not reconstruct cache discounts. [OpenAI model documentation](https://developers.openai.com/api/docs/models/gpt-6-sol) · [Release notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes)

The [raw Sol responses](sol-comparison-responses.json) include prompts, results, model identifiers, usage and run metadata. Regrade all three configurations and their paired comparisons without API calls:

```sh
python -m unittest discover -s tests -v
python -m conlang.verify_sol_comparison
python -m experiments.build_tier3_site
```

The verifier first checks the base comparison, then checks Sol's frozen manifest hashes, coverage, prompts, answers, settings and token-cost arithmetic. It recomputes paired intervals. Verification cannot attest that a provider produced the submitted transcript. The [search report](TIER3-SEARCH.md) explains generation, the uniqueness checker, budgeted reruns and the remaining benchmark limitations.
