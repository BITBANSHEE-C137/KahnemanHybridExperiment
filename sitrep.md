# v2 Training SITREP

## v2 Training Status
**Step 26,600/50,000 (53.2% complete)** | A10G @ 100% util, 194W/300W, 52°C | VRAM: 16.6/23GB  
Rate: ~2.34 steps/min | **ETA: ~17 hours** | Current spot: **$0.45/hr** (62.9% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 19000 | 30.81 | 4.31 | 24.5% | 0.860 | 0.007 |
| 20000 | 30.92 | 4.75 | 21.3% | 0.851 | 0.007 |
| 21000 | 30.88 | 4.85 | 20.7% | 0.851 | 0.007 |
| 22000 | 30.95 | 4.19 | 27.5% | 0.858 | 0.010 |
| 23000 | 31.03 | 4.03 | 27.9% | 0.864 | 0.010 |
| 24000 | 30.98 | 4.46 | 24.3% | 0.863 | 0.005 |
| 25000 | 31.22 | 4.20 | 27.6% | 0.860 | 0.012 |
| **26000** | **31.46** | **4.06** | **28.0%** | **0.863** | **0.018** |

**Trends:** AR PPL **stagnant** ~31 (concerning). Diff loss **improving** toward target. S1 accuracy **volatile** but trending up. AUROC **stable** ~0.86. ECE **degrading** recently.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **31.46** | ✅ **Met** |
| AUROC | > 0.75 | **0.863** | ✅ **Met** |
| ECE | < 0.05 | **0.018** | ✅ **Met** |
| Diff Loss | → 4.0 | **4.06** | ✅ **Nearly met** |
| S1 Accuracy | → 40% | **28.0%** | ❌ **70% to target** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% acc, 1.46 PPL | WikiText-103 43.86 PPL | S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Assessment:** v1 AR slightly regressed from joint training; S1 loss dropped 67%

## Infrastructure
**12 spot sessions** across 3 AZs | Total cost: **$18.0** (vs $38.3 on-demand)  
Current session: 3.3hrs uptime, no interruptions | **Spot stability: good** in us-east-1a  
Multiple reclaims yesterday (11 sessions), now stabilized on A10G

## What's Next
After v2 completion (~17hrs): Full benchmark suite, v1 vs v2 comparison, confidence calibration analysis. **Priority:** Address S1 accuracy plateau and ECE degradation in final 23k steps.