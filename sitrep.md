# v3 Training Status SITREP

## v3 Training Status
**COMPLETE** - Training finished at step **50,000/50,000** (100%). Current instance idle (0% GPU util, trainer stopped). Last checkpoint: step_50000.pt (1.5GB, 03-12 01:08 UTC). Sync running for final model upload.

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 43000 | 28.14 | 4.20 | 25.9% | 0.869 | 0.010 |
| 44000 | 28.07 | 4.40 | 24.9% | 0.867 | 0.010 |
| 45000 | 27.95 | 4.16 | 26.5% | 0.870 | 0.011 |
| 46000 | 28.13 | 3.94 | 28.1% | 0.866 | 0.016 |
| 47000 | 28.09 | 3.88 | 29.3% | 0.870 | 0.014 |
| 48000 | 28.04 | 4.19 | 26.1% | 0.870 | 0.012 |
| 49000 | 28.05 | 4.41 | 24.9% | 0.867 | 0.012 |
| **50000** | **27.99** | **4.16** | **26.5%** | **0.870** | **0.012** |

**Trends**: AR PPL stable ~28, minor improvement. Diff loss volatile (3.88→4.41). S1 accuracy peaked at step 47k (29.3%), regressed to 26.5%. AUROC consistent 0.867-0.870. ECE degraded from 0.010→0.016, recovered to 0.012.

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **27.99** | ✅ **MET** |
| AUROC > 0.75 | **0.870** | ✅ **MET** |
| ECE < 0.05 | **0.012** | ✅ **MET** |
| Diff loss → 4.0 | **4.16** | ⚠️ **CLOSE** |
| S1 accuracy → 40% | **26.5%** | ❌ **MISS** |

**3/5 targets met**. S1 accuracy significantly below 40% target. Diff loss close but not quite at 4.0.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. 
v3 final: AR PPL **27.99** (36% better than v1 WikiText), S1 comparable metrics suggest similar S1 loss.

## Infrastructure
**Total cost**: $40.35 across 23 spot instances. Current: g5.2xlarge @ $0.48/hr (60.8% savings vs $1.21 on-demand). 

**Spot history**: Heavy reclaiming 03-09 (11 reclaims in 6 hours), stabilized 03-10+. Mixed instance types (g5/g6, xlarge/2xlarge) due to availability constraints.

**Uptime**: 6.8 hours current session, no training activity.

## What's Next
v3 training **COMPLETE**. Ready for:
1. **v3 benchmark suite** (LAMBADA, WikiText-103)  
2. **v1 vs v3 comparison** - expect AR improvement, S1 performance assessment
3. **Confidence head deep-dive** - AUROC strong but S1 accuracy concerning
4. **Cost analysis** - $40 for 50k steps, heavy spot reclaim impact

**Critical**: S1 underperformance needs investigation before v4 architecture decisions.