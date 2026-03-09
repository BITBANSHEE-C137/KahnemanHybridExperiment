# v3 Training SITREP

## v3 Training Status
**Step 14,900/50,000 (29.8%)** | GPU: 100% util, 201W/300W, 49°C | VRAM: 16.2GB/23GB | Rate: ~2.3 steps/min | **ETA: ~15.2 days** | Spot cost: **$0.45/hr** (62% savings)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|--------|-----|
| 7000 | 25.48 | 5.87 | 10.6% | 0.739 | 0.0089 |
| 8000 | 26.29 | 5.60 | 12.6% | 0.785 | 0.0076 |
| 9000 | 26.95 | 5.06 | 18.4% | 0.805 | 0.0059 |
| 10000| 27.55 | 4.98 | 19.0% | 0.828 | 0.0053 |
| 11000| 27.85 | 4.43 | 22.0% | **0.853** | 0.0102 |
| 12000| 28.12 | 4.31 | **25.0%** | 0.853 | 0.0066 |
| 13000| 28.41 | 4.42 | 24.1% | 0.844 | 0.0110 |
| 14000| **28.51** | **4.29** | 24.7% | 0.852 | **0.0087** |

**Trends:** AR PPL degrading (+11.9% from step 7k). Diffusion loss improving (-27%). S1 accuracy plateauing ~24-25%. AUROC strong, ECE volatile.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.51** | ✅ |
| AUROC > 0.75 | **0.852** | ✅ |
| ECE < 0.05 | **0.0087** | ✅ |
| Diff loss → 4.0 | **4.29** | 🔄 (93% progress) |
| S1 accuracy → 40% | **24.7%** | 🔄 (62% progress) |

**3/5 targets met.** Diffusion loss nearly there, S1 accuracy lagging.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. **Current AR PPL (28.51) already better than v1 WikiText baseline (43.86)** but worse than GPT-2.

## Infrastructure
**Current session:** 18.1hrs uptime, $8.31 spent. **Previous session:** 6.8hrs, $3.11 (spot reclaimed). **Total:** 2 sessions, $11.38 vs $22.01 on-demand. No current issues, sync running.

## What's Next
**Monitor AR PPL regression** - concerning +3 point drift since step 7k. S1 accuracy plateau needs investigation. Target completion ~24 days at current rate. Post-v3: comprehensive v1/v2/v3 benchmark comparison, confidence calibration analysis.