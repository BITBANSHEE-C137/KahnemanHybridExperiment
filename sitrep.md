# SITREP: v2 Training Status

## v2 Training Status
**Step 36,100/50,000 (72.2%)** | GPU: 100% util, 196W/300W | Rate: ~400 steps/h | **ETA: 34hrs** | Spot: $4.50 ($0.45/hr, 62.7% savings vs on-demand)

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 29k  | 31.43  | 4.21      | 27.7%  | 0.860 | 0.022 |
| 30k  | 31.68  | 4.08      | 28.1%  | 0.864 | 0.023 |
| 32k  | 31.39  | 3.96      | 28.4%  | **0.871** | 0.013 |
| 34k  | 31.13  | 4.68      | 22.0%  | 0.854 | 0.009 |
| 35k  | 30.84  | 4.79      | 21.4%  | 0.855 | 0.011 |
| **36k** | **30.69** | **4.30** | **24.8%** | **0.863** | **0.010** |

**Trends:** AR PPL steadily improving ✓ | Diff loss volatile, spiked at 35k | S1 acc recovering from 34k dip | AUROC stable ~0.86 | ECE excellent <0.02

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.69** | ✅ **PASS** |
| AUROC > 0.75 | **0.863** | ✅ **PASS** |  
| ECE < 0.05 | **0.010** | ✅ **PASS** |
| Diff Loss → 4.0 | **4.30** | ⚠️ **Close** (trending down) |
| S1 Acc → 40% | **24.8%** | ❌ **MISS** (62% of target) |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. **v2 AR significantly outperforming** (30.69 vs 43.86 PPL). S1 acc needs 15pp improvement to match v1's implied performance.

## Infrastructure
**13 spot sessions, $23.47 total** | Current: 9.9hr uptime, no interruptions | A10G running cool (52°C) | **Spot reliability strong** - longest session 10hrs

## What's Next
**14k steps remaining (~34hrs)** | Monitor diff loss convergence to 4.0 | S1 acc critical - investigate if joint training limiting System 1 | Post-completion: v2 benchmarks, head analysis, v1→v2 performance delta deep-dive