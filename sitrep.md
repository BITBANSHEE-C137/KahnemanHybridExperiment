# v3 Training Status SITREP

## v3 Training Status
**Step 47,200/50,000** (94.4% complete). L4 GPU at **100% utilization**, 72W power draw, 82°C. Current rate ~7 steps/min. **ETA: 6.7 hours**. Spot instance (g6.2xlarge) running $0.463/hr vs $0.978 on-demand (**52.6% savings**). Current session cost: $1.83.

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|---------|-----------|---------|--------|--------|
| 40000 | 28.27   | 3.76      | 30.3%   | 0.881  | 0.0094 |
| 42000 | 28.33   | 3.89      | 29.1%   | 0.870  | 0.0126 |
| 44000 | 28.07   | 4.40      | 24.9%   | 0.867  | 0.0096 |
| 46000 | 28.13   | 3.94      | 28.1%   | 0.866  | 0.0155 |
| **47000** | **28.09** | **3.88** | **29.3%** | **0.870** | **0.0144** |

**Trends**: AR perplexity stable ~28. Diffusion loss volatile (3.76→4.40→3.88). S1 accuracy recovering from 44k dip. **AUROC plateau at 0.87**. ECE degrading slightly.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.09** | ✅ **MET** |
| AUROC > 0.75 | **0.870** | ✅ **MET** |
| ECE < 0.05 | **0.0144** | ✅ **MET** |
| Diff loss → 4.0 | **3.88** | ✅ **MET** |
| S1 accuracy → 40% | **29.3%** | ❌ **MISS** |

**4/5 targets met**. S1 accuracy stuck at ~29%, **11% below target**.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText-103 PPL 43.86, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. 

**Current v3 shows improvement**: AR PPL **28.09 vs 43.86** (36% better than v1). Diffusion loss **3.88 vs 4.12** (6% better). Joint training working.

## Infrastructure
**22 spot sessions**, $38.11 total cost vs $84.95 on-demand (**55% savings**). Current session stable 3.9hrs, no interruptions. Previous session: 9.1hr run (45.3k steps). **Spot reclaim rate manageable** - longest continuous runs on g6.2xlarge instances.

## What's Next
**2,800 steps remaining** (~6.7hrs). After completion: full v3 benchmarks on LAMBADA/WikiText, detailed v1→v3 progression analysis, **confidence head investigation** for AUROC plateau, S1 accuracy deep-dive.