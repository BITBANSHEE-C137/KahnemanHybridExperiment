# SITREP: v2 Training Status Report

## v2 Training Status
**Step 14,300/50,000 (28.6% complete)**  
GPU: 100% util, NVIDIA A10G, 72% VRAM (16.6/23GB), 52°C  
Rate: ~10.8 steps/min based on uptime  
ETA: ~55 hours at current pace  
Spot cost: **$0.44/hr** (64% savings vs on-demand $1.21/hr)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Tok Acc | AUROC | ECE |
|------|--------|-----------|-------------|--------|-----|
| 7000 | 27.12 | 5.13 | 17.9% | 0.833 | 0.008 |
| 8000 | 27.58 | 4.65 | 21.1% | 0.845 | 0.007 |
| 10000 | 28.39 | 4.37 | 25.1% | 0.850 | 0.004 |
| 12000 | 29.35 | 4.34 | 25.6% | 0.852 | 0.009 |
| 14000 | 30.34 | 4.31 | 26.0% | 0.853 | 0.011 |

**⚠️ AR perplexity trending upward** - regression from 27.12→30.34  
**✅ Confidence AUROC steady** at ~0.85  
**⚠️ ECE degrading** - increased from 0.004→0.011  
**✅ Diffusion loss converging** toward target  

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **30.34** | ✅ PASS |
| AUROC | > 0.75 | **0.853** | ✅ PASS |
| ECE | < 0.05 | **0.011** | ✅ PASS |
| Diff Loss | → 4.0 | **4.31** | 🟡 CLOSE |
| S1 Accuracy | → 40% | **26.0%** | ❌ MISS |

**3/5 targets met**, S1 accuracy lagging significantly behind target pace.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% / PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
Current v2 AR performance (PPL 30.34) better than v1 WikiText baseline (43.86) but **concerning upward trend**.

## Infrastructure
**10 spot reclaims** in 48 hours - heavy churn in us-east-1b (6 reclaims)  
Current instance stable 47min in us-east-1f  
Total infrastructure cost: **$10.27** across all sessions  
Average session duration: ~3.2 hours before reclaim

## What's Next
**Immediate concern**: AR PPL regression needs investigation - possible overfitting to S1 task  
After completion: Full benchmark suite, analyze confidence calibration degradation, compare S1 task learning efficiency vs v1