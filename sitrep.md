# v2 Training SITREP

## v2 Training Status
**Step 29,900/50,000 (59.8%)** - A10G @ 100% util, 2.4 hrs remaining @ current rate  
Spot: $0.45/hr (63% savings vs $1.21 on-demand), **$1.10 session cost**  
Total project cost: **$20.08** across 13 sessions

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 22000 | 30.95  | 4.19      | 27.5%  | 0.858 | 0.010 |
| 24000 | 30.98  | 4.46      | 24.3%  | 0.863 | 0.005 |
| 26000 | 31.46  | 4.06      | 28.0%  | 0.863 | 0.018 |
| 28000 | 31.32  | 3.95      | 28.2%  | 0.872 | 0.007 |
| 29000 | **31.43** | **4.21** | **27.7%** | **0.860** | **0.022** |

**Trends**: AR PPL stable ~31.4 (good). Diffusion loss volatile but trending down. **AUROC regression** from 0.872 → 0.860. ECE spiked to 0.022 - **calibration degrading**.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **31.43** | ✅ **MET** |
| AUROC > 0.75 | **0.860** | ✅ **MET** |
| ECE < 0.05 | **0.022** | ✅ **MET** |
| Diff loss → 4.0 | **4.21** | 🔄 Close |
| S1 accuracy → 40% | **27.7%** | ❌ **MISS** |

**3/5 targets met**. S1 accuracy stuck at ~28%, needs **+12.3%** gain.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
Current v2 AR performance **better than v1** (31.4 vs 43.9 PPL)

## Infrastructure
**13 spot reclaims** - aggressive spot market. Current session stable 2.4hrs.  
Instance hopping: 2xlarge→xlarge→2xlarge pattern from pricing pressure  
**62.9% cost savings** vs on-demand, $20 total burn rate acceptable

## What's Next
ETA **6hrs to completion**. Post-v2: benchmark suite, confidence head deep-dive on ECE regression, S1 accuracy troubleshooting. **AUROC trending down** - monitor closely.