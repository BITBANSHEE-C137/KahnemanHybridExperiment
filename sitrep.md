# Sitrep — 2026-03-01 5:50 PM ET / 22:50 UTC

## v1 Training — running, healthy, 35% complete

- **Step ~17,400 / 50,000** (34.8%)
- GPU: 100% utilization, 16.6 / 23 GB VRAM, 51°C
- Rate: ~830 steps/hr (4.3s/step)
- ETA to 50k: ~23.5 hours at current rate
- Spot price: $0.433/hr (g5.2xlarge)
- Spot cost so far: $8.72 — projected total: $25.05 (65% savings vs on-demand)
- Instance up 20h15m since bootstrap (02:33 UTC)

## Eval trajectory (step 10k → 17k)

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 10000 | 26.5   | 5.41      | 14.7%  | 0.791 | 0.0110 |
| 11000 | 26.9   | 5.44      | 15.3%  | 0.792 | 0.0062 |
| 12000 | 27.2   | 5.09      | 17.2%  | 0.814 | 0.0173 |
| 13000 | 27.4   | 4.75      | 20.3%  | 0.821 | 0.0176 |
| 14000 | 27.9   | 5.01      | 18.8%  | 0.838 | 0.0049 |
| 15000 | 28.2   | 4.79      | 20.2%  | 0.843 | 0.0049 |
| 17000 | 28.4   | 4.36      | 24.4%  | 0.850 | 0.0068 |

Live at step ~17,400: ar_loss 3.37, diff_loss 5.44, conf_acc 0.842

## Target status (5 of 5)

- **AR PPL < 40:** 28.4 — met since step 50, drifting up slowly but solid margin
- **AUROC > 0.75:** 0.850 — met since step 8k, steady climb
- **ECE < 0.05:** 0.007 — met since step 1k, excellent calibration
- **Diff loss → 4.0:** 4.36 at eval step 17k — 91% of the way, closing in
- **S1 accuracy → 40%:** 24.4% at eval — jumped +4.2pp since step 15k, 61% of target

## Trends since last sitrep (~2.75 hours ago)

- +2,200 steps (15.2k → 17.4k)
- Diff loss: 4.79 → 4.36 (significant drop, best eval yet)
- S1 accuracy: 20.2% → 24.4% (accelerating)
- AUROC: 0.843 → 0.850

## Code & infra

- Instance on `v2-fixes` branch
- Dashboard clock shows ET + UTC (commit `fa4c07f`)
- All services healthy: sync daemon, nginx, Flask dashboard, spot price cron
- Checkpoints on disk: step_15000, step_16000, step_17000 (all synced to S3)

## What's next (after v1 completes)

1. Merge `v2-fixes` → `main`
2. Run LAMBADA + WikiText-103 benchmarks on final v1 checkpoint
3. Start v2 run with identical config (fresh, from scratch)
4. Compare v1 vs v2 (especially hybrid escalation rates with fixed confidence signal)
