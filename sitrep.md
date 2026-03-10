# SITREP: v3 Training Status

## v3 Training Status
**Step 28,600 / 50,000** (57.2% complete)  
**GPU**: L4 @ 100% util, 73W/72W limit, 82°C, 16.6/23GB VRAM  
**Rate**: ~800 steps/8hr session  
**ETA**: ~27 hours remaining  
**Spot Cost**: $0.46/hr (53% savings), **$3.69** current session, **$23.69 total**

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|---------|-----------|---------|-------|--------|
| 21000 | 29.94   | 4.26      | 26.8%   | 0.856 | 0.0116 |
| 22000 | 29.70   | 3.95      | 28.3%   | 0.876 | 0.0039 |
| 23000 | 29.57   | 4.19      | 26.1%   | 0.861 | 0.0059 |
| 24000 | 29.53   | 4.31      | 25.2%   | 0.862 | 0.0055 |
| 25000 | 29.48   | 4.08      | 26.5%   | 0.861 | 0.0042 |
| 26000 | 29.58   | 4.02      | 27.7%   | 0.864 | 0.0063 |
| 27000 | 29.55   | 4.32      | 24.6%   | 0.866 | 0.0109 |
| **28000** | **29.40** | **4.51** | **23.8%** | **0.865** | **0.0068** |

**Trends**: AR PPL slowly improving (~29.9→29.4). S1 accuracy **declining** (28.3%→23.8% since step 22k). Diff loss volatile, trending up. AUROC stable ~0.86. ECE well-controlled.

## Target Scorecard

| Metric | Target | Current | Status |
|--------|---------|---------|--------|
| AR PPL | < 40 | **29.4** | ✅ **MET** |
| AUROC | > 0.75 | **0.865** | ✅ **MET** |
| ECE | < 0.05 | **0.0068** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.51** | ❌ Moving away |
| S1 Accuracy | → 40% | **23.8%** | ❌ **Regressing** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v3 AR performance strong vs v1, but S1 token accuracy concerning.**

## Infrastructure
**19 spot sessions**, frequent interruptions 3/9 (12+ reclaims in 4hrs)  
Current: g6.2xlarge, 8hr uptime, stable since 04:25 UTC  
**Spot savings critical** - saved $20+ vs on-demand ($43.39)  
Checkpoints: 26k/27k/28k syncing properly

## What's Next
**Immediate concern**: S1 accuracy regression needs investigation  
After 50k: Full benchmark suite, v1→v3 comparison analysis  
**Risk**: May need hyperparameter adjustment if S1 doesn't recover