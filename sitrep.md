# v2 Training SITREP

## v2 Training Status
**Step 25,200/50,000** (50.4% complete). A10G @ 100% GPU util, 200W/300W, 53°C, 16.6GB/23GB VRAM. Rate: ~4.8 steps/min. **ETA: ~90 hours** (3.7 days). Spot cost: **$0.45/hr** (63% savings vs on-demand $1.21/hr).

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 18000 | 30.77  | 4.03      | 27.2%  | 0.869 | 0.006 |
| 19000 | 30.81  | 4.31      | 24.5%  | 0.860 | 0.007 |
| 20000 | 30.92  | 4.75      | 21.3%  | 0.851 | 0.007 |
| 21000 | 30.88  | 4.85      | 20.7%  | 0.851 | 0.007 |
| 22000 | 30.95  | 4.19      | 27.5%  | 0.858 | 0.010 |
| 23000 | 31.03  | 4.03      | 27.9%  | 0.864 | 0.010 |
| 24000 | 30.98  | 4.46      | 24.3%  | 0.863 | 0.005 |
| **25000** | **31.22** | **4.20** | **27.6%** | **0.860** | **0.012** |

**Concerning trends**: AR PPL **stagnating ~31**, diffusion loss volatile (4.0-4.9 range), S1 accuracy **highly unstable** (20-28%). AUROC declining from 0.869 peak. ECE acceptable but variable.

## Target Scorecard

| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **31.22** | ✅ **MET** |
| AUROC > 0.75 | **0.860** | ✅ **MET** |
| ECE < 0.05 | **0.012** | ✅ **MET** |
| Diff loss → 4.0 | **4.20** | ⚠️ Close |
| S1 accuracy → 40% | **27.6%** | ❌ **MISSING** |

**3/5 targets met**. S1 accuracy **severely underperforming** (27.6% vs 40% target). Diffusion loss close but unstable.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% acc/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%/WikiText 29.07 PPL. **Current v2 AR PPL (31.22) performing better than v1 WikiText (43.86)** but worse than GPT-2. S1 performance tracking below v1 baseline.

## Infrastructure
**12 spot sessions**, $17.17 total cost. Current session: 1.6hrs uptime, $0.69 spent. **Frequent spot reclaims** (avg 3.5hr sessions). Last stable run: 10hrs (steps 14100-21900). Infrastructure resilience holding but **high churn rate** impacting training stability.

## What's Next
At 50% completion, **S1 accuracy regression critical**. Post-v2: comprehensive v1/v2 benchmarking, confidence head analysis for AUROC decline investigation, potential hyperparameter adjustment for S1 stability.