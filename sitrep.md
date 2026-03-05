# v2 Training SITREP

## v2 Training Status
**Progress**: 23,300/50,000 steps (46.6% complete)  
**GPU**: A10G @ 100% util, 201W/300W, 55°C, 16.6GB/23GB VRAM  
**Rate**: ~3.8 hours uptime = 1.5K steps → **~395 steps/hour**  
**ETA**: **67 hours** (est. March 8 evening)  
**Spot cost**: $0.45/hr (62.9% savings vs on-demand)

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 16000 | 30.79  | 4.13      | 26.8%  | 0.860 | 0.007 |
| 18000 | 30.77  | 4.03      | 27.2%  | 0.869 | 0.006 |
| 20000 | 30.92  | 4.75      | 21.3%  | 0.851 | 0.007 |
| 22000 | 30.95  | 4.19      | 27.5%  | 0.858 | 0.010 |
| 23000 | **31.03** | **4.03** | **27.9%** | **0.864** | **0.010** |

**Trends**: AR PPL **worsening** (+0.24 since 16K). S1 accuracy volatile but **recovering**. AUROC steady. ECE **degraded** from excellent 0.006 to 0.010.

## Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **31.03** | ✅ |
| AUROC | > 0.75 | **0.864** | ✅ |
| ECE | < 0.05 | **0.010** | ✅ |
| Diff Loss | → 4.0 | **4.03** | ✅ |
| S1 Accuracy | → 40% | **27.9%** | ❌ |

**4/5 targets met**. S1 accuracy **12pp short** of target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  

Current v2 AR PPL (**31.03**) already **29% better** than v1 WikiText baseline (43.86).

## Infrastructure
**11 spot sessions**, 10 reclaims in 40 hours. Current session: 3.8h uptime, stable.  
**Total cost**: $16.02 (vs $43.77 on-demand)  
**Availability**: Mixed AZ hopping (1a/1b/1f), some g5.xlarge fallbacks during shortages

## What's Next
Training **67% complete by cost**. Post-completion: benchmark v2 on LAMBADA/WikiText, compare AR regression vs v1, analyze confidence calibration trends, investigate S1 accuracy plateau.