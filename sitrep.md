# v3 Training SITREP

## v3 Training Status
**Step 28,900/50,000 (57.8% complete)** | GPU: L4 @ 100% util, 66°C | **Rate: ~300 steps/hr** | ETA: ~3 days | Current spot: **$0.457/hr** (53% savings) | Total cost: **$23.95**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 21000 | 29.94 | 4.26 | 26.8% | 0.856 | 0.012 |
| 22000 | 29.70 | **3.95** | **28.3%** | **0.876** | **0.004** |
| 23000 | 29.57 | 4.19 | 26.1% | 0.861 | 0.006 |
| 24000 | 29.53 | 4.31 | 25.2% | 0.862 | 0.005 |
| 25000 | 29.48 | 4.08 | 26.5% | 0.861 | 0.004 |
| 26000 | 29.58 | **4.02** | 27.7% | 0.864 | 0.006 |
| 27000 | 29.55 | 4.32 | 24.6% | 0.866 | 0.011 |
| 28000 | **29.40** | 4.51 | 23.8% | 0.865 | **0.007** |

**Trends:** AR perplexity slowly improving. **S1 accuracy regressing** (-5% from peak). Diffusion loss volatile, trending up. AUROC stable ~0.86. ECE excellent.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **29.4** | ✅ **PASS** |
| AUROC > 0.75 | **0.865** | ✅ **PASS** |
| ECE < 0.05 | **0.007** | ✅ **PASS** |
| Diff Loss → 4.0 | **4.51** | ❌ Stalled |
| S1 Acc → 40% | **23.8%** | ❌ **Regressing** |

## v1 Benchmark Baseline  
v1 (step 50k): LAMBADA 94.26% acc/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v3 AR already outperforms v1 WikiText baseline.**

## Infrastructure
**19 spot sessions**, 8+ reclaims in 48hrs. Heavy instability 3/9 18:00-22:00 UTC. Current g6.2xlarge stable 8.6hrs. **Total uptime efficiency: ~65%** due to frequent interruptions. Checkpoints syncing properly.

## What's Next
**Concerning S1 regression** - may indicate AR/diffusion interference intensifying. Monitor next 5k steps closely. Consider S1 loss weighting adjustment if trend continues. On track for 3/13 completion if spot stability improves.