# v3 Training SITREP

## v3 Training Status
**Step 24,100 / 50,000** (48.2% complete). GPU at **100% utilization** (A10G, 52°C, 16.6GB VRAM used). Current rate: ~400 steps/hr. **ETA: 2.7 days**. Spot cost: **$0.48/hr** (60.7% savings vs on-demand).

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|--------|-----|
| 17000 | 28.89 | 4.344 | 25.2% | 0.858 | 0.0079 |
| 20000 | 29.22 | **4.235** | **26.8%** | 0.857 | **0.0048** |
| 22000 | 29.70 | **3.945** | **28.3%** | **0.876** | **0.0039** |
| 23000 | 29.57 | 4.192 | 26.1% | 0.861 | 0.0059 |
| 24000 | **29.53** | 4.309 | 25.2% | 0.862 | **0.0055** |

**Trends:** AR perplexity stable ~29.5. **Diff loss regressed** from 3.95→4.31. S1 accuracy volatile (peak 28.3% at step 22k, now 25.2%). AUROC holding ~0.86. ECE excellent <0.006.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | <40 | **29.53** | ✅ **Met** |
| AUROC | >0.75 | **0.862** | ✅ **Met** |
| ECE | <0.05 | **0.0055** | ✅ **Met** |
| Diff Loss | →4.0 | **4.31** | ❌ **Regressed** |
| S1 Accuracy | →40% | **25.2%** | ❌ **Behind** |

**3/5 targets met**. Diffusion loss and S1 accuracy underperforming.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. 

Current v3 AR performance **better than v1** (29.53 vs 43.86 WikiText). S1 accuracy at 25.2% vs v1's ~67% drop from 4.12 loss.

## Infrastructure
**18 spot reclaims** in 2.5 days - extremely unstable. Current session: 5.2hrs uptime on g5.2xlarge. Total cost: **$19.60** across all sessions. Frequent instance type switching (g5.2xl→g6.xl→g6.2xl) due to availability.

## What's Next
**Critical:** Investigate diffusion loss regression since step 22k. Consider checkpoint rollback to 22k if trend continues. After v3 completion: comprehensive v1/v2/v3 benchmark suite, confidence calibration analysis.