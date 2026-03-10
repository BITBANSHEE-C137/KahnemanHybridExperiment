# v3 Training SITREP

## v3 Training Status
**Step 29,200/50,000** (58.4% complete) | **GPU**: 100% util, L4 @ 75°C | **Rate**: ~300 steps/hr | **ETA**: ~28h | **Spot cost**: $0.457/hr (53.3% savings vs on-demand)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 22000 | 29.70  | 3.95      | 28.3%  | 0.876 | 0.004 |
| 23000 | 29.57  | 4.19      | 26.1%  | 0.861 | 0.006 |
| 24000 | 29.53  | 4.31      | 25.2%  | 0.862 | 0.005 |
| 25000 | 29.48  | 4.08      | 26.5%  | 0.861 | 0.004 |
| 26000 | 29.58  | 4.02      | 27.7%  | 0.864 | 0.006 |
| 27000 | 29.55  | 4.32      | 24.6%  | 0.866 | 0.011 |
| 28000 | 29.40  | 4.51      | 23.8%  | 0.865 | 0.007 |
| 29000 | **29.36** | 4.27   | 25.5%  | **0.867** | 0.012 |

**Trends**: AR PPL **improving** (-1.2% from 29.7→29.36). Diffusion loss **volatile** (3.95→4.27). S1 accuracy **regressed** (-10% from peak 28.3%). AUROC **stable** ~0.86. ECE **unstable** (0.004→0.012).

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **29.36** | ✅ **MET** |
| AUROC | > 0.75 | **0.867** | ✅ **MET** |
| ECE | < 0.05 | **0.012** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.27** | 🟡 **CLOSE** |
| S1 Acc | → 40% | **25.5%** | ❌ **MISSING** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v3 AR performance on-track** (29.36 vs baseline 43.86). **S1 accuracy concerning** - significantly below v1's implied performance.

## Infrastructure
**Current**: g6.2xlarge (L4) in us-east-1a, 9h uptime. **Cost**: $24.14 total across 19 sessions. **Spot history**: Heavy reclaiming 3/9 (~15 interruptions), mostly g5/g6 instances. Current session stable since 04:25 UTC.

## What's Next
- **Monitor S1 regression** - accuracy dropped 10% from peak
- **Diffusion loss convergence** - target 4.0, currently 4.27
- After completion: comprehensive v1 vs v3 benchmarks, confidence calibration analysis
- **Risk**: Spot market volatility may extend timeline