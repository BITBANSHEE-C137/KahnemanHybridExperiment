# SITREP: v3 Training Status - Step 34200

## v3 Training Status
**Progress**: 34,200/50,000 steps (**68.4%** complete)  
**GPU**: L4 @ 100% util, 71W/72W, 80°C, 16.6GB/23GB VRAM  
**Rate**: ~200 steps/hr (17.3hrs runtime)  
**ETA**: ~79 hours remaining  
**Spot Cost**: $8.06 current session, **53.1% savings** ($0.46/hr vs $0.98/hr on-demand)

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 27000 | 29.55 | 4.316 | 24.6% | 0.866 | 0.011 |
| 28000 | 29.40 | 4.513 | 23.8% | 0.865 | 0.007 |
| 29000 | 29.36 | 4.266 | 25.5% | 0.867 | 0.012 |
| 30000 | 29.16 | 4.337 | 24.6% | 0.868 | 0.005 |
| 31000 | 28.95 | 4.469 | 23.3% | **0.871** | 0.003 |
| 32000 | 29.04 | 4.350 | 24.2% | 0.865 | 0.009 |
| 33000 | 28.93 | **4.085** | **26.6%** | 0.861 | 0.009 |
| 34000 | **28.85** | 4.149 | 25.6% | **0.871** | **0.007** |

**Trends**: AR perplexity steadily improving (**-0.7 over 7k steps**). Diffusion loss volatile but trending down. S1 accuracy peaked at 26.6% then regressed slightly. AUROC stable ~0.87. ECE excellent and stable.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **28.85** | ✅ **ACHIEVED** |
| AUROC | > 0.75 | **0.871** | ✅ **ACHIEVED** |
| ECE | < 0.05 | **0.007** | ✅ **ACHIEVED** |
| Diff Loss | → 4.0 | **4.15** | 🟡 **CLOSE** (96.3%) |
| S1 Accuracy | → 40% | **25.6%** | ❌ **BEHIND** (64.0%) |

**3/5 targets met**. Confidence metrics excellent. S1 accuracy lagging significantly.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v3 AR PPL (28.85) already beating v1 WikiText baseline (43.86)**

## Infrastructure
**Current**: g6.2xlarge, us-east-1a, 17.6hr uptime  
**History**: 19 sessions, **excessive spot reclaims** (especially 3/9 evening cascade)  
**Total Cost**: $28.05 across all sessions  
**Stability**: Current session stable since 04:25 UTC

## What's Next
Continue to 50k steps (~3.3 days). **S1 accuracy plateau concerning** - may need architecture review. After completion: comprehensive v1 vs v3 benchmarks, confidence calibration analysis.