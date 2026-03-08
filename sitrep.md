# v3 Training SITREP

## v3 Training Status
**Step 7000/50000 (14.0%)** | GPU: A10G @ **100% util**, 206W/300W, 60°C | VRAM: 16.2/23.0GB | Rate: **0.23 steps/sec** | ETA: **~211 hours** | Spot cost: **$0.458/hr** (62% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 1000 | 21.29  | 6.75      | 5.0%    | 0.557 | 0.0057 |
| 3000 | 23.17  | 6.38      | 7.6%    | 0.638 | 0.0100 |
| 5000 | 24.35  | 6.12      | 9.1%    | 0.695 | 0.0082 |
| 7000 | **25.48** | **5.87** | **10.6%** | **0.739** | **0.0089** |

**Trends:** AR perplexity **degrading** (+4.2 since step 1k). Diffusion loss **improving** (-0.88). S1 accuracy **steadily climbing** (+5.5%). AUROC **strong upward trend** (+0.18). ECE stable around 0.01.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40   | **25.48** | ✅ **MET** |
| AUROC  | > 0.75 | **0.739** | ⚠️ **CLOSE** (-0.011) |
| ECE    | < 0.05 | **0.0089** | ✅ **MET** |
| Diff Loss | → 4.0 | **5.87** | 🔄 **PROGRESS** |
| S1 Acc | → 40%  | **10.6%** | 🔄 **PROGRESS** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%/WikiText 29.07 PPL. **Current v3 AR PPL (25.48) already better than v1 baseline (43.86)** - promising early signal.

## Infrastructure
**Current session:** 8.7hrs uptime, $3.98 spot cost. **Previous session:** Terminated after 6.8hrs at step 1000, $3.11 cost. **Total cost: $7.05** across 2 sessions. No spot reclaims during active training. Checkpointing every 1k steps (1.5GB each).

## What's Next
**AUROC on track to hit 0.75** within ~500 steps. **AR PPL regression concerning** - monitor for overfitting. S1 accuracy climbing too slowly for 40% target. After v2 completes: confidence calibration analysis, AR/diffusion loss balance tuning.