## v3 Training Status
**Step 29,800/50,000 (59.6%)** running at **100% GPU util** on L4 (83°C, 72W). Rate ~1.47 steps/min, **ETA ~9.5 hours**. Spot cost **$0.46/hr** (53% savings), projected **$20.39** total vs $43.37 on-demand.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 22000 | 29.70  | 3.95      | 0.283  | 0.876 | 0.0039 |
| 23000 | 29.57  | 4.19      | 0.261  | 0.861 | 0.0059 |
| 24000 | 29.53  | 4.31      | 0.252  | 0.862 | 0.0055 |
| 25000 | 29.48  | 4.08      | 0.265  | 0.861 | 0.0042 |
| 26000 | 29.58  | 4.02      | 0.277  | 0.864 | 0.0063 |
| 27000 | 29.55  | 4.32      | 0.246  | 0.866 | 0.0109 |
| 28000 | 29.40  | 4.51      | 0.238  | 0.865 | 0.0068 |
| 29000 | **29.36** | **4.27** | **0.255** | **0.867** | **0.0118** |

**AR PPL improving** (29.70→29.36), **diffusion loss volatile** (3.95→4.27), **S1 accuracy declining** (0.283→0.255). AUROC stable ~0.86.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | **29.36** | ✅ |
| AUROC  | > 0.75 | **0.867** | ✅ |
| ECE    | < 0.05 | **0.012** | ✅ |
| Diff Loss | → 4.0 | **4.27** | ⚠️ |
| S1 Acc | → 40% | **25.5%** | ❌ |

**3/5 targets met**. Diffusion loss trending away from 4.0 target, S1 accuracy **significantly below 40%** target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% (PPL 1.46), WikiText-103 PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. **Current v3 AR PPL (29.36) matches GPT-2 baseline**, major improvement over v1's 43.86.

## Infrastructure
**19 spot sessions**, $24.60 total cost. Multiple **reclaims yesterday** (9 sessions in 4 hours), stabilized on current g6.2xlarge since 04:25 UTC (**10.1h uptime**). Cost efficiency strong at 53% savings.

## What's Next
Complete training in ~9.5h. **Critical**: S1 accuracy regression needs analysis - dropped from 28% to 25%. Diffusion loss instability concerning. Post-completion: full benchmarks, confidence calibration analysis, v1/v2 comparison.