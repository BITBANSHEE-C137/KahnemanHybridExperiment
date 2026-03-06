# v2 Training Status SITREP

## v2 Training Status
**Step 31,100/50,000 (62.2%)**  
GPU: A10G @ **100% util**, 192W/300W, 53°C, 16.6GB/23GB VRAM  
Rate: ~6.5 steps/min | ETA: **~2 days** | Spot: **$0.45/hr** (62.8% savings)  
Current session: 3h57m uptime, $1.78 spent

## Eval Metrics & Trends

| Step | AR PPL | AUROC | ECE | Diff Loss | S1 Acc |
|------|--------|-------|-----|-----------|--------|
| 24k  | 30.98  | 0.863 | 0.005 | 4.46 | 24.3% |
| 25k  | 31.22  | 0.860 | **0.012** | 4.20 | **27.6%** |
| 26k  | 31.46  | 0.863 | **0.018** | 4.06 | **28.0%** |
| 27k  | 31.46  | 0.862 | 0.009 | **4.48** | 24.4% |
| 28k  | 31.32  | **0.872** | 0.007 | **3.95** | **28.2%** |
| 29k  | 31.43  | 0.860 | **0.022** | 4.21 | 27.7% |
| 30k  | 31.68  | 0.864 | **0.023** | 4.08 | **28.1%** |
| 31k  | **31.60** | 0.862 | 0.014 | **4.49** | 24.5% |

**Trends:** AR PPL **stable** ~31.5. AUROC **strong** 0.86+. ECE **volatile** (0.005→0.023). Diff loss **unstable** 3.95-4.49. S1 accuracy **oscillating** 24-28%.

## Target Scorecard
❌ **AR PPL < 40:** 31.6 ✅  
✅ **AUROC > 0.75:** 0.862 ✅  
⚠️ **ECE < 0.05:** 0.014 ✅ (volatile)  
❌ **Diff loss → 4.0:** 4.49 (regressed from 3.95)  
❌ **S1 accuracy → 40%:** 24.5% (dropped from 28.1%)

**3/5 targets met**

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
v2 current: AR PPL **better** than v1 (31.6 vs 43.86), diff loss **similar** to v1

## Infrastructure
**13 spot sessions**, $20.80 total cost  
**12 spot reclaims** in 2 days - high churn rate  
Current: g5.2xlarge us-east-1b, stable 4h  
Checkpoint: step_31000.pt (1.5GB) synced

## What's Next
Complete v2 training (~18.9k steps remaining)  
Run full benchmark suite vs v1 baselines  
**Priority:** Stabilize diffusion loss oscillation and S1 accuracy regression