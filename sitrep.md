# Sitrep — 2026-03-01T19:04 UTC

## v1 Training — running, healthy
- Step ~14,000 / 50,000 (28%)
- GPU: 100% utilization, 16.6 / 23 GB VRAM
- Latest checkpoint: `step_14000.pt` (18:34 UTC)
- Checkpoints every ~73 min → ~1,000 steps/hr
- ETA to 50k: ~36 hours at current rate

## v2-fixes branch — complete, tested, pushed
- 5 commits on `v2-fixes`, branched from `main` at `10f4bc4`
- All 6 planned fixes implemented (fixes #1 + #3 bundled)
- 14/14 tests pass
- Parked until v1 finishes → merge to `main`

## `main` branch — CLAUDE.md updated
- 276-line audit version deployed
- Bootstrap pulls `main`, so spot recovery stays on v1 code (no v2-fixes code)

## What's next (after v1 completes)
1. Merge `v2-fixes` → `main`
2. Run LAMBADA + WikiText-103 benchmarks on final v1 checkpoint
3. Start v2 run with identical config
4. Compare v1 vs v2 (especially hybrid escalation rates with fixed confidence signal)
