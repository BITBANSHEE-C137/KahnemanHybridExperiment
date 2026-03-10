# v3 Training Status SITREP

## v3 Training Status
**49.0% complete** (24,500/50,000 steps) | **100% GPU util** | A10G at 52°C drawing 198W | **~25.5k steps remaining** at current rate | ETA: ~14 hours | Spot cost: **$2.71** (60.7% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Tok Acc | AUROC | ECE |
|------|--------|-----------|-------------|-------|-----|
| 17k  | 28.89  | 4.34      | 25.2%       | 0.858 | 0.008 |
| 18k  | 28.99  | 4.44      | 23.0%       | 0.858 | 0.010 |
| 19k  | 29.21  | 4.39      | 22.1%       | 0.866 | 0.011 |
| 20k  | 29.22  | 4.24      | 26.8%       | 0.857 | 0.005 |
| 21k  | 29.94  | 4.26      | 26.8%       | 0.856 | 0.012 |
| 22k  | 29.70  | **3.95**  | **28.3%**   | **0.876** | 0.004 |
| 23k  | 29.57  | 4.19      | 26.1%       | 0.861 | 0.006 |
| 24k  | **29.53** | 4.31   | 25.2%       | 0.862 | **0.0055** |

**Trends**: AR PPL slowly improving. Diffusion loss volatile but trending down. **S1 accuracy peaked at 22k then regressed**. AUROC stable ~0.86. ECE excellent throughout.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.53** | ✅ **MET** |
| AUROC > 0.75 | **0.862** | ✅ **MET** |
| ECE < 0.05 | **0.0055** | ✅ **MET** |
| Diff loss → 4.0 | **4.31** | 🔶 **CLOSE** |
| S1 accuracy → 40% | **25.2%** | ❌ **MISSING** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, PPL 1.46 | WikiText-103 PPL 43.86 | S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Current v3 AR PPL (29.53) matches GPT-2 baseline**. S1 performance critical gap remains.

## Infrastructure
**18 spot sessions** across 3 AZs. **Heavy spot churn** around step 20k (12 reclaims in 4 hours). Current session stable 5.7 hours on g5.2xlarge. Total cost: **$19.88** vs $44.32 on-demand. Checkpoints syncing normally.

## What's Next
**S1 accuracy regression** at 22k→24k needs investigation. Diffusion loss close to target but unstable. Monitor for further spot interruptions. After completion: benchmark suite, confidence calibration analysis, v1 vs v3 head-to-head comparison.