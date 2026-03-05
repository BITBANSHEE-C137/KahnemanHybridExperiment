# v2 Training Status

**Step 21,300/50,000 (42.6% complete)** | GPU: 100% util, 53°C, 16.6/23GB VRAM | **Rate: ~400 steps/hr** | ETA: **~72 hours** | Current spot: **$0.44/hr** (64% savings vs on-demand)

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 14000 | 30.34  | 4.31      | 25.96% | 0.853 | 0.011  |
| 16000 | 30.79  | 4.13      | 26.82% | 0.860 | 0.007  |
| 18000 | 30.77  | 4.03      | 27.23% | **0.869** | 0.006 |
| 20000 | 30.92  | **4.75**  | 21.31% | 0.851 | 0.007  |
| 21000 | 30.88  | **4.85**  | **20.67%** | 0.851 | 0.007  |

**🔴 Regressions:** Diffusion loss climbing (+0.82 since step 18k), S1 accuracy dropping (-6.6pp). AUROC peaked at 18k, now plateaued.

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.88** | ✅ **MET** |
| AUROC > 0.75 | **0.851** | ✅ **MET** |
| ECE < 0.05 | **0.0075** | ✅ **MET** |
| Diff loss → 4.0 | **4.85** | 🔴 **REGRESSING** |
| S1 accuracy → 40% | **20.67%** | 🔴 **STALLED** |

## v1 Benchmark Baseline

v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v2 AR performance on track** (30.88 vs 43.86), but **S1 training unstable**.

## Infrastructure

**Current session:** 9.3hrs uptime, $4.06 spent. **Total cost:** $14.02 across 10 sessions. **Spot interruptions:** 9 reclaims (avg 2.1hrs/session). Instance hopping us-east-1b→1a→1f. **Stability improving** - current session longest yet.

## What's Next

**Priority:** Investigate S1 accuracy collapse and diffusion loss divergence. Consider learning rate adjustment or S1 loss weighting. After v2 completion: comprehensive benchmark suite, confidence calibration deep-dive, architectural analysis of dual-process interference.