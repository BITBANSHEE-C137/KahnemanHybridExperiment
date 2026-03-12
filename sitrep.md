# v3 Training Status SITREP

## v3 Training Status
**99.8% complete** (49,900/50,000 steps). **~15 mins to completion**. GPU utilization **99%** on L4 (82°C, 72W/70W). Training rate ~1.67 steps/sec. Current spot: **$0.46/hr** (53% savings vs on-demand). **Total cost: $40.20** across 22 sessions.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|---------|--------|--------|
| 42000 | 28.33  | 3.89      | 29.1%   | 0.870  | 0.013  |
| 43000 | 28.14  | 4.20      | 25.9%   | 0.869  | 0.010  |
| 44000 | 28.07  | 4.40      | 24.9%   | 0.867  | 0.010  |
| 45000 | 27.95  | 4.16      | 26.5%   | 0.870  | 0.011  |
| 46000 | 28.13  | 3.94      | 28.1%   | 0.866  | 0.016  |
| 47000 | 28.09  | 3.88      | 29.3%   | 0.870  | 0.014  |
| 48000 | 28.04  | 4.19      | 26.1%   | 0.870  | 0.012  |
| 49000 | 28.05  | 4.41      | 24.9%   | 0.867  | 0.012  |

**AR PPL plateaued ~28**. **Diffusion loss oscillating 3.9-4.4** (not converging). **S1 accuracy volatile 25-29%** with downward drift. AUROC stable ~0.87, ECE excellent <0.02.

## Target Scorecard
| Target            | Current | Status |
|-------------------|---------|---------|
| AR PPL < 40       | **28.05** | ✅ MET |
| AUROC > 0.75      | **0.867** | ✅ MET |
| ECE < 0.05        | **0.012** | ✅ MET |
| Diff loss → 4.0   | **4.41**  | ❌ **+10% over target** |
| S1 accuracy → 40% | **24.9%** | ❌ **38% below target** |

**3/5 targets met**. Diffusion head struggling to converge. S1 performance concerning.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. **v3 AR significantly better than v1** (28 vs 44 PPL). S1 accuracy regression vs v1's implied ~67% improvement.

## Infrastructure
**22 spot sessions, 10 reclaims** (high churn). Mix of g5/g6 instances. Current g6.2xlarge stable 8.5hrs. **$40.16 total cost, 53% savings**. Frequent interruptions in us-east-1b (9 sessions), more stable in us-east-1a.

## What's Next
**Training completes in ~15min**. Priority: comprehensive v3 benchmarks, confidence calibration analysis, S1 head debugging. Compare v1→v3 joint training impact on individual components.