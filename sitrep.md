## v3 Training Status
**98.6% complete** (49,300/50,000 steps). GPU utilization **99%** on g6.2xlarge L4. Current rate ~300 steps/hr, **ETA 2.5 hours**. Spot cost **$0.46/hr** (53% savings vs on-demand $0.98/hr). Current session cost **$3.45**, total project **$39.70**.

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|--------|--------|
| 42000 | 28.33  | 3.89      | 29.1%  | 0.870  | 0.0126 |
| 43000 | 28.14  | 4.20      | 25.9%  | 0.869  | 0.0103 |
| 44000 | 28.07  | 4.40      | 24.9%  | 0.867  | 0.0096 |
| 45000 | 27.95  | 4.16      | 26.5%  | 0.870  | 0.0112 |
| 46000 | 28.13  | 3.94      | 28.1%  | 0.866  | 0.0155 |
| 47000 | 28.09  | 3.88      | 29.3%  | 0.870  | 0.0144 |
| 48000 | 28.04  | 4.19      | 26.1%  | 0.870  | 0.0120 |
| 49000 | 28.05  | 4.41      | 24.9%  | 0.867  | 0.0121 |

**Trends**: AR PPL stable ~28 (good). Diff loss volatile 3.9-4.4 (concerning). S1 accuracy degrading 29.3% → 24.9% (regression). AUROC/ECE stable.

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.05** | ✅ **MET** |
| AUROC > 0.75 | **0.867** | ✅ **MET** |
| ECE < 0.05 | **0.012** | ✅ **MET** |
| Diff loss → 4.0 | **4.41** | ❌ **10% over** |
| S1 accuracy → 40% | **24.9%** | ❌ **38% under** |

**3/5 targets met**. S1 performance significantly underperforming.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, PPL 1.46; WikiText PPL 43.86; S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. **v3 AR performance superior to v1** (28 vs 44 PPL), but **S1 regression continues** (25% vs target 40%).

## Infrastructure
**22 spot sessions**, multiple reclaims in us-east-1b on 3/9. Current session stable 7.5hrs on g6.2xlarge us-east-1a. Total uptime issues cost ~$2-3 in failed sessions. Checkpointing every 1k steps, last backup 23:26 UTC.

## What's Next
**700 steps to completion** (~2.5hrs). Priority: **investigate S1 token accuracy collapse** - potential data/masking issue or learning rate problem. Post-completion: full v3 benchmarks, confidence calibration analysis, v1-v2-v3 progression study.