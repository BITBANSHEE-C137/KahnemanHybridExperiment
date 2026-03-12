# v3 Training Status SITREP

## v3 Training Status
**TRAINING COMPLETE** - v3 reached **50k/50k steps** (100%). Current instance idle on g6.2xlarge (L4, 0% util, 15.6W). No active training. Spot rate $0.42/hr (57% savings vs on-demand). **ETA: N/A - Complete**.

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 43000 | 28.14  | 4.20      | 25.9%  | 0.869 | 0.010  |
| 44000 | 28.07  | 4.40      | 24.9%  | 0.867 | 0.010  |
| 45000 | 27.95  | 4.16      | 26.5%  | 0.870 | 0.011  |
| 46000 | 28.13  | 3.94      | 28.1%  | 0.866 | 0.016  |
| 47000 | 28.09  | 3.88      | 29.3%  | 0.870 | 0.014  |
| 48000 | 28.04  | 4.19      | 26.1%  | 0.870 | 0.012  |
| 49000 | 28.05  | 4.41      | 24.9%  | 0.867 | 0.012  |
| 50000 | 27.99  | 4.16      | 26.5%  | 0.870 | 0.012  |

**Trends**: AR perplexity **stable ~28** (excellent). Diff loss **volatile 3.9-4.4**. S1 accuracy **peaked at 29.3%** then regressed. AUROC **steady 0.87**. ECE **good <0.02**.

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **27.99** | ✅ **PASS** |
| AUROC > 0.75 | **0.870** | ✅ **PASS** |
| ECE < 0.05 | **0.012** | ✅ **PASS** |
| Diff loss → 4.0 | **4.16** | ⚠️ Close |
| S1 accuracy → 40% | **26.5%** | ❌ **MISS** |

**3/5 targets met**. S1 accuracy **13.5% short** of goal.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. 

v3 shows **36% AR improvement** (28 vs 44 PPL) but **S1 regressed** (26.5% vs target 40%).

## Infrastructure
**25 sessions**, $40.48 total cost. Heavy spot reclaims on 3/9-3/10 (11 interruptions). Last stable run: 3/11-3/12 (g6.2xlarge, 8.6hrs, $4.0). Current instance: 47min uptime, $0.33 accrued. **Excellent 57% spot savings**.

## What's Next
**v3 training complete**. Ready for: comprehensive benchmarking (LAMBADA, WikiText-103), v1 vs v3 performance analysis, confidence head calibration study. **S1 underperformance needs investigation**.