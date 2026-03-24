## v4 Training Status
**55.73%** complete (step **41.8K**/75K). GPU @ **100%** utilization, **56°C**, 16.6GB VRAM used. Current rate: ~133 steps/hr. **ETA: ~9.7 days**. Spot cost: **$0.44/hr** (63.8% savings vs on-demand).

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 38000 | 29.43 | 4.38 | 27.7% | 0.856 | 0.016 |
| 39000 | **29.17** | 4.08 | **30.5%** | 0.857 | **0.008** |
| 40000 | 29.05 | **3.79** | **32.7%** | **0.862** | 0.018 |
| 41000 | **28.84** | 3.94 | 30.9% | **0.864** | 0.016 |
| 41500 | 28.88 | 4.02 | 30.7% | 0.863 | **0.011** |

**Trends**: AR PPL steadily improving (**-0.6** from 38K). S1 accuracy peaked at 40K then **regressed 2%**. AUROC trending up (+0.007). ECE volatile but improving. Diffusion loss volatile around 4.0.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.88** | ✅ **BEAT** |
| AUROC > 0.75 | **0.863** | ✅ **BEAT** |
| ECE < 0.05 | **0.011** | ✅ **BEAT** |
| Diff loss → 4.0 | **4.02** | ✅ **AT TARGET** |
| S1 accuracy → 40% | **30.7%** | ❌ **Need +9.3%** |

## v1 Benchmark Baseline
v1 (50K): LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. **Current v4 AR PPL already 34% better than v1**. S1 accuracy tracking behind v1's final performance.

## Infrastructure  
Current session: **12.5hrs** uptime, $5.50 spot cost. **Total: 73 sessions, $53.88 cost**. Multiple short-lived sessions 19-21 Mar suggest **heavy spot reclaims**. Current g5.2xlarge in us-east-1e stable since midnight.

## What's Next
Monitor S1 accuracy regression—may need hyperparameter adjustment if trend continues. Strong AR performance suggests good dual-process balance. After v4: comprehensive benchmarking vs v1, confidence calibration analysis, potential early stopping if targets sustained.