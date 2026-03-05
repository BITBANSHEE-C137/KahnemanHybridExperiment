# SITREP v2 Training Status Report

## v2 Training Status
**Step 14,300/50,000** (28.6% complete) | **GPU: 100% util** A10G @ 51°C, 16.6/23GB VRAM | **Rate:** ~2.52 steps/min | **ETA:** ~10 days | **Spot cost:** $0.42/hr (57.7% savings vs on-demand)

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 7k   | 27.12  | 5.13      | 17.9%   | 0.833 | 0.008 |
| 8k   | 27.58  | 4.65      | 21.1%   | 0.845 | 0.007 |
| 9k   | 28.06  | 5.02      | 18.9%   | 0.843 | 0.006 |
| 10k  | 28.39  | 4.37      | 25.1%   | 0.850 | 0.004 |
| 11k  | 28.91  | 4.19      | 26.0%   | 0.857 | 0.005 |
| 12k  | 29.35  | 4.34      | 25.6%   | 0.852 | 0.009 |
| 13k  | 30.50  | 4.40      | 25.5%   | 0.852 | 0.012 |
| 14k  | **30.34** | **4.31** | **26.0%** | **0.853** | **0.011** |

**Trends:** AR PPL degrading (+12% since 7k). AUROC plateaued ~0.85. ECE creeping up. **S1 accuracy stalled** at ~25-26%.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40   | **30.34** | ✅ |
| AUROC  | > 0.75 | **0.853** | ✅ |
| ECE    | < 0.05 | **0.011** | ✅ |
| Diff Loss | → 4.0 | **4.31** | 🟡 Close |
| S1 Acc | → 40% | **26.0%** | ❌ **Far behind** |

**3/5 targets met.** S1 accuracy is biggest concern—stuck well below target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. **Current v2 AR PPL (30.34) already better than v1 WikiText (43.86)** but still worse than GPT-2.

## Infrastructure
**9 sessions, 8 spot reclaims** in 24hrs. Total cost: **$9.82** ($1.37 saved vs on-demand). Current g5.xlarge stable 2.5hrs. Multiple brief sessions suggest **high spot pressure in us-east-1b**, better stability in us-east-1f.

## What's Next
**Critical:** S1 accuracy plateau needs investigation—may require hyperparameter adjustment or architectural fix. Continue monitoring AR PPL regression. After completion: full v2 benchmarks, confidence calibration analysis, v1→v2 delta assessment.