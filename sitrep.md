# v3 Training SITREP

## v3 Training Status
**Step 45,700/50,000** (91.4% complete). GPU at **100% utilization**, L4 running hot at 81°C/72W. Training rate steady. **ETA: ~5 hours** to completion. Current spot rate **$0.46/hr** (52.5% savings vs on-demand).

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 38000 | 28.43  | 4.02      | 28.5%  | 0.864 | 0.009 |
| 39000 | 28.34  | 4.04      | 29.0%  | 0.863 | 0.011 |
| 40000 | 28.27  | **3.76**  | 30.3%  | **0.881** | 0.009 |
| 41000 | 28.30  | 3.95      | 27.8%  | 0.866 | 0.011 |
| 42000 | 28.33  | 3.89      | 29.1%  | 0.870 | 0.013 |
| 43000 | 28.14  | 4.20      | 25.9%  | 0.869 | 0.010 |
| 44000 | 28.07  | **4.40**  | 24.9%  | 0.867 | 0.010 |
| 45000 | 27.95  | 4.16      | 26.5%  | 0.870 | 0.011 |

**Trends:** AR PPL improving steadily (**-0.5 over 7k steps**). Diffusion loss **volatile**, peak regression to 4.4 at 44k. S1 accuracy **stagnant around 26-30%**. AUROC stable ~0.87, ECE well-controlled <0.013.

## Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **27.95** | ✅ **PASS** |
| AUROC | > 0.75 | **0.870** | ✅ **PASS** |
| ECE | < 0.05 | **0.011** | ✅ **PASS** |
| Diff Loss | → 4.0 | **4.16** | ⚠️ **CLOSE** |
| S1 Acc | → 40% | **26.5%** | ❌ **MISS** |

**3/5 targets met.** S1 accuracy **severely underperforming** vs 40% target. Diffusion loss needs **-0.16** improvement.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **Current AR PPL (27.95) beats both v1 and GPT-2.** S1 performance unknown until benchmarking.

## Infrastructure
**22 spot sessions**, **$36.92 total cost**. Heavy reclaim period Mar 9th (11 interruptions). Current g6.2xlarge session stable **1.5hrs**, no recent reclaims. Infrastructure **resilient** despite spot volatility.

## What's Next
**4,300 steps remaining** (~5hrs). Post-completion: v3 LAMBADA/WikiText benchmarks, v1 vs v3 AR comparison, **S1 token accuracy deep-dive** (major concern), confidence calibration analysis.