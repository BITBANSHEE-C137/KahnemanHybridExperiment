# v3 Training Status SITREP

## v3 Training Status
**COMPLETE** ✅ Step **50,000/50,000** (100%). Current instance idle - GPU 0% util, VRAM empty. Training completed at 01:08 UTC. Ready to begin v3 training run.

Current spot: **$0.48/hr** (60.8% savings vs on-demand $1.21/hr). Session cost: **$2.53**, total project: **$42.88**.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 43000 | 28.14 | 4.20 | 25.9% | 0.869 | 0.010 |
| 44000 | 28.07 | **4.40** | 24.9% | 0.867 | 0.010 |
| 45000 | 27.95 | 4.16 | 26.5% | 0.870 | 0.011 |
| 46000 | 28.13 | **3.94** | **28.1%** | 0.866 | 0.016 |
| 47000 | 28.09 | **3.88** | **29.3%** | 0.870 | 0.014 |
| 48000 | 28.04 | 4.19 | 26.1% | 0.870 | 0.012 |
| 49000 | 28.05 | **4.41** | 24.9% | 0.867 | 0.012 |
| 50000 | **27.99** | 4.16 | 26.5% | **0.870** | 0.012 |

**Trends**: AR PPL plateaued ~28, slight improvement to **27.99** final. Diffusion loss volatile (3.88→4.41), trending away from target. S1 accuracy peaked at **29.3%** (step 47k), regressed to 26.5%. AUROC stable **~0.87**, ECE excellent **<0.016**.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | <40 | **27.99** | ✅ **PASS** |
| AUROC | >0.75 | **0.870** | ✅ **PASS** |
| ECE | <0.05 | **0.012** | ✅ **PASS** |
| Diff Loss | →4.0 | **4.16** | ⚠️ **CLOSE** |
| S1 Accuracy | →40% | **26.5%** | ❌ **MISS** |

**3/5 targets met**. Missing S1 accuracy by **13.5pp**, diffusion loss **0.16** above target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL.

Current v2 AR PPL (**27.99**) beats v1 WikiText baseline (**43.86**) and approaches GPT-2 (**29.07**). S1 accuracy (**26.5%**) still underperforming vs target.

## Infrastructure
**23 spot sessions**, heavy reclaim activity mid-training (sessions 3-17). Stable g6.2xlarge runs for final 10k steps. Total cost **$40.35** across 4 days. Current instance: 5.3hr uptime, no issues.

Most expensive session: **$11.02** (g6.2xlarge, 13k steps). Cheapest: **$0.027** (4min g6.xlarge).

## What's Next
1. **v2 benchmarks**: LAMBADA, WikiText-103 evaluation on final checkpoint
2. **v1 vs v2 comparison**: Joint training impact analysis  
3. **Confidence head analysis**: AUROC/ECE performance deep dive
4. **v3 training prep**: Address S1 accuracy regression, diffusion loss volatility

**Ready to proceed with v2 evaluation phase.**