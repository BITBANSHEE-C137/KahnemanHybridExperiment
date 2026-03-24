# v4 Training Status

**Step 40,700 / 75,000** (54.3% complete) | GPU: 100% util, 200W/300W, 56°C | VRAM: 16.6GB/23.0GB used
Rate: ~1.1 steps/min | **ETA: ~26 hours** | Current spot: **$0.44/hr** (64% savings vs on-demand)

# Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 37000 | 30.10 | 4.34 | 27.7% | 0.854 | 0.020 |
| 38000 | 29.43 | 4.38 | 27.7% | 0.856 | 0.016 |
| 39000 | 29.17 | 4.08 | 30.5% | 0.857 | 0.008 |
| 40000 | 29.05 | **3.79** | **32.7%** | **0.862** | 0.018 |
| 40500 | **28.94** | 3.80 | 32.9% | 0.862 | **0.009** |

**Trends:** Strong AR improvement (-1.16 PPL). Diffusion loss volatile but trending down. S1 accuracy surged +5.2% since step 37k. AUROC steady climb. ECE excellent at 0.009.

# Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **28.94** | ✅ **BEAT** |
| AUROC | > 0.75 | **0.862** | ✅ **BEAT** |
| ECE | < 0.05 | **0.009** | ✅ **BEAT** |
| Diff Loss | → 4.0 | **3.80** | ✅ **BEAT** |
| S1 Accuracy | → 40% | **32.9%** | 🔄 **82% there** |

**4/5 targets met.** S1 accuracy climbing fast - could hit 40% by step 50k at current trajectory.

# v1 Benchmark Baseline

v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12
Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL

**v4 is crushing v1:** AR PPL improved 34% (43.86→28.94). Diffusion performance similar to v1 S1 final. On track to significantly outperform v1 across all metrics.

# Infrastructure

**Current session:** 10.5hrs uptime, $4.62 spot cost
**Total project:** 73 sessions, **$53.00 total** (vs $141 on-demand)
**Spot reliability:** Solid run - longest stable session in weeks. A10G performing well at 200W power draw.

**Recent issues:** Heavy spot volatility days 3/19-3/21 with 50+ reclaims. Stabilized since 3/24.

# What's Next

- **Step 45k:** Mid-training eval checkpoint
- **Step 50k:** Compare S1 accuracy vs v1 final (32.9% → target 40%)  
- **Step 60k:** Full benchmark suite if metrics hold
- **Training complete (~26hrs):** Comprehensive v1 vs v4 analysis, confidence calibration deep-dive

**Risk:** Spot market volatility could fragment final training phase.