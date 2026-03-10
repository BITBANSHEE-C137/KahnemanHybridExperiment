## v3 Training Status
**Step 26,900/50,000** (53.8% complete). L4 GPU at **99% util**, 73W/72W power limit, 72°C, 16.6GB/23GB VRAM. Training rate ~150 steps/hr. **ETA: 6.4 days**. Spot cost **$0.46/hr** (53% savings vs on-demand). Current session: 5h uptime, $2.28 cost.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|--------|-----|
| 19000 | 29.21 | 4.39 | 22.1% | 0.866 | 0.011 |
| 20000 | 29.22 | 4.24 | 26.8% | 0.857 | 0.005 |
| 21000 | 29.94 | 4.26 | 26.8% | 0.856 | 0.012 |
| 22000 | **29.70** | **3.95** | **28.3%** | **0.876** | **0.004** |
| 23000 | 29.57 | 4.19 | 26.1% | 0.861 | 0.006 |
| 24000 | 29.53 | 4.31 | 25.2% | 0.862 | 0.005 |
| 25000 | 29.48 | 4.08 | 26.5% | 0.861 | 0.004 |
| 26000 | 29.58 | 4.02 | **27.7%** | 0.864 | 0.006 |

**Trends:** AR PPL stable ~29.5. Diffusion loss trending down (4.39→4.02). S1 accuracy climbing (22%→28%). AUROC solid ~0.86. **Step 22k spike** notable across metrics.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|---------|----------|---------|
| AR PPL | < 40 | **29.58** | ✅ Met |
| AUROC | > 0.75 | **0.864** | ✅ Met |
| ECE | < 0.05 | **0.0063** | ✅ Met |
| Diff Loss | → 4.0 | **4.02** | ✅ Near target |
| S1 Accuracy | → 40% | **27.7%** | ❌ 69% of target |

**4/5 targets met.** S1 accuracy lagging but improving (+25% since step 19k).

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v3 AR PPL (29.58) significantly better than v1 (43.86)**, approaching GPT-2 baseline. Diffusion loss tracking v1 final levels.

## Infrastructure
**19 spot sessions**, frequent interruptions Mar 9th (15 reclaims in 4hrs). Stabilized on current g6.2xlarge since 04:25 UTC. Total cost **$22.31** vs $43.25 on-demand. Checkpoint sync active, last backup: step_26000.pt (1.5GB).

## What's Next
**23k steps remaining** (~6 days). Monitor S1 accuracy convergence to 40% target. Post-completion: v3 LAMBADA/WikiText benchmarks, v1→v3 performance delta analysis, confidence calibration deep-dive.