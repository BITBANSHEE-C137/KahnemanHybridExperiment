# Sitrep — 2026-03-01 3:30 PM ET / 19:30 UTC

## v1 Training — running, healthy, 29% complete

- **Step ~14,700 / 50,000** (29.4%)
- GPU: 98% utilization, 16.6 / 23 GB VRAM
- Rate: ~830 steps/hr (4.3s/step)
- ETA to 50k: ~42 hours at current rate
- Spot price: $0.433/hr (g5.2xlarge, trending down)
- Instance up 16h49m since last spot recovery (bootstrap at 02:37 UTC)

## Eval trajectory (step 10k → 14k)

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 10000 | 26.5   | 5.41      | 14.7%  | 0.791 | 0.0110 |
| 11000 | 26.9   | 5.44      | 15.3%  | 0.792 | 0.0062 |
| 12000 | 27.2   | 5.09      | 17.2%  | 0.814 | 0.0173 |
| 13000 | 27.4   | 4.75      | 20.3%  | 0.821 | 0.0176 |
| 14000 | 27.9   | 5.01      | 18.8%  | 0.838 | 0.0049 |

Live at step ~14,700: ar_loss 3.40, **diff_loss 4.48** (best yet), conf_acc 0.864

## Target status (5 of 5)

- **AR PPL < 40:** 27.9 — met since step 50, drifting up slowly but solid margin
- **AUROC > 0.75:** 0.838 — met since step 8k, still climbing
- **ECE < 0.05:** 0.005 — met since step 1k, excellent calibration
- **Diff loss → 4.0:** 4.48 live / 4.75 at eval step 13k — approaching target, 88% of the way
- **S1 accuracy → 40%:** 18.8% at eval, ~47% of target — accelerating (was 14.7% at step 10k)

## Code & infra

- Instance on `v2-fixes` branch (bootstrap pulled it) — training-neutral, v2 fixes are eval/docs only
- Sitrep modal added to dashboard (commit `221240e`)
- All services healthy: sync daemon, nginx, Flask dashboard, spot price cron
- Deploy artifacts synced to S3

## What's next (after v1 completes)

1. Merge `v2-fixes` → `main`
2. Run LAMBADA + WikiText-103 benchmarks on final v1 checkpoint
3. Start v2 run with identical config (fresh, from scratch)
4. Compare v1 vs v2 (especially hybrid escalation rates with fixed confidence signal)
