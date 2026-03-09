# v3 Training SITREP

## v3 Training Status
**Step 13,600/50,000** (27.2% complete) | GPU: **98.0%** util, 51°C | Rate: ~6.9 steps/min | **ETA: ~88 hours** | Spot: **$0.46/hr** (-62% vs on-demand)

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 6000  | 24.85  | 6.08      | 9.9%   | 0.719 | 0.012 |
| 8000  | 26.29  | 5.60      | 12.6%  | 0.785 | 0.008 |
| 10000 | 27.55  | 4.98      | 19.0%  | 0.828 | 0.005 |
| 12000 | 28.12  | 4.31      | 25.0%  | 0.853 | 0.007 |
| **13000** | **28.41** | **4.42** | **24.1%** | **0.844** | **0.011** |

**Trends**: AR PPL degrading steadily (+14% since step 6k). Diffusion loss converging well (-27%). **S1 accuracy plateaued/regressed** last 1k steps. AUROC strong but **stalled**. ECE volatile but acceptable.

## Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **28.41** | ✅ **MET** |
| AUROC | > 0.75 | **0.844** | ✅ **MET** |  
| ECE | < 0.05 | **0.011** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.42** | 🟡 **90% there** |
| S1 Accuracy | → 40% | **24.1%** | 🔴 **60% to target** |

## v1 Benchmark Baseline
v1 (50k steps): LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. GPT-2 baseline: 95.08%/29.07 PPL. **Current v3 AR PPL significantly better** than v1 final (28.4 vs 43.9), suggesting improved joint training balance.

## Infrastructure
**Session 2** running 16.7h | Total cost: **$10.70** ($7.59 current session) | **No spot reclaims** | 70% VRAM usage (16.2GB/23GB) | Checkpoints syncing normally

## What's Next
Training progressing well on AR/confidence metrics but **S1 accuracy stagnation concerning**. Monitor S1 learning rate scheduling. ETA completion: **March 13th**. Post-completion: comprehensive v1/v2/v3 benchmark suite, confidence calibration analysis.