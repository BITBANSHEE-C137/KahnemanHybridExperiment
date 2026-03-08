# SITREP: v3 Dual-Process Training

## v3 Training Status
**Step 4900/50000** (9.8% complete) • **100% GPU util** A10G @ 253W/300W • **6.16 hrs runtime** current session • **~188 steps/hr** • **ETA: ~12 days** • **Spot cost: $0.46/hr** (62% savings vs on-demand)

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Tok Acc | AUROC | ECE |
|------|--------|-----------|-------------|-------|-----|
| 1000 | 21.29  | 6.75      | 5.04%       | 0.557 | 0.006 |
| 2000 | 22.53  | 6.54      | 6.44%       | 0.613 | 0.004 |
| 3000 | 23.17  | 6.38      | 7.57%       | 0.638 | 0.010 |
| 4000 | **23.71** | **6.29** | **8.46%** | **0.672** | **0.011** |

**Trends**: AR PPL degrading (+11% since step 1K). Diffusion loss improving steadily (-0.46). S1 accuracy climbing (+68%). AUROC improving but slowly. ECE volatile but acceptable.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **23.71** | ✅ |
| AUROC | > 0.75 | **0.672** | ❌ |
| ECE | < 0.05 | **0.011** | ✅ |
| Diff Loss | → 4.0 | **6.29** | 🔄 |
| S1 Accuracy | → 40% | **8.46%** | 🔄 |

**2/5 targets met**. AUROC lagging significantly. S1 accuracy improving but needs 5x boost.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. **Current v3 AR PPL (23.71) tracking well vs v1 (43.86)**. Confidence calibration significantly better than v1's post-joint-training regression.

## Infrastructure
**2 spot sessions** • **$5.91 total cost** • Current instance 6.16hrs uptime • **1 reclaim event** (session 1 interrupted at step 1K) • Checkpoints syncing properly • **70% VRAM utilization** (16.2GB/23GB)

## What's Next
Monitor AUROC plateau - may need confidence head LR adjustment. Diffusion loss trajectory good. **Critical eval at 10K steps** to assess if confidence calibration improvements sustain. Prepare v2 benchmark infrastructure.