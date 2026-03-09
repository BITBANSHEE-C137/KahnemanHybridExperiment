# v3 Training SITREP

## v3 Training Status
**Step 19,000/50,000 (38%)** - Training resumed after spot reclaim. GPU: **99% util**, L4 running at 70W/72W, 59°C, 16.5GB/23GB VRAM. No current rate data (just restarted). **ETA**: ~31k steps remaining. Current spot: **$0.37/hr** (54% savings vs on-demand).

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 12000 | 28.12  | 4.31      | 25.0%  | 0.853 | 0.007 |
| 13000 | 28.41  | 4.42      | 24.1%  | 0.844 | 0.011 |
| 14000 | 28.51  | 4.29      | 24.7%  | 0.852 | 0.009 |
| 15000 | 28.64  | 4.50      | 23.7%  | 0.864 | 0.005 |
| 16000 | 28.66  | 4.38      | 23.5%  | 0.856 | 0.010 |
| 17000 | 28.89  | 4.34      | 25.2%  | 0.858 | 0.008 |
| 18000 | 28.99  | 4.44      | 23.0%  | 0.858 | 0.010 |
| 19000 | 29.21  | 4.39      | 22.1%  | 0.866 | 0.011 |

**Trends**: AR PPL **degrading** (+4% over 7k steps). S1 accuracy **declining** (-11%). AUROC **stable/improving**. ECE volatile but acceptable.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **29.21** | ✅ |
| AUROC | > 0.75 | **0.866** | ✅ |
| ECE | < 0.05 | **0.011** | ✅ |
| Diff Loss | → 4.0 | **4.39** | ⚠️ |
| S1 Accuracy | → 40% | **22.1%** | ❌ |

**2/5 targets not met**. S1 accuracy concerning at 22% vs 40% target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Current v3 AR PPL (**29.21**) significantly better than v1 (**43.86**). S1 performance (**22% acc**) still well below target but training continues.

## Infrastructure
**Session 3** on g6.xlarge spot (9min uptime). Previous sessions: g5.2xlarge ran 18.3k steps over 1.6 days before reclaim. **Total cost: $13.87** across 3 sessions. Current 54% spot savings. Checkpoints syncing properly.

## What's Next
Monitor S1 accuracy trend - **critical metric underperforming**. AR PPL degradation needs investigation. After 50k steps: comprehensive v1 vs v3 comparison, confidence calibration analysis.