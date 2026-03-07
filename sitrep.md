# v2 Training Status SITREP

## v2 Training Status
**99.6% complete** (49,800/50,000 steps). A10G at **100% utilization**, 197W/300W, 50°C. Current rate ~400 steps/hr. **ETA: 30 minutes**. Spot instance stable at $0.46/hr (**61.8% savings** vs on-demand).

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 42000 | 30.08  | 4.07      | 29.0%  | 0.862 | 0.016 |
| 43000 | 29.96  | 3.93      | 29.2%  | 0.868 | 0.020 |
| 45000 | 29.80  | 3.86      | 29.3%  | 0.875 | 0.016 |
| 47000 | 29.72  | 4.61      | 22.7%  | 0.855 | 0.011 |
| 48000 | 29.72  | 4.73      | 21.9%  | 0.858 | 0.012 |
| **49000** | **29.64** | **4.24** | **25.4%** | **0.865** | **0.010** |

**Trends**: AR PPL steady improvement. **S1 accuracy volatile** - dropped to 21.9% at 48k, recovered to 25.4%. Diffusion loss unstable, spiked to 4.73. AUROC recovering after 47k dip. ECE excellent at 0.010.

## Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **29.64** | ✅ **PASS** |
| AUROC | > 0.75 | **0.865** | ✅ **PASS** |
| ECE | < 0.05 | **0.010** | ✅ **PASS** |
| Diff Loss | → 4.0 | **4.24** | ⚠️ **CLOSE** |
| S1 Accuracy | → 40% | **25.4%** | ❌ **MISS** |

**3/5 targets met**. S1 accuracy significantly underperforming - **37% below target**.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. 

v2 AR PPL (**29.64**) **beating v1 WikiText** (43.86) and approaching GPT-2 baseline. S1 performance concerning - accuracy 25% vs v1's loss equivalent.

## Infrastructure
**15 spot sessions**, $31.30 total cost. **14 spot reclaims** - high churn but training resilient. Current session: 10.8hr uptime, stable. Checkpoints syncing properly. **$8.08 saved** vs on-demand.

## What's Next
200 steps to completion (~30min). Run v2 benchmarks immediately. **Priority**: S1 analysis - volatile accuracy suggests potential training instability or eval bugs. Compare v1/v2 confidence calibration. Full benchmark suite for publication.