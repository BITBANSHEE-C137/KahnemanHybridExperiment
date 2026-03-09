# SITREP: v3 Training Progress

## v3 Training Status
**Step 17,800/50,000 (35.6% complete)**  
GPU: 98% util, A10G @ 51°C, 16.2GB/23GB VRAM  
Rate: ~500 steps/day, **ETA: 65 days**  
Spot cost: **$0.45/hr** (62.3% savings vs on-demand)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 10000 | 27.55  | 4.98      | 18.99% | 0.828 | 0.005 |
| 12000 | 28.12  | 4.31      | 25.03% | 0.853 | 0.007 |
| 14000 | 28.51  | 4.29      | 24.68% | 0.852 | 0.009 |
| 16000 | 28.66  | 4.38      | 23.53% | 0.856 | 0.010 |
| 17000 | **28.89** | **4.34** | **25.22%** | **0.858** | **0.008** |

**Trends:** AR perplexity **worsening** (+1.34 since step 10k). Diffusion loss improved then plateaued. S1 accuracy volatile but trending up. AUROC steady improvement. ECE well-controlled.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.89** | ✅ **MET** |
| AUROC > 0.75 | **0.858** | ✅ **MET** |
| ECE < 0.05 | **0.008** | ✅ **MET** |
| Diff loss → 4.0 | **4.34** | 🔶 **CLOSE** |
| S1 accuracy → 40% | **25.22%** | ❌ **MISS** |

**3/5 targets met.** Diffusion loss needs -0.34, S1 accuracy needs +14.78pp.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v3 AR performance ahead of v1 baseline** (28.89 vs 43.86 PPL)

## Infrastructure
**Current session:** 21.7h uptime, $9.90 spent, no interruptions  
**Previous session:** 6.8h, terminated cleanly, $3.11  
**Total cost:** $12.97 across 2 sessions  
Last checkpoint: step_17000.pt (1.5GB, synced)

## What's Next
**Concerning AR regression trend** - monitor next 5k steps closely. S1 accuracy improvement critical for dual-process effectiveness. Consider learning rate adjustment if AR continues degrading. v2 benchmarking blocked until training completes (~9 weeks at current rate).