# v2 Training Status SITREP

## v2 Training Status
**TRAINING HALTED** - Trainer offline, step 14400/50000 (28.8%). GPU idle (0% util, 14W). Current instance up 48min, no cost data available. **ETA unknown** - need restart.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 14000 | 30.34  | 4.31      | 25.96% | 0.853 | 0.011 |
| 15000 | 31.05  | 4.33      | 26.09% | 0.852 | 0.014 |
| 16000 | 30.79  | **4.13**  | 26.82% | 0.860 | **0.007** |
| 17000 | 30.70  | 4.52      | 23.65% | 0.860 | 0.007 |
| 18000 | 30.77  | **4.03**  | **27.23%** | **0.869** | **0.006** |
| 19000 | 30.81  | 4.31      | 24.46% | 0.860 | 0.007 |
| 20000 | 30.92  | 4.75      | 21.31% | 0.851 | 0.007 |
| 21000 | 30.88  | **4.85**  | **20.67%** | 0.851 | 0.007 |

**Trends**: AR PPL stable ~30.8. **Diffusion loss regressing** (4.03→4.85). **S1 accuracy declining** (27.2%→20.7%). AUROC peaked at step 18k. ECE excellent and stable.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **30.34** | ✅ **MET** |
| AUROC | > 0.75 | **0.853** | ✅ **MET** |
| ECE | < 0.05 | **0.011** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.31** | ⚠️ **CLOSE** |
| S1 Accuracy | → 40% | **25.96%** | ❌ **MISS** |

**3/5 targets met**. S1 accuracy **65% below target**, diffusion loss **8% above target**.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% acc/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. 

Current v2 AR performance **improved** vs v1 (30.34 vs 43.86 PPL). S1 accuracy **behind schedule** for 67% improvement target.

## Infrastructure
g5.2xlarge spot (us-east-1b), **48min uptime**. **Training halted** - trainer process down, sync running. Checkpoints through step 21k available. **Cost tracking broken** - no spot rate data.

## What's Next
**IMMEDIATE**: Restart trainer, investigate cost tracking failure. **Monitor S1 regression closely** - may need hyperparameter adjustment. After completion: benchmark suite, confidence calibration analysis, v1/v2 head-to-head comparison.