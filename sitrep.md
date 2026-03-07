## v2 Training Status
**Step 47,300/50,000 (94.6%)** | GPU: **99% util** A10G @ 198W/50°C | Rate: ~35 steps/hr | **ETA: ~3 days** | Spot: **$0.46/hr** (62% savings vs on-demand)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 40000 | 30.21  | 4.56      | 23.2%  | 0.857 | 0.007 |
| 43000 | 29.96  | 3.93      | 29.2%  | 0.868 | 0.020 |
| 45000 | 29.80  | 3.86      | 29.3%  | 0.875 | 0.016 |
| 47000 | **29.72** | **4.61** | **22.8%** | **0.855** | **0.011** |

**Trends:** AR PPL steadily improving ✓. **Diffusion loss regressed** from 3.86→4.61. S1 accuracy **volatile, trending down**. AUROC peaked at 45k, now declining. ECE stable.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | **29.72** | ✅ |
| AUROC  | > 0.75 | **0.855** | ✅ |
| ECE    | < 0.05 | **0.011** | ✅ |
| Diff Loss | → 4.0 | **4.61** | ❌ |
| S1 Acc | → 40% | **22.8%** | ❌ |

**3/5 targets met**. Diffusion loss and S1 accuracy **both regressing** in recent steps.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. **Current v2 AR PPL (29.72) matches GPT-2 baseline** - significant improvement over v1's 43.86.

## Infrastructure
**15 spot sessions**, **$29.94 total cost**. Current instance: 7.8hrs uptime, stable. History shows **frequent reclaims** (avg 5.3hr sessions). Recent stability improved - longest session was 16hrs (steps 28.6k-41k).

## What's Next
Training completes ~3 days. **Critical:** Monitor diffusion/S1 regression trend. After completion: comprehensive v2 benchmarks, v1→v2 comparison analysis, investigate confidence head calibration at peak AUROC (step 45k).