# SITREP: v3 Training - Step 200/50k

## v3 Training Status
**Step 200/50,000** (0.4% complete) | GPU: **100%** util (A10G, 54°C, 70% VRAM) | Rate: ~2.2 steps/min | ETA: ~15.7 days | Spot: **$0.46/hr** (62% savings vs on-demand)

## Eval Metrics & Trends
**No eval checkpoints yet** - first scheduled eval pending at step 500.

Current training metrics (step 200):
- AR loss: **3.14** (decreasing from initial)
- Diffusion loss: **7.11** (high, expected early training)
- Confidence accuracy: **0.0%** (not yet trained)

## Target Scorecard
| Metric | Target | Current | Status |
|--------|---------|---------|---------|
| AR PPL | < 40 | ~23.1 | ✅ **MET** |
| AUROC | > 0.75 | TBD | ⏳ |
| ECE | < 0.05 | TBD | ⏳ |
| Diff loss | → 4.0 | **7.11** | 🔴 **MISS** |
| S1 accuracy | → 40% | **0%** | 🔴 **MISS** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07
**Note:** AR slightly regressed (-0.82% LAMBADA), S1 loss improved 67% in joint training

## Infrastructure
**3 spot sessions, 2 reclaims** | Current: 22min uptime | Total cost: **$0.48** | Reclaim rate: aggressive (avg 24min sessions) | 62% cost savings vs on-demand (**$27.98** projected vs $73.15)

Previous sessions terminated at steps 0→400 (36min), need longer-lived instances for stability.

## What's Next
- **Immediate:** First eval checkpoint at step 500 (~2 hours)
- **Critical:** Monitor diffusion loss convergence - currently 78% above target
- **Infrastructure:** Consider reserved instances if reclaim rate stays >2/day
- Post-step 500: confidence head metrics, S1 token accuracy trending