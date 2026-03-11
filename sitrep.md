# v3 Training SITREP

## v3 Training Status
**Step 40,200/50,000 (80.4%)** • L4 GPU **100% util** @ 70W/72W, 79°C • **38.4 min ETA** @ current pace • Spot: **$0.43/hr** (56.5% savings) • Total cost: **$32.60**

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 33000 | 28.93  | 4.09      | 26.6%  | 0.861 | 0.0086 |
| 34000 | 28.85  | 4.15      | 25.6%  | **0.871** | 0.0069 |
| 35000 | 28.73  | **4.26**  | 25.0%  | 0.863 | 0.0057 |
| 36000 | 28.59  | **4.46**  | 23.5%  | 0.864 | **0.0109** |
| 37000 | 28.51  | **4.52**  | 24.1%  | 0.856 | 0.0065 |
| 38000 | **28.43** | 4.02   | **28.5%** | 0.864 | 0.0092 |
| 39000 | **28.34** | 4.04   | **29.0%** | 0.863 | **0.0113** |
| 40000 | **28.27** | **3.76** | **30.3%** | **0.881** | 0.0094 |

**Trends:** AR PPL steadily improving. **Diffusion loss volatile** (4.52→3.76). S1 accuracy **recovering** after mid-training dip. AUROC peaked at 0.881. ECE remains stable.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | **28.27** | ✅ |
| AUROC  | > 0.75 | **0.881** | ✅ |
| ECE    | < 0.05 | **0.0094** | ✅ |
| Diff Loss | → 4.0 | **3.76** | ✅ |
| S1 Acc | → 40% | **30.3%** | ⚠️ |

**4/5 targets met.** S1 accuracy trending up but needs **+9.7%** gain.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% / PPL 1.46, WikiText PPL 43.86, S1 loss 4.12
Pretrained GPT-2: LAMBADA 95.08%, WikiText PPL 29.07
**Current v3 AR performance on-track** (28.27 vs v1's 43.86). S1 system improving (**3.76 vs v1's 4.12**).

## Infrastructure
**21 spot sessions**, 8 reclaims in 3 days. Current: g6.2xlarge us-east-1b, 38min uptime. Major disruptions on 3/9 (**12 reclaims** in 6hrs). **Cost efficiency: 56.5% savings** vs on-demand.

## What's Next
**ETA 38min to completion.** Post-v3: benchmark suite, v1→v3 comparison analysis, confidence calibration deep-dive. **S1 accuracy** needs monitoring - currently underperforming target by 25%.