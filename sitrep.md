# v3 Training SITREP

## v3 Training Status
**Step 18,200/50,000** (36.4% complete) • **GPU: 98% util** A10G @ 208W/300W, 50°C, 16.2/23GB VRAM • **Rate**: ~229 steps/hr • **ETA**: ~6.1 days • **Spot cost**: $0.45/hr (62% savings vs on-demand $1.21/hr)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Tok Acc | Conf AUROC | Conf ECE |
|------|--------|-----------|-------------|------------|----------|
| 11000| 27.85  | 4.43      | 22.0%       | 0.853      | 0.0102   |
| 12000| 28.12  | 4.31      | 25.0%       | 0.853      | 0.0066   |
| 13000| 28.41  | 4.42      | 24.1%       | 0.844      | 0.0110   |
| 14000| 28.51  | 4.29      | 24.7%       | 0.852      | 0.0087   |
| 15000| 28.64  | 4.50      | 23.7%       | 0.864      | 0.0052   |
| 16000| 28.66  | 4.38      | 23.5%       | 0.856      | 0.0104   |
| 17000| 28.89  | 4.34      | 25.2%       | 0.858      | 0.0079   |
| 18000| **28.99** | **4.44** | **23.0%** | **0.858** | **0.0098** |

**Trends**: AR PPL slowly degrading (+1.14 from step 11k). S1 accuracy volatile, recent drop to 23%. AUROC stable ~0.85. ECE well-controlled <0.01.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **28.99** | ✅ **MET** |
| AUROC > 0.75 | **0.858** | ✅ **MET** |
| ECE < 0.05 | **0.0098** | ✅ **MET** |
| Diff loss -> 4.0 | **4.44** | 🟡 **11% above** |
| S1 accuracy -> 40% | **23.0%** | ❌ **42.5% below** |

**3/5 targets met**. S1 accuracy significantly underperforming, diff loss plateau at ~4.4.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. Current v3 AR PPL (**28.99**) outperforms v1 WikiText baseline, but S1 performance (**23%** accuracy) lags v1's implied ~67% improvement trajectory.

## Infrastructure
**Current session**: 22.1hrs uptime, $10.08 spot cost. **Previous session**: spot reclaim after 6.8hrs, $3.11 cost. **Total**: 2 sessions, $13.20 total cost vs $26.86 on-demand. No current stability issues, checkpoints syncing normally.

## What's Next
**S1 accuracy regression** needs investigation - volatile 22-25% range suggests training instability. Consider learning rate adjustment or S1 loss weighting. Diff loss plateau may require hyperparameter tuning. Monitor for potential spot reclaim given 22hr runtime.