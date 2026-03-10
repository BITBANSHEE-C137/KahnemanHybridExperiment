# v3 Training SITREP

## v3 Training Status
**Step 30,400/50,000 (60.8%)** | GPU: 100% util, 84°C | **19.6K steps remaining** (~17h ETA)  
Current spot rate: **$0.46/hr** (53% savings vs on-demand) | Total cost: **$25.06**

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 23000 | 29.57  | 4.19      | 26.1%  | 0.861 | 0.0059 |
| 24000 | 29.53  | 4.31      | 25.2%  | 0.862 | 0.0055 |
| 25000 | 29.48  | 4.08      | 26.5%  | 0.861 | 0.0042 |
| 26000 | 29.58  | 4.02      | 27.7%  | 0.864 | 0.0063 |
| 27000 | 29.55  | 4.32      | 24.6%  | 0.866 | 0.0109 |
| 28000 | 29.40  | 4.51      | 23.8%  | 0.865 | 0.0068 |
| 29000 | 29.36  | 4.27      | 25.5%  | 0.867 | 0.0118 |
| 30000 | **29.16** | 4.34   | 24.6%  | **0.868** | **0.0046** |

**Trends:** AR perplexity **improving steadily** (29.57→29.16). AUROC **climbing** (0.861→0.868). S1 accuracy **volatile** around 25%. Diff loss **stagnant** ~4.3. ECE **excellent** but unstable.

## Target Scorecard

| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **29.16** | ✅ **MET** |
| AUROC > 0.75 | **0.868** | ✅ **MET** |
| ECE < 0.05 | **0.0046** | ✅ **MET** |
| Diff loss → 4.0 | **4.34** | ❌ Need -8% |
| S1 accuracy → 40% | **24.6%** | ❌ Need +63% |

**3/5 targets met.** Diffusion and S1 accuracy lagging significantly.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Current v3 AR performance superior to v1** (29.16 vs 43.86 PPL). S1 accuracy severely degraded from v1 baseline.

## Infrastructure
**19 spot sessions** across g5/g6 instances. Multiple **interruptions** 3/9 afternoon (11 reclaims in 4h window). Current g6.2xlarge stable **11h uptime**. Total infrastructure cost **well-managed** at $25.06 for 30K steps.

## What's Next
**Continue training to 50K steps** (17h remaining). Monitor S1 accuracy plateau - may need **learning rate adjustment** if no improvement by step 35K. Diffusion loss requires **loss weighting analysis**. Post-completion: comprehensive v1/v3 benchmark comparison and confidence calibration deep-dive.