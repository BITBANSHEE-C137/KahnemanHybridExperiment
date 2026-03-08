# v3 Training SITREP

## v3 Training Status
**Step 7,800/50,000** (15.6% complete). A10G at **100% GPU util**, 204W/300W, 58°C, 16.2GB/23GB VRAM. Training rate ~400 steps/9.4hrs. **ETA: ~43 days**. Current spot: **$0.46/hr** (62% savings vs on-demand).

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 1000 | 21.29  | 6.75      | 5.04%  | 0.557 | 0.006 |
| 3000 | 23.17  | 6.38      | 7.57%  | 0.638 | 0.010 |
| 5000 | 24.35  | 6.12      | 9.13%  | 0.695 | 0.008 |
| **7000** | **25.48** | **5.87** | **10.55%** | **0.739** | **0.009** |

**Trends:** AR perplexity **degrading** (+4.2 from step 1k). Diffusion loss **improving** steadily (-0.88). S1 accuracy **doubling** but still low. AUROC **strong upward** trend (+0.18). ECE stable/good.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **25.48** | ✅ |
| AUROC | > 0.75 | **0.739** | ❌ (98% there) |
| ECE | < 0.05 | **0.009** | ✅ |
| Diff Loss | → 4.0 | **5.87** | 🟡 (68% progress) |
| S1 Acc | → 40% | **10.55%** | ❌ (26% there) |

**3/5 targets met.** AUROC almost there, S1 accuracy lagging significantly.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. Current v3 AR performance **better than v1** (25.48 vs 43.86 PPL), but **worse than GPT-2 baseline** (29.07). Joint training showing **no AR regression** vs v1.

## Infrastructure
**2 spot sessions, 0 reclaims.** Current session: 9.7hrs uptime, $4.40 cost. Total project cost: **$7.51** (vs $73.63 on-demand). Instance stable, sync/trainer running clean.

## What's Next
Continue training - **AUROC close to threshold**. Monitor AR PPL trend (concerning uptick). S1 accuracy needs significant improvement. Next eval checkpoint at 8k steps due soon.