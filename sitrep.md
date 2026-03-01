# Sitrep — 2026-03-01 3:05 PM ET / 20:05 UTC

## v1 Training — running, healthy, 30% complete

- **Step ~15,200 / 50,000** (30.4%)
- GPU: 99% utilization, 16.6 / 23 GB VRAM, 52°C
- Rate: ~830 steps/hr (4.3s/step)
- ETA to 50k: ~23 hours at current rate
- Spot price: $0.433/hr (g5.2xlarge)
- Spot cost so far: $7.53 — projected total: $24.76 (65% savings vs on-demand)
- Instance up 17h29m since last spot recovery (bootstrap at 02:33 UTC)

## Eval trajectory (step 10k → 15k)

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 10000 | 26.5   | 5.41      | 14.7%  | 0.791 | 0.0110 |
| 11000 | 26.9   | 5.44      | 15.3%  | 0.792 | 0.0062 |
| 12000 | 27.2   | 5.09      | 17.2%  | 0.814 | 0.0173 |
| 13000 | 27.4   | 4.75      | 20.3%  | 0.821 | 0.0176 |
| 14000 | 27.9   | 5.01      | 18.8%  | 0.838 | 0.0049 |
| 15000 | 28.2   | 4.79      | 20.2%  | 0.843 | 0.0049 |

Live at step ~15,200: ar_loss 3.45, diff_loss 5.12, conf_acc 0.860

## Target status (5 of 5)

- **AR PPL < 40:** 28.2 — met since step 50, drifting up slowly but solid margin
- **AUROC > 0.75:** 0.843 — met since step 8k, still climbing
- **ECE < 0.05:** 0.005 — met since step 1k, excellent calibration
- **Diff loss → 4.0:** 4.79 at eval / 4.32 best live (step 14800) — 85% of the way
- **S1 accuracy → 40%:** 20.2% at eval — crossed 20%, halfway to target

## Code & infra

- Instance on `v2-fixes` branch — training-neutral, v2 fixes are eval/docs only
- Dashboard clock now shows ET + UTC (commit `fa4c07f`)
- All services healthy: sync daemon, nginx, Flask dashboard, spot price cron
- Checkpoints on disk: step_13000, step_14000, step_15000 (all synced to S3)

## What's next (after v1 completes)

1. Merge `v2-fixes` → `main`
2. Run LAMBADA + WikiText-103 benchmarks on final v1 checkpoint
3. Start v2 run with identical config (fresh, from scratch)
4. Compare v1 vs v2 (especially hybrid escalation rates with fixed confidence signal)
