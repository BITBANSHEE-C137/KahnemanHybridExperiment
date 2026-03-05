# ML Ops SITREP - v2 Training

## v2 Training Status
**Step 13,800/50,000** (27.6% complete) | GPU: 99% util @ 201W/300W, 52°C | Current instance: g5.xlarge spot @ $0.42/hr (57.7% savings) | **ETA: ~40 hours** at current pace | Total cost: **$9.61**, projected **$35**

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | Conf AUROC | Conf ECE |
|-------|--------|-----------|--------|------------|----------|
| 6000  | 26.44  | 5.12      | 17.5%  | 0.830      | 0.005    |
| 8000  | 27.58  | 4.65      | 21.1%  | 0.845      | 0.007    |
| 10000 | 28.39  | 4.37      | 25.1%  | 0.850      | 0.004    |
| 11000 | 28.91  | 4.19      | 26.0%  | 0.857      | 0.005    |
| 13000 | 30.50  | 4.40      | 25.5%  | 0.852      | 0.012    |

**Trends**: AR PPL degrading (+15% since step 6k). S1 accuracy plateaued at ~25%. Confidence AUROC solid but ECE rising (**regression**). Diffusion loss volatile but trending down.

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.5** | ✅ |
| AUROC > 0.75 | **0.852** | ✅ |
| ECE < 0.05 | **0.012** | ✅ |
| Diff loss → 4.0 | **4.40** | 🔶 Close |
| S1 accuracy → 40% | **25.5%** | ❌ Stalled |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText-103 PPL 43.86, S1 loss 4.12. v2 AR performance **worse** than v1 (30.5 vs expected ~26 PPL). S1 training progressing but **behind target**.

## Infrastructure
**9 spot reclaims** in 24h - highly unstable. Downgraded to g5.xlarge after frequent g5.2xlarge interruptions. Current session: 1.9h uptime. Total interruption overhead: ~3-4 hours. **Spot market brutal**.

## What's Next
Training unstable but progressing. **Critical**: S1 accuracy plateau needs investigation - potential LR adjustment. After v2: comprehensive v1/v2 benchmark comparison, confidence calibration analysis, spot strategy review.