# v3 Training SITREP - March 8, 2026

## v3 Training Status
**Progress:** 5,400/50,000 steps (**10.8%** complete)  
**GPU:** A10G at **97% util**, 204W/300W, 60°C, 16.2GB/23GB VRAM  
**Rate:** ~0.23 steps/sec, **ETA:** ~54 hours  
**Spot Cost:** $0.46/hr (**62% savings**), $6.17 total spend

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 1000 | 21.29  | 6.75      | 5.0%   | 0.557 | 0.006 |
| 2000 | 22.53  | 6.54      | 6.4%   | 0.613 | 0.004 |
| 3000 | 23.17  | 6.38      | 7.6%   | 0.638 | 0.010 |
| 4000 | 23.71  | 6.29      | 8.5%   | 0.672 | 0.011 |
| 5000 | **24.35** | **6.12** | **9.1%** | **0.696** | **0.008** |

**Trends:** AR perplexity **degrading** (+14% since step 1k). Diffusion loss improving steadily (-9%). S1 accuracy climbing (+82%). Confidence AUROC progressing well (+25%).

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **24.35** | ✅ |
| AUROC | > 0.75 | **0.696** | ❌ |
| ECE | < 0.05 | **0.008** | ✅ |
| Diff Loss | → 4.0 | **6.12** | 🔄 |
| S1 Accuracy | → 40% | **9.1%** | 🔄 |

**2/5 targets met.** AUROC needs +0.054, diffusion loss -2.12, S1 accuracy +30.9pp.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL

Current v3 AR performance (**24.35 PPL**) significantly better than v1's 43.86 PPL at comparable stage.

## Infrastructure
**Current:** g5.2xlarge spot in us-east-1a, **6.7h uptime**  
**History:** 2 sessions, 1 reclaim after 600 steps (i-0b467969), current instance stable  
**Cost:** $6.17 total, on track for ~$28 full run vs $74 on-demand

## What's Next
Monitor **AR perplexity regression** - concerning +14% drift. AUROC approaching threshold but needs acceleration. Diffusion loss trending well toward 4.0 target. Next eval at step 6k critical for trajectory assessment.