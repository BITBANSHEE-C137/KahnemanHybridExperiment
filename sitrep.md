# v4 Training Status

**Step 39,800/75,000 (53.1%)** | A10G @ 100% util, 204W/300W | **1.26 steps/sec** | ETA: **7.8 hrs** | Spot: **$0.44/hr** (64% savings)

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|---------|-----------|--------|-------|-----|
| 36000 | 31.11 | 4.200 | 29.9% | 0.864 | 0.021 |
| 37000 | 30.10 | 4.337 | 27.7% | 0.854 | 0.020 |
| 38000 | 29.43 | 4.382 | 27.7% | 0.856 | 0.016 |
| 39000 | 29.17 | 4.082 | 30.5% | 0.857 | 0.008 |
| **39500** | **29.10** | **4.366** | **26.9%** | **0.855** | **0.016** |

**Strong AR convergence** (PPL -6.5%), **diffusion loss volatile** around 4.3, **S1 accuracy regressed** from 30.5% → 26.9%. **Confidence calibration excellent** (ECE < 0.02).

## Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **29.1** | ✅ **PASS** |
| AUROC | > 0.75 | **0.855** | ✅ **PASS** |
| ECE | < 0.05 | **0.016** | ✅ **PASS** |
| Diff Loss | → 4.0 | **4.37** | ⚠️ **Near target** |
| S1 Accuracy | → 40% | **26.9%** | ❌ **33% below** |

**3/5 targets met**. S1 accuracy **struggling vs v1 baseline (40.9%)**.

## v1 Benchmark Baseline

v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **Current AR performance exceeds v1** (29.1 vs 43.86 PPL). S1 accuracy **significantly worse** than v1's implied 40.9%.

## Infrastructure

**73 spot sessions**, **$52.34 total cost**. Current session: 9h uptime, **$3.96 cost**. **Heavy spot reclaim history** - 20+ micro-sessions < 1hr indicating aggressive market conditions. **Stable since midnight** on g5.2xlarge us-east-1e.

## What's Next

**36k steps remaining** (~29 hrs). Monitor **S1 accuracy recovery** - may need learning rate adjustment. Post-completion: comprehensive benchmarking vs v1, confidence head ablation studies, diffusion loss convergence analysis.