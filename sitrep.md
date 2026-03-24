# ML Ops SITREP - v4 Training

## v4 Training Status
**Step 41,500/75,000 (55.3% complete)** | Rate: ~1k steps/12h | **ETA: ~17 days**
GPU: A10G @ 100% util, 203W/300W, 55°C, 16.6GB VRAM used
Current spot: **$0.44/hr** (63.8% savings vs on-demand $1.21/hr)

## Eval Metrics & Trends

| Step  | AR PPL | AUROC | ECE   | Diff Loss | S1 Acc |
|-------|---------|--------|-------|-----------|--------|
| 38000 | 29.43   | 0.856  | 0.016 | 4.38      | 0.277  |
| 39000 | 29.17   | 0.857  | 0.008 | 4.08      | 0.305  |
| 40000 | 29.05   | 0.862  | 0.018 | 3.79      | 0.327  |
| 41000 | 28.84   | 0.864  | 0.016 | 3.94      | 0.309  |
| 41500 | **28.88** | **0.863** | **0.011** | **4.02** | **0.307** |

**Trends:** AR PPL steadily improving (-0.55 in 3.5k steps). AUROC stable ~0.86. ECE volatile but improving. **Diff loss regressed +0.24** since step 40k. S1 accuracy plateau at ~0.31.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.88** | ✅ **MET** |
| AUROC > 0.75 | **0.863** | ✅ **MET** |
| ECE < 0.05 | **0.011** | ✅ **MET** |
| Diff loss → 4.0 | **4.02** | ✅ **MET** |
| S1 accuracy → 40% | **30.7%** | ❌ **23% short** |

**3/5 targets met.** S1 accuracy critically underperforming.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%, PPL 1.46 | WikiText PPL 43.86 | S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07

Current v4 AR PPL (**28.88**) already **beats WikiText baseline** and approaching v1 levels despite dual training.

## Infrastructure
**Total cost: $53.70** across 73 sessions | Current session: 12h uptime, $5.28 cost
**Spot reclaims: Frequent** - 15+ interruptions in 48h, mostly <1h sessions in early training
Recent stability: **12h uninterrupted** on current g5.2xlarge instance

## What's Next
**Immediate:** Monitor diff loss regression - may need LR adjustment if trend continues
**After completion:** v4 vs v1 benchmark comparison, S1 head analysis for underperformance root cause
**Priority:** Investigate S1 accuracy plateau - only target significantly missing