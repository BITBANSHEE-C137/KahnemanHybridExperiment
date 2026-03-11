# v3 Training SITREP

## v3 Training Status
**Step 48,100/50,000** (96.2% complete) | GPU: **98%** util on L4 @ 82°C | Rate: ~300 steps/hr | **ETA: 6.3 hrs** | Spot: **$0.463/hr** (53% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | AUROC | ECE | Diff Loss | S1 Acc |
|------|--------|-------|-----|-----------|--------|
| 41000| 28.30  | 0.866 | 0.011| 3.949    | 27.8%  |
| 42000| 28.33  | 0.870 | 0.013| 3.892    | 29.1%  |
| 43000| 28.14  | 0.869 | 0.010| 4.196    | 25.9%  |
| 44000| 28.07  | 0.867 | 0.010| 4.404    | 24.9%  |
| 45000| 27.95  | 0.870 | 0.011| 4.159    | 26.5%  |
| 46000| 28.13  | 0.866 | 0.016| 3.943    | 28.1%  |
| 47000| 28.09  | 0.870 | 0.014| 3.883    | 29.3%  |
| **48000**| **28.04** | **0.870** | **0.012**| **4.192** | **26.1%** |

**Trends**: AR perplexity **plateaued ~28**, excellent stability. AUROC **stable 0.87**. ECE **well-controlled <0.016**. Diffusion loss **volatile 3.9-4.4 range**. S1 accuracy **oscillating 25-29%**, no clear convergence.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | <40 | **28.04** | ✅ **PASS** |
| AUROC | >0.75 | **0.870** | ✅ **PASS** |
| ECE | <0.05 | **0.012** | ✅ **PASS** |
| Diff Loss | →4.0 | **4.192** | 🟡 **CLOSE** |
| S1 Accuracy | →40% | **26.1%** | ❌ **FAIL** |

**3/5 targets met**. S1 accuracy **significantly underperforming** - only 65% of target.

## v1 Benchmark Baseline
v1 achieved LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. Current v3 AR performance (**PPL 28**) is **36% better** than v1 WikiText. However, S1 accuracy at 26% vs v1's implied performance suggests **joint training degradation**.

## Infrastructure
Current session: **5.5hrs uptime**, $2.53 spent. **22 spot reclaims** historically - frequent interruptions on 3/9 (11 reclaims), then **stable 24hr+ sessions** since 3/10. Total cost **$38.77** across 48k steps. L4 instance **running hot** at 82°C but within limits.

## What's Next
**1,900 steps to completion**. Post-v3: comprehensive benchmarking vs v1, investigate **S1 accuracy regression**, analyze confidence calibration performance, optimize diffusion stability.