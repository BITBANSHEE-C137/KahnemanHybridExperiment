# v3 Training Status SITREP

## v3 Training Status
**Step 16,500/50,000 (33%)** | A10G @ 100% util, 202W/300W, 53°C | VRAM: 16.2/23GB  
Rate: ~9.6 steps/min | **ETA: ~5.8 days** | Spot cost: **$0.45/hr** (62% savings vs on-demand)

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 9000 | 26.95 | 5.06 | 18.4% | 0.805 | 0.006 |
| 10000 | 27.55 | 4.98 | 19.0% | 0.828 | 0.005 |
| 11000 | 27.85 | 4.43 | 22.0% | 0.853 | 0.010 |
| 12000 | 28.12 | 4.31 | 25.0% | 0.853 | 0.007 |
| 13000 | 28.41 | 4.42 | 24.1% | 0.844 | 0.011 |
| 14000 | 28.51 | 4.29 | 24.7% | 0.852 | 0.009 |
| 15000 | 28.64 | 4.50 | 23.7% | 0.864 | 0.005 |
| **16000** | **28.66** | **4.38** | **23.5%** | **0.856** | **0.010** |

**Trends:** AR PPL steadily degrading (+1.7 since step 9k). S1 accuracy peaked at 25% (step 12k), now declining. AUROC solid with upward trend. ECE volatile but acceptable.

## Target Scorecard

| Target | Current | Met? |
|--------|---------|------|
| AR PPL < 40 | **28.66** | ✅ |
| AUROC > 0.75 | **0.856** | ✅ |  
| ECE < 0.05 | **0.010** | ✅ |
| Diff loss → 4.0 | **4.38** | 🟡 (87% there) |
| S1 accuracy → 40% | **23.5%** | ❌ (59% there) |

**3/5 targets met.** Diffusion loss close but stalled. S1 accuracy regressing from peak.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, WikiText PPL 43.86, S1 loss 4.12. Current v3 AR PPL (**28.66**) significantly better than v1 (**43.86**). S1 performance tracking slightly behind v1 baseline trajectory.

## Infrastructure
**Uptime:** 20.2h across 2 spot sessions | **Total cost:** $12.29 | Current session stable 20h+  
No spot reclaims since 03-08. Checkpoint sync active. **Projected run cost: $27.61** (vs $73.59 on-demand).

## What's Next
**Monitor S1 accuracy decline** - may need learning rate adjustment or S1 loss weighting increase. Diffusion loss plateau suggests approaching convergence. Consider intermediate benchmarking at step 20k if trends persist.