# v2 Training SITREP

## v2 Training Status
**Step 34,800 / 50,000 (69.6%)** | A10G @ 100% util, 188W/300W, 48°C | **Rate**: ~400 steps/hr | **ETA**: ~38 hours | **Spot cost**: $0.45/hr (62.7% savings)

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 27000 | 31.46  | 4.48      | 24.4%  | 0.862 | 0.0095 |
| 28000 | 31.32  | **3.95**  | **28.2%** | **0.872** | **0.0073** |
| 29000 | 31.43  | 4.21      | 27.7%  | 0.860 | 0.0217 |
| 30000 | 31.68  | 4.08      | **28.1%** | 0.864 | 0.0234 |
| 31000 | 31.60  | 4.49      | 24.5%  | 0.862 | 0.0141 |
| 32000 | 31.39  | **3.96**  | **28.4%** | **0.871** | 0.0129 |
| 33000 | 31.29  | 4.23      | 25.4%  | 0.864 | **0.0075** |
| 34000 | **31.13** | 4.68   | 22.0%  | 0.854 | **0.0086** |

**Trends**: AR perplexity slowly improving. Diffusion loss volatile but averaging ~4.2. **S1 accuracy regressed** from 28% to 22%. AUROC stable ~0.86. ECE excellent <0.01.

## Target Scorecard
- ✅ **AR PPL < 40**: 31.13 (BEATING)
- ✅ **AUROC > 0.75**: 0.854 (BEATING) 
- ✅ **ECE < 0.05**: 0.0086 (BEATING)
- ❌ **Diff loss → 4.0**: 4.68 (MISSING by 0.68)
- ❌ **S1 accuracy → 40%**: 22.0% (MISSING by 18pp)

**3/5 targets met**. S1 accuracy concerning - down from 28% peak.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v2 AR PPL (31.13) beating v1 (43.86)** but still behind pretrained GPT-2.

## Infrastructure
**Current session**: 8.5hrs uptime, $3.78 spot cost. **Total**: 13 sessions, **$22.79 spent**, 62.7% savings vs on-demand. **Multiple spot reclaims** (sessions 2-12), but current instance stable. No infrastructure issues.

## What's Next
**15,200 steps remaining** (~38hrs). After v2 completion: comprehensive v1 vs v2 benchmarks, analyze S1 accuracy regression, evaluate confidence calibration improvements.