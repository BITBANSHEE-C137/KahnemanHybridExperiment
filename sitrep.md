# v3 Training SITREP

## v3 Training Status
**Step 42,900/50,000 (85.8%)** | **99% GPU util** | L4 @ 72W | **~7100 steps remaining** | **$2.18 spot cost** (56.5% savings vs on-demand) | **5.1h uptime** | ETA: ~1.0h

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|---------|-----------|--------|-------|-----|
| 35000| 28.73   | 4.26      | 25.0%  | 0.863 | 0.006 |
| 38000| 28.43   | 4.02      | 28.5%  | 0.864 | 0.009 |
| 40000| 28.27   | 3.76      | 30.3%  | **0.881** | 0.009 |
| 42000| **28.33**| 3.89     | 29.1%  | 0.870 | **0.013** |

**Trends:** AR PPL plateaued ~28.3. Diff loss trending down well. S1 accuracy volatile but improving. AUROC strong but dropped from peak. **ECE deteriorating** - confidence calibration regressing.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.33** | ✅ |
| AUROC > 0.75 | **0.870** | ✅ |
| ECE < 0.05 | **0.0126** | ✅ |
| Diff loss → 4.0 | **3.89** | ✅ |
| S1 accuracy → 40% | **29.1%** | ❌ |

**4/5 targets met.** S1 accuracy lagging at 29% vs 40% target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07

**Current v3 AR PPL (28.33) already beating WikiText baseline (29.07).** Diff loss (3.89) improved 6% from v1 S1 baseline (4.12).

## Infrastructure
**21 spot sessions** across g5/g6 types. **Total cost $34.55** for 42,500 steps. Multiple reclaims 3/9 (11 instances terminated), now stable on g6.2xlarge for 2.6k steps. **Current session healthy** - no interruptions 5h runtime.

## What's Next
**7100 steps to completion (~1h).** Then: comprehensive v3 benchmarks, v1→v3 progression analysis, confidence calibration deep-dive (ECE regression concerning). S1 accuracy unlikely to hit 40% target in remaining steps.