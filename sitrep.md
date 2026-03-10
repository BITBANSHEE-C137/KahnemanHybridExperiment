# v3 Training SITREP - March 10, 2026

## v3 Training Status
**Progress**: Step 400/50,000 (**0.8%**) | **GPU**: 0% util on L4 (IDLE - training halted) | **Rate**: N/A | **ETA**: Unknown | **Spot Cost**: $0.45/hr (54% savings)

**⚠️ CRITICAL**: Training stopped at step 400, GPU idle. Last checkpoint at step 24,000 suggests major rollback or data corruption.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 17000 | 28.89  | 4.34      | 25.2%  | 0.858 | 0.008  |
| 18000 | 28.99  | 4.44      | 23.0%  | 0.858 | 0.010  |
| 19000 | 29.21  | 4.39      | 22.1%  | 0.866 | 0.011  |
| 20000 | 29.22  | **4.24**  | 26.8%  | 0.857 | **0.005** |
| 21000 | 29.94  | 4.26      | 26.8%  | 0.856 | 0.012  |
| 22000 | 29.70  | **3.95**  | **28.3%** | **0.876** | **0.004** |
| 23000 | 29.57  | 4.19      | 26.1%  | 0.861 | 0.006  |
| 24000 | 29.53  | 4.31      | 25.2%  | 0.862 | 0.005  |

**Trends**: AR PPL stable ~29, diffusion loss volatile (3.95-4.44), S1 accuracy peaked at 28.3% (step 22k), confidence metrics strong.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | **29.53** | ✅ |
| AUROC  | > 0.75 | **0.862** | ✅ |
| ECE    | < 0.05 | **0.005** | ✅ |
| Diff Loss | 4.0 | **4.31** | ❌ (8% over) |
| S1 Acc | 40%   | **25.2%** | ❌ (37% short) |

**3/5 targets met**. Diffusion loss and S1 accuracy lagging.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. Current v3 shows **33% better AR PPL** (29.53 vs 43.86) but **39% worse S1 performance** (25.2% vs theoretical 40% target from 4.12→4.0 loss improvement).

## Infrastructure
**Cost**: $20.07 total across 19 spot instances | **Instability**: Extreme - **18 spot reclaims** in 2 days | **Current**: g6.2xlarge, 4min uptime, stable

**Major Issues**: Constant spot interruptions causing training fragmentation, especially steps 20k-21k (7 reclaims in 3 hours).

## What's Next
**IMMEDIATE**: Investigate training halt - checkpoint corruption likely. Resume from step 24k backup.
**TACTICAL**: Switch to on-demand for stability, current spot chaos unsustainable.
**STRATEGIC**: Diffusion loss convergence and S1 accuracy remain critical blockers.