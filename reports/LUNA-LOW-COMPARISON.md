# GPT-6 Luna, low reasoning: matched five-object test

GPT-6 Luna with **low** reasoning was evaluated on the same 48 stories and matched English controls as the [existing comparison](TIER3-COMPARISON.md). It answered **14/48 (29.17%)** conlang questions and **48/48 (100%)** English controls correctly. All responses completed without reaching the output cap. It scored **6/24** on the original set and **8/24** on the fresh set.

| Configuration | Conlang | English control |
|---|---:|---:|
| GPT-6 Luna (low) | 14/48 (29.17%) | 48/48 (100%) |
| GPT-6 Luna (medium) | 18/48 (37.50%) | 48/48 (100%) |
| GPT-6 Sol (low) | 18/48 (37.50%) | 48/48 (100%) |
| GPT-6.1 Terra (medium) | 40/48 (83.33%) | 48/48 (100%) |

On paired stories, Luna low and medium were both right on nine, low alone on five, medium alone on nine, and neither on 25. Low minus medium was **−8.3 percentage points**, with a **−22.9 to +6.2 point** suite-stratified paired bootstrap interval. The interval includes zero, so this sample does not establish a reliable difference between these two effort configurations. It resamples stories within each 24-story set, using 10,000 samples and seed 492014.

The last-name-mentioned shortcut scores **15/48 (31.25%)** on the same stories, slightly above Luna low. A uniform choice among suffix-blind possible holders has **18.8% expected accuracy**. These are exploratory results from one grammar family and one run per configuration; neither the score nor the baselines establish general language comprehension. Equal provider-native effort labels do not imply equal compute across models.

Each request used a fresh context, no tools, `gpt-6-luna`, low reasoning and a 16,384-token completion limit, with no temperature specified. The 96 completed calls cost approximately **$0.03718** at the recorded standard token rates, compared with approximately **$0.17711** for the existing Luna medium run. These are usage-based estimates, not invoices, and do not reconstruct cache discounts. There were no pending or uncertain requests in the Luna low bundles.

The [raw responses](luna-low-comparison-responses.json) preserve prompts, answers, model identifiers, usage and run metadata. Regrade without paid calls:

```sh
python -m unittest discover -s tests -v
python -m conlang.verify_luna_low_comparison
python -m experiments.build_tier3_site
```

The regrader verifies the existing comparison first, then checks Luna low's manifest hashes, coverage, generated prompts and gold answers, settings, parsed scores and token-cost arithmetic. It computes paired bootstrap intervals. It cannot attest that a provider produced the transcript. The [search report](TIER3-SEARCH.md) describes generation, answerability, budgeted reruns and limitations.
