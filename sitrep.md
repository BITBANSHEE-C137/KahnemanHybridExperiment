# v2 Training SITREP

## v2 Training Status
**Step 38,100/50,000** (76.2% complete). A10G @ **100% GPU util**, 194W/300W, 53°C, 16.6GB/23GB VRAM. Training rate ~900 steps/day. **ETA: 13.2 days**. Current spot rate **$0.45/hr** (62.7% savings vs on-demand).

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 31000 | 31.60 | 4.49 | 24.5% | 0.862 | 0.014 |
| 32000 | 31.39 | **3.96** | **28.4%** | **0.871** | 0.013 |
| 33000 | 31.29 | 4.23 | 25.4% | 0.864 | **0.008** |
| 34000 | 31.13 | 4.68 | 22.0% | 0.854 | 0.009 |
| 35000 | 30.84 | 4.79 | 21.4% | 0.855 | 0.011 |
| 36000 | 30.69 | 4.30 | 24.8% | 0.863 | 0.010 |
| 37000 | 30.65 | 4.75 | 21.6% | 0.861 | 0.007 |
| 38000 | **30.44** | 4.28 | 26.7% | 0.865 | **0.004** |

**Trends:** AR PPL steadily improving (-3.8% since 31k). S1 accuracy volatile but trending up. ECE **excellent** at 0.004. Diffusion loss plateaued ~4.3.

## Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **30.44** | ✅ **PASS** |
| AUROC | > 0.75 | **0.865** | ✅ **PASS** |
| ECE | < 0.05 | **0.004** | ✅ **PASS** |
| Diff Loss | → 4.0 | 4.28 | 🟡 Close |
| S1 Accuracy | → 40% | 26.7% | 🔴 **Behind** |

**3/5 targets met**. S1 accuracy lagging significantly.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. 

**v2 vs v1:** AR PPL improved (30.44 vs 43.86). S1 performance similar trajectory.

## Infrastructure
**13 spot sessions** across 3 AZs. Total cost **$24.60** vs $32.55 on-demand. Current session: 12.4hr uptime, no interruptions. **Stable run** - longest session yet.

**Spot reclaim risk:** Moderate (62.7% savings indicates tight capacity).

## What's Next
**11,900 steps remaining** (~13 days). Focus: S1 accuracy breakthrough needed. Post-completion: comprehensive v1/v2 benchmarks, confidence calibration analysis, ablation studies on dual-process convergence.