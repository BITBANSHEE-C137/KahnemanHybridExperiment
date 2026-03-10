# v3 Training SITREP

## v3 Training Status
**Step 27,200/50,000 (54.4%)** - NVIDIA L4 @ 100% util, 79°C, 16.6/23GB VRAM  
Rate: ~137 steps/hr | ETA: **~6.9 days** | Spot cost: **$0.46/hr** (53% savings vs on-demand)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 20000 | 29.22  | 4.235     | 26.8%  | 0.857 | 0.0048 |
| 22000 | 29.70  | 3.945     | 28.3%  | **0.876** | 0.0039 |
| 25000 | 29.48  | 4.079     | 26.5%  | 0.861 | 0.0042 |
| 27000 | **29.55**  | **4.316**     | **24.6%**  | **0.866** | **0.0109** |

**Trends:** AR PPL stable ~29.5. **Diffusion loss regressing** (4.08→4.32). **S1 accuracy declining** (28.3%→24.6%). AUROC holding strong. **ECE degrading** (0.004→0.011).

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | **29.55** | ✅ **MET** |
| AUROC  | > 0.75 | **0.866** | ✅ **MET** |
| ECE    | < 0.05 | **0.011** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.32** | ❌ **REGRESSING** |
| S1 Accuracy | → 40% | **24.6%** | ❌ **DECLINING** |

**3/5 targets met.** S1 performance concerning - down from 28% peak.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v3 AR better than v1** (29.55 vs 43.86 PPL). S1 accuracy needs 15pp gain to hit 40% target.

## Infrastructure
**19 spot sessions, $22.54 total cost** - Multiple reclaims yesterday (9 instances terminated)  
Current g6.2xlarge stable 5.6hrs, projected $20.24 total vs $43.28 on-demand  
**Spot instability**: 11 reclaims between steps 20k-25k caused training delays

## What's Next
**Critical:** Monitor S1 accuracy decline - may need hyperparameter adjustment  
After v3: Full benchmark suite, confidence calibration analysis, v1/v2/v3 comparison  
Consider reducing LR if diffusion loss continues regressing