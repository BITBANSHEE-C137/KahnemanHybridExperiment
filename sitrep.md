## v2 Training Status
**Step 46k/50k (92%)** - A10G @ 100% util, 199W/300W, 50°C. Current rate ~400 steps/hr, **ETA: 10 hours**. Spot cost $0.46/hr (62% savings vs on-demand). Total run cost **$29.21** across 15 sessions.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 39k  | 30.41  | 3.80      | 30.7%  | 0.863 | 0.007 |
| 40k  | 30.21  | **4.56**  | 23.2%  | 0.857 | 0.007 |
| 41k  | 30.12  | 4.47      | 25.1%  | 0.862 | **0.012** |
| 42k  | 30.08  | 4.07      | 29.0%  | 0.862 | **0.016** |
| 43k  | 29.96  | 3.93      | 29.2%  | 0.868 | **0.020** |
| 44k  | 29.96  | 4.37      | 25.4%  | 0.865 | **0.016** |
| 45k  | 29.80  | 3.86      | 29.3%  | **0.875** | **0.016** |
| 46k  | **29.74** | 4.15   | 26.2%  | 0.865 | **0.011** |

**AR PPL steadily improving**. Diff loss volatile (3.8-4.6 range). **ECE degraded mid-training but recovering**. S1 accuracy unstable 23-31%.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | **29.74** | ✅ **MET** |
| AUROC  | > 0.75 | **0.865** | ✅ **MET** |
| ECE    | < 0.05 | **0.011** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.15** | ⚠️ **CLOSE** |
| S1 Acc | → 40%  | **26.2%** | ❌ **MISS** |

**3/5 targets met**. Diffusion loss hovering around target. **S1 accuracy significantly underperforming**.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% / PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. **v2 AR PPL (29.74) substantially better than v1 WikiText (43.86)**. Current S1 accuracy (26.2%) suggests potential regression from v1 joint training benefits.

## Infrastructure
15 spot sessions, **4 reclaims** (most recent 6hrs uptime). Heavy AZ switching (1a→1b→1f→1b). Instance type oscillation (g5.xlarge failovers). **62% cost savings maintained**. Current session stable since 17:42 UTC.

## What's Next
**4k steps remaining** - monitor S1 accuracy recovery and diffusion loss convergence. Post-completion: comprehensive v2 benchmarks, v1-v2 comparison analysis, **confidence calibration deep-dive** given ECE volatility pattern.