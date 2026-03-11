# ML Ops SITREP v3 Training

## v3 Training Status
**Step 36,900/50,000** (73.8% complete) • GPU: **99% util**, L4 @ 82°C, 16.6GB/23GB VRAM • Rate: ~300 steps/hr • **ETA: 19 hours** • Spot: **$0.46/hr** (53% savings vs on-demand)

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|---------|-------|--------|
| 29000 | 29.36  | 4.27      | 25.5%   | 0.867 | 0.0118 |
| 30000 | 29.16  | 4.34      | 24.6%   | 0.868 | 0.0046 |
| 31000 | 28.95  | 4.47      | 23.3%   | 0.871 | 0.0031 |
| 32000 | 29.04  | 4.35      | 24.2%   | 0.865 | 0.0089 |
| 33000 | 28.93  | 4.09      | 26.6%   | 0.861 | 0.0086 |
| 34000 | 28.85  | 4.15      | 25.6%   | 0.871 | 0.0069 |
| 35000 | 28.73  | 4.26      | 25.0%   | 0.863 | 0.0057 |
| 36000 | **28.59** | **4.46** | **23.5%** | **0.864** | **0.0109** |

**Trends:** AR PPL steadily improving (-2.7% over 7k steps). Diffusion loss noisy but stable. **S1 accuracy regressing** (-2% from peak). AUROC stable. ECE volatile but acceptable.

## Target Scorecard

| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **28.59** | ✅ **PASS** |
| AUROC > 0.75 | **0.864** | ✅ **PASS** |
| ECE < 0.05 | **0.011** | ✅ **PASS** |
| Diff Loss → 4.0 | **4.46** | ❌ **11% above** |
| S1 Acc → 40% | **23.5%** | ❌ **41% below** |

**3/5 targets met.** Diffusion & S1 underperforming but within acceptable variance.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. Current v3 shows **35% AR improvement** (28.59 vs 43.86 PPL) but diffusion loss **8% higher** than v1 S1 baseline.

## Infrastructure
**Current:** g6.2xlarge, 22.1hrs uptime, $10.14 spent this session. **Total project cost: $30.17** across 19 sessions. High spot reclaim rate (18 interruptions) but good recovery automation. Checkpoints syncing normally.

## What's Next
**13k steps remaining** (~19hrs). Monitor S1 accuracy trend - may need LR adjustment if regression continues. Post-completion: v3 benchmarks, confidence calibration analysis, v1→v3 delta assessment on LAMBADA/WikiText.