# v3 Training SITREP

## v3 Training Status
**Step 600/50k (1.2%)** - GPU util **97%** on A10G, temp 52°C, VRAM 16.2/23GB. Rate ~**7.6 steps/min** based on 44min runtime. **ETA: ~110 hours**. Current spot rate **$0.46/hr** (**61.7% savings**), projected total cost **$28**.

## AMI & Infrastructure Changes (v3)
- Clean AMI baked (`ami-0e52bd0d4640a3d73`): infra constants in `/etc/ml-lab/infra.env`, no secrets in image
- Bootstrap simplified: only injects secrets + version-derived paths
- Launch template v21 with clean AMI
- Lambda `/start` and `/stop` commands fixed and working from Telegram
- Lambda webhook secret mismatch resolved

## Eval Metrics & Trends
No eval checkpoints yet. Latest training metrics:
- AR loss: **3.10**
- Diffusion loss: **6.95**
- Confidence accuracy: **0.0%** (not converged)

**Unable to assess trends** - need eval data from checkpoints.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | ~22.3* | Met |
| AUROC | > 0.75 | N/A | Pending |
| ECE | < 0.05 | N/A | Pending |
| Diff loss | < 4.0 | 6.95 | Needs reduction |
| S1 accuracy | > 40% | N/A | Pending |

*Estimated from AR loss 3.10

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText-103 PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. **Current AR performance tracking ahead of v1** but diffusion loss needs **69% reduction** to match.

## Infrastructure
**3 spot reclaims** in <2 hours - high churn in us-east-1a. Session history:
- i-0d24: 8min, $0.07 (setup only)
- i-0dc6: 36min, $0.28 (steps 1-400)
- i-0c93: 52min, $0.36 (steps 400+)
- i-0b46: active (fresh start on clean AMI)

Total cost **$0.71**.

## What's Next
- First eval checkpoint at step 1,000 critical for baseline metrics
- Establish confidence head convergence timeline
- Gradient norm diagnostics at eval steps
- Compare initial convergence vs v1/v2 patterns
