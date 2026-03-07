# v2 Training SITREP

## v2 Training Status
**Step 48,500/50,000 (97.0%)** | A10G @ 100% util, 201W/300W | **ETA: ~45 min** | Spot: $0.46/hr (61.8% savings) | Current run cost: **$4.31**

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 41000 | 30.12  | 4.47      | 25.1%  | 0.862 | 0.012 |
| 43000 | 29.96  | 3.93      | 29.2%  | 0.868 | 0.020 |
| 45000 | 29.80  | 3.86      | 29.3%  | 0.875 | 0.016 |
| 47000 | 29.72  | 4.61      | 22.7%  | 0.855 | 0.011 |
| 48000 | **29.72** | **4.73** | **21.9%** | **0.858** | **0.012** |

**Trends**: AR PPL plateaued ~30. **S1 accuracy regressing** (29.3% → 21.9%). Diff loss volatile, trending up. AUROC declining from peak 0.875.

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.72** | ✅ **MET** |
| AUROC > 0.75 | **0.858** | ✅ **MET** |
| ECE < 0.05 | **0.012** | ✅ **MET** |
| Diff loss → 4.0 | **4.73** | ❌ Miss (trending away) |
| S1 accuracy → 40% | **21.9%** | ❌ **Miss (declining)** |

**3/5 targets met**. S1 performance concerning.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 4.12 loss | GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL

v2 AR slightly better than v1 (29.72 vs 43.86). **S1 regressing vs v1's 67% loss drop**.

## Infrastructure
**15 sessions, $30.60 total cost** | Current: 9.3h uptime, no interruptions | Spot reclaims: 14 (avg 2.2h runtime) | **Stable current session**

## What's Next
- Complete training (~45min)
- **Critical**: Investigate S1 accuracy regression
- Run v2 benchmarks vs v1/GPT-2 baselines
- Analyze confidence head calibration trends