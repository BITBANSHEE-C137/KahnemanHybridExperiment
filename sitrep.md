# v3 Training Status SITREP

## v3 Training Status
**Step 13,200/50,000** (26.4% complete) • GPU util **97%** A10G • **203W/300W** @ 53°C • Rate ~400 steps/hr • **ETA: ~38 hours** • Spot cost **$0.46/hr** (62% savings) • Total spent **$10.51**

## Eval Metrics & Trends
| Step | AR PPL | AUROC | ECE | Diff Loss | S1 Acc |
|------|--------|-------|-----|-----------|---------|
| 6000 | 24.85 | 0.719 | 0.012 | 6.08 | 9.9% |
| 8000 | 26.29 | 0.785 | 0.008 | 5.60 | 12.6% |
| 10000 | 27.55 | 0.828 | 0.005 | 4.98 | 19.0% |
| 12000 | 28.12 | 0.853 | 0.007 | 4.31 | 25.0% |
| **13000** | **28.41** | **0.844** | **0.011** | **4.42** | **24.1%** |

**Concerning trends**: AR PPL degrading (+14% since step 6k). AUROC plateaued/slight regression. ECE uptick suggests overconfidence creep. **S1 accuracy stalled** at ~24% (down from 25% at 12k). Diffusion loss volatile.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|---------|---------|---------|
| AR PPL | < 40 | **28.41** | ✅ |
| AUROC | > 0.75 | **0.844** | ✅ |
| ECE | < 0.05 | **0.011** | ✅ |
| Diff Loss | → 4.0 | **4.42** | 🔶 Close |
| S1 Accuracy | → 40% | **24.1%** | ❌ Behind |

**3/5 targets met**. S1 accuracy significantly behind pace for 40% target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Current v3 AR PPL (**28.41**) already **35% better** than v1's WikiText performance. S1 accuracy trending toward similar gains vs v1's final loss.

## Infrastructure
**Current session**: 16.2h uptime, no interruptions • **Previous session**: Spot reclaim after 6.8h (steps 400-1000) • **Total cost**: $10.48 across 2 sessions • Checkpoint sync active • **Risk**: Stable spot pricing $0.46/hr in us-east-1a

## What's Next
**Monitor S1 stagnation** - may need LR adjustment or curriculum changes. AR quality exceeding expectations but **confidence calibration regressing**. After step 15k: deep dive on confidence head dynamics and S1 token distribution analysis.