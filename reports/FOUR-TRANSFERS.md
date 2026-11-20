# Four-transfer diagnostic

GPT-6 Luna with low reasoning scored **85.42% (82/96)** with minimal clues and **100.00% (96/96)** on the paired English control. Its original two-transfer scores were 98.96% with minimal clues and 100% in English.

## What changed

The 24 fresh stories use the same grammar family and two objects. Each object changes hands twice, alternating between the coin and the key. The order of the initial ownership statements varies. The historical question asks who held one object just before the other was given away for the second time. The direct and final-holder questions keep their original form.

| Question | Minimal clues | English |
|---|---:|---:|
| Recipient of an early transfer | 21/24 | 24/24 |
| Historical holder of the other object | 19/24 | 24/24 |
| Final holder of the first object asked about | 21/24 | 24/24 |
| Final holder of the second object asked about | 21/24 | 24/24 |

The paired English version provides a control for story tracking on the four-transfer suite. Differences from the earlier tier are descriptive because the seed set, transfer count, and historical question all changed. This diagnostic reports each condition separately.

## Reproduce the run

The manifest uses master seed 1643. The API run used `gpt-6-luna`, low reasoning, and a 512-token cap including reasoning, matching the earlier Luna configuration. The 48 responses cost approximately $0.00652 at list price. [Frozen manifest](../suites/transfer4.json) · [Raw responses](../results/transfer4/gpt-6-luna-low.json)

```sh
python -m conlang generate --suite transfer4 --out .work/transfer4
python -m conlang score results/transfer4/gpt-6-luna-low.json
```
