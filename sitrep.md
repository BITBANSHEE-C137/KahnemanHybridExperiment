## v2 Training Status
**Step 27,300 / 50,000 (54.6%)** - GPU at **99%** utilization, A10G running cool at 50°C. Rate: ~180 steps/hr. **ETA: ~5.3 days**. Current spot cost: **$0.45/hr** (63% savings vs on-demand). Total cost: **$18.30**.

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|---------|-------|-------|
| 20000 | 30.92  | 4.75      | 21.3%   | 0.851 | 0.007 |
| 22000 | 30.95  | **4.19**  | **27.5%** | 0.858 | 0.010 |
| 23000 | 31.03  | **4.03**  | **27.9%** | **0.864** | 0.010 |
| 25000 | 31.22  | 4.20      | 27.6%   | 0.860 | 0.012 |
| 27000 | **31.46** | 4.48   | 24.4%   | 0.862 | 0.009 |

**Trends**: AR PPL slowly degrading (+1.8% over 7k steps). Diffusion loss volatile but improving trend. S1 accuracy peaked at 23k, now regressing. AUROC stable ~0.86. **ECE well controlled**.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **31.46** | ✅ **PASS** |
| AUROC > 0.75 | **0.862** | ✅ **PASS** |
| ECE < 0.05 | **0.009** | ✅ **PASS** |
| Diff Loss → 4.0 | **4.48** | 🟡 **CLOSE** |
| S1 Acc → 40% | **24.4%** | ❌ **MISS** |

**3/5 targets met**. S1 accuracy significantly underperforming - needs investigation.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, WikiText PPL 43.86, S1 loss 4.12. **Current v2 AR PPL (31.46) already beating v1 WikiText (43.86)**. S1 performance lagging expectations but diffusion loss approaching v1 levels.

## Infrastructure
**12 spot reclaims** over 2.5 days - aggressive spot termination pattern. Current instance (us-east-1a) stable for **4.1 hrs**. Cost efficiency excellent: **$18.30 total** vs **$38.32 on-demand**. Multiple AZ failover working well.

## What's Next
Critical: **Investigate S1 accuracy plateau/regression** around step 23k-27k. Consider learning rate schedule adjustment. After completion: v2 benchmarks, confidence calibration deep-dive, v1 vs v2 head-to-head on LAMBADA/WikiText.