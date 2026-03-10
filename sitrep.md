# ML Training SITREP - 2026-03-10 19:00 UTC

## v3 Training Status
**Step 32,500/50,000 (65%)** - GPU: **100% util** L4 @81°C, 72W draw. Rate: ~300 steps/hr. **ETA: ~2.4 days**. Current spot: **$0.46/hr** (53% savings vs on-demand). Run cost: **$26.71** total.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 25000 | 29.48  | 4.08      | 26.5%  | 0.861 | 0.0042 |
| 28000 | 29.40  | 4.51      | 23.8%  | 0.865 | 0.0068 |
| 30000 | 29.16  | 4.34      | 24.6%  | 0.868 | 0.0046 |
| 32000 | **29.04** | **4.35** | **24.2%** | **0.865** | **0.0089** |

**Trends**: AR PPL slowly improving (-0.44 over 7k steps). Diffusion loss volatile around 4.3. S1 accuracy **stagnating ~24%**. AUROC stable ~0.865. ECE degrading slightly.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | **29.04** | ✅ |
| AUROC  | > 0.75 | **0.865** | ✅ |
| ECE    | < 0.05 | **0.009** | ✅ |
| Diff Loss | → 4.0 | **4.35** | ❌ |
| S1 Acc | → 40% | **24.2%** | ❌ |

**3/5 targets met**. Diffusion loss needs -0.35 improvement. **S1 accuracy severely underperforming** - needs +16pp.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. **Current AR PPL (29.04) already beating WikiText baseline**. S1 performance unclear without loss comparison.

## Infrastructure
**19 spot reclaims** - extreme instability 3/9-3/10. Multiple brief sessions <1hr suggesting aggressive spot market. Current g6.2xlarge stable 14.5hrs. Total sessions cost $26.67 vs $43.31 on-demand projection (**38% actual savings**).

## What's Next
**Critical**: S1 accuracy plateau concerning - may need LR adjustment or architecture review. Diffusion loss regression from mid-training needs investigation. Complete by ~3/13, then v2 benchmarks and confidence head analysis.