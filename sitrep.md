# ML Ops SITREP - v3 Training

## v3 Training Status
**Step 5800/50000 (11.6%)** | GPU: **100% util**, A10G @ 210W/60°C | Rate: ~23 steps/hr | **ETA: ~80 days** | Spot: **$0.46/hr** (-62% vs on-demand)

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 1000 | 21.29  | 6.75      | 5.0%   | 0.557 | 0.006 |
| 2000 | 22.53  | 6.54      | 6.4%   | 0.613 | 0.004 |
| 3000 | 23.17  | 6.38      | 7.6%   | 0.638 | 0.010 |
| 4000 | 23.71  | 6.29      | 8.5%   | 0.672 | 0.011 |
| 5000 | **24.35** | **6.12** | **9.1%** | **0.696** | **0.008** |

**Trends**: AR PPL **degrading** (+14% since step 1k). Diffusion loss **improving** (-9%). S1 accuracy **steady climb** (+82%). AUROC **improving** (+25%). ECE stable/low.

## Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **24.35** | ✅ **MET** |
| AUROC | > 0.75 | **0.696** | ❌ Need +8% |
| ECE | < 0.05 | **0.008** | ✅ **MET** |
| Diff Loss | → 4.0 | **6.12** | ❌ Need -35% |
| S1 Accuracy | → 40% | **9.1%** | ❌ Need +339% |

**2/5 targets met**. S1 accuracy severely lagging baseline trajectory.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. 

Current v3 AR performance **superior** to v1 baseline (-45% PPL). S1 training **extremely slow** vs v1 trajectory.

## Infrastructure
**7.2hrs uptime** on current g5.2xlarge spot (session 2). **Total cost: $6.36** across 2 sessions. **1 spot reclaim** at step 1000 (6.8hr session). No current issues. Checkpoints: 3k, 4k, 5k available.

## What's Next
**Critical**: S1 accuracy severely underperforming - investigate learning rate, loss weighting. Monitor AR PPL regression trend. ETA suggests **80-day completion** - evaluate acceleration options. Post-v3: comprehensive benchmarking vs v1/v2, confidence calibration analysis.