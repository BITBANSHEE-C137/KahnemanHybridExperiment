# v3 Training SITREP

## v3 Training Status
**COMPLETE** - v3 finished at step **50,000/50,000** (100%). Current instance idle (0% GPU util, 10W power). A10G g5.2xlarge @ $0.47/hr spot (61% savings). No training ETA - **run complete**.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|---------|-----------|--------|-------|-----|
| 43k  | 28.14   | 4.20      | 25.9%  | 0.869 | 0.010 |
| 44k  | 28.07   | 4.40      | 24.9%  | 0.867 | 0.010 |
| 45k  | 27.95   | 4.16      | 26.5%  | 0.870 | 0.011 |
| 46k  | 28.13   | 3.94      | 28.1%  | 0.866 | 0.016 |
| 47k  | 28.09   | 3.88      | 29.3%  | 0.870 | 0.014 |
| 48k  | 28.04   | 4.19      | 26.1%  | 0.870 | 0.012 |
| 49k  | 28.05   | 4.41      | 24.9%  | 0.867 | 0.012 |
| **50k** | **27.99** | **4.16** | **26.5%** | **0.870** | **0.012** |

**Trends**: AR PPL plateaued ~28. Diff loss volatile (3.88→4.41). S1 accuracy peaked at 29.3% then regressed. AUROC stable ~0.87. ECE well-controlled.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **27.99** | ✅ **MET** |
| AUROC | > 0.75 | **0.870** | ✅ **MET** |
| ECE | < 0.05 | **0.012** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.16** | ⚠️ **CLOSE** |
| S1 Accuracy | → 40% | **26.5%** | ❌ **MISS** |

**3/5 targets met**. S1 accuracy significantly below target (26.5% vs 40%).

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. v3 shows **36% AR improvement** (28.0 vs 43.9 PPL) but **S1 accuracy regression** vs target. Confidence calibration excellent (ECE 0.012 vs baseline ECE unknown).

## Infrastructure
**23 spot sessions**, **$40.35 total cost**. Multiple reclaims 3/9-3/10 (9 interruptions in 6hrs). Stabilized on g6.2xlarge 3/11-3/12. Current g5.2xlarge idle since completion. **99.6% cost savings** vs on-demand projected.

## What's Next
v3 **complete** - ready for benchmarking. Priority: LAMBADA/WikiText eval, S1 confidence analysis (why 26.5% vs 40% target?), v1→v3 comparison. Investigate S1 accuracy plateau - may need arch changes or longer training.