# v3 Training SITREP

## v3 Training Status
**Step 16,100/50,000** (32.2%) | GPU: **100% util** A10G @ 51°C | **0.23 steps/sec** | ETA: **40.8h** | Spot cost: **$8.99** (62.3% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 16000 | **28.66** | 4.38 | 23.5% | **0.856** | **0.010** |
| 15000 | 28.64 | 4.50 | 23.7% | **0.864** | **0.005** |
| 14000 | 28.51 | 4.29 | 24.7% | 0.852 | 0.009 |
| 13000 | 28.41 | 4.42 | 24.1% | 0.844 | 0.011 |

**Trends:** AR perplexity **plateauing** around 28.6 (good). AUROC **volatile** but holding >0.84. S1 accuracy **stagnant** at ~23.5%. ECE fluctuating but controlled.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **28.66** | ✅ **MET** |
| AUROC > 0.75 | **0.856** | ✅ **MET** |
| ECE < 0.05 | **0.010** | ✅ **MET** |
| Diff loss → 4.0 | **4.38** | 🔶 **90% there** |
| S1 accuracy → 40% | **23.5%** | ❌ **59% to go** |

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12
Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL
**Current v3 AR performance tracking ahead of v1 baseline.**

## Infrastructure
**Current session:** 19.7h uptime, **2 spot reclaims** total. Session costs: $3.11 + $8.95 = **$12.06** total.
**Stability:** Good - no recent interruptions. Checkpoints syncing properly (1.5GB each).

## What's Next
**Critical:** S1 accuracy badly lagging targets - investigate S1 head learning dynamics. Diff loss needs **0.4 point drop**. After step 20k: deep dive on confidence calibration stability. ETA completion: **Mar 11 02:00 UTC**.