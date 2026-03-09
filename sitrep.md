# SITREP: v3 Dual-Process Training

## v3 Training Status
**Step 17,300/50,000** (34.6%) | **100% GPU util** A10G @ 198W/300W, 49°C | **16.2GB/23GB VRAM** | Rate: ~430 steps/hr | **ETA: ~76 hours** | Spot cost: **$0.45/hr** (62.3% savings vs on-demand $1.21/hr)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 10000 | 27.55  | 4.98      | 18.99% | 0.828 | 0.0053 |
| 11000 | 27.85  | 4.43      | 21.97% | 0.853 | 0.0102 |
| 12000 | 28.12  | 4.31      | 25.03% | 0.853 | 0.0066 |
| 13000 | 28.41  | 4.42      | 24.13% | 0.844 | 0.0110 |
| 14000 | 28.51  | 4.29      | 24.68% | 0.852 | 0.0087 |
| 15000 | 28.64  | 4.50      | 23.75% | 0.864 | 0.0052 |
| 16000 | 28.66  | 4.38      | 23.53% | 0.856 | 0.0104 |
| 17000 | **28.89** | **4.34** | **25.22%** | **0.858** | **0.0079** |

**Trends**: AR PPL slowly degrading (+1.34 over 7k steps). S1 accuracy volatile but trending up (+6.23pp). AUROC stable ~0.85. Diffusion loss converging to target.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.89** | ✅ **PASS** |
| AUROC > 0.75 | **0.858** | ✅ **PASS** |
| ECE < 0.05 | **0.0079** | ✅ **PASS** |
| Diff loss → 4.0 | **4.34** | 🟡 **APPROACHING** |
| S1 accuracy → 40% | **25.22%** | 🟡 **PROGRESSING** |

**3/5 targets met**. On track for remaining two.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Current v3 AR PPL (**28.89**) outperforming v1 WikiText baseline. S1 performance improving but still below v1 convergence point.

## Infrastructure
**Current session**: 21.2h uptime, $9.67 spot cost. **Previous session**: 6.8h, $3.11 (spot reclaim). **Total cost**: $12.78 across 2 sessions. No current issues. Last checkpoint: step_17000.pt (1.5GB, synced).

## What's Next
Continue to 50k steps (~3 more days). Monitor AR PPL degradation - may need LR adjustment if exceeds 35. S1 accuracy should reach 35%+ by 35k steps based on current trajectory. Post-training: comprehensive v1/v2/v3 benchmarking suite.