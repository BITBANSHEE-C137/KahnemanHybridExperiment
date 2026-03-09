# v3 Training SITREP - 2026-03-09 19:00Z

## v3 Training Status
**Step 20,200/50,000 (40.4%)** | L4 GPU 100% util @ 74W | **~30k steps remaining**  
Rate: ~16 steps/min | ETA: ~31 hours | Spot: **$0.43/hr** (57% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 13000 | 28.41 | 4.42 | 24.1% | 0.844 | 0.011 |
| 15000 | 28.64 | 4.50 | 23.7% | 0.864 | 0.005 |
| 17000 | 28.89 | 4.34 | 25.2% | 0.858 | 0.008 |
| 19000 | 29.21 | 4.39 | 22.1% | 0.866 | 0.011 |
| 20000 | **29.22** | **4.24** | **26.8%** | 0.857 | **0.005** |

**Trends**: AR PPL slowly degrading (+0.8 over 7k steps). Diff loss improving (-0.18). S1 accuracy volatile but recent uptick. AUROC stable ~0.86. ECE excellent <0.011.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.22** | ✅ **GOOD** |
| AUROC > 0.75 | **0.857** | ✅ **GOOD** |
| ECE < 0.05 | **0.005** | ✅ **EXCELLENT** |
| Diff loss → 4.0 | **4.24** | 🟡 **CLOSE** |
| S1 accuracy → 40% | **26.8%** | ❌ **LAGGING** |

## v1 Benchmark Baseline
v1 @ 50k: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
Current v3 AR regressing slightly vs v1, but diffusion improving beyond v1 target.

## Infrastructure
**12 spot reclaims** in 2 days! Frequent interruptions on g5/g6 instances across AZs.  
Total cost: **$15.87** (would be $36.41 on-demand)  
Current: g6.2xlarge us-east-1b, 32min uptime, stable at $0.43/hr

## What's Next
Monitoring S1 accuracy - needs +13% to hit target. AR PPL trend concerning but within bounds. After 50k: comprehensive v1/v3 benchmark comparison, confidence calibration analysis.