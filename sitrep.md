# v3 Training SITREP
*2026-03-08 14:00 UTC*

## v3 Training Status
**Step 1/50k** (0.0% complete). GPU at **100% util**, A10G running 208W/300W at 58°C. VRAM: 16.2GB/23GB used. Fresh restart from step 1000 checkpoint after spot reclaim. No meaningful rate/ETA yet - just started.

**Spot cost**: $0.46/hr (62% savings vs $1.21 on-demand).

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | Conf AUROC | Conf ECE |
|------|--------|-----------|--------|------------|----------|
| 1000 | **21.29** | **6.75** | **4.98%** | **0.555** | **0.0038** |

Single eval point available. AR PPL significantly better than v1 baseline (43.86→21.29). Diffusion loss higher than target but training just resumed.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **21.29** | ✅ **PASS** |
| AUROC | > 0.75 | **0.555** | ❌ **MISS** |
| ECE | < 0.05 | **0.0038** | ✅ **PASS** |
| Diff Loss | → 4.0 | **6.75** | 🔄 **PROGRESS** |
| S1 Accuracy | → 40% | **4.98%** | ❌ **EARLY** |

**3/5 targets on track**. AR performance strong, confidence calibration excellent, but AUROC needs major improvement.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12.
Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL.

**v3 showing strong AR improvement** (43.86→21.29 PPL) over v1, suggesting better joint training balance.

## Infrastructure
**Spot reclaim event**: Previous session (i-0b467969d9fe6585b) ran steps 400-1000 for $3.11 before termination. Current session restarted cleanly from checkpoint.

**Total spend**: $3.15 across 2 sessions. Current rate sustainable for full 50k steps (~$150 projected).

## What's Next
Monitor training stability post-restart. Key watch: diffusion loss convergence and confidence head development. Next eval at step 1500 will show recovery trajectory from spot interruption.

**Critical**: AUROC development needs attention - currently random performance.