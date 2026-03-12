# v3 Training Status

**TRAINING COMPLETE** - Step **50,000/50,000** (100.0%)

Current instance idle (step 0 shown due to restart). GPU: NVIDIA L4 at 0% util, trainer stopped. Last checkpoint: **step_50000.pt** (1.5GB, saved 11h ago). Sync running.

Spot rate: **$0.42/hr** (57% savings vs on-demand $0.98/hr). Current session cost: $0.14.

---

# Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 43000 | 28.14 | 4.20 | 25.9% | 0.869 | 0.010 |
| 44000 | 28.07 | **4.40** | 24.9% | 0.867 | 0.010 |
| 45000 | **27.95** | 4.16 | 26.5% | **0.870** | 0.011 |
| 46000 | 28.13 | **3.94** | **28.1%** | 0.866 | **0.016** |
| 47000 | 28.09 | **3.88** | **29.3%** | **0.870** | 0.014 |
| 48000 | 28.04 | 4.19 | 26.1% | **0.870** | 0.012 |
| 49000 | 28.05 | **4.41** | 24.9% | 0.867 | 0.012 |
| 50000 | **27.99** | 4.16 | 26.5% | **0.870** | 0.012 |

**Trends:** AR PPL stable ~28 (slight improvement). Diffusion loss volatile but trending down. S1 accuracy peaked at 29.3% (step 47k), regressed to 26.5%. AUROC consistent at 0.87. ECE spiked briefly at 46k.

---

# Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **27.99** | ✅ **MET** |
| AUROC | > 0.75 | **0.870** | ✅ **MET** |
| ECE | < 0.05 | **0.012** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.16** | 🔄 **CLOSE** |
| S1 Accuracy | → 40% | **26.5%** | ❌ **MISS** |

**3/5 targets met.** Diffusion loss 4% above target. S1 accuracy significantly below 40% target.

---

# v1 Benchmark Baseline

v1 final metrics: LAMBADA 94.26% acc, PPL 1.46; WikiText-103 PPL 43.86; S1 loss 4.12.
Pretrained GPT-2: LAMBADA 95.08%, WikiText PPL 29.07.

**Current v3 vs v1:** AR improved (27.99 vs 43.86 PPL). S1 accuracy at 26.5% vs v1's implied ~67% improvement from 4.12 loss baseline.

---

# Infrastructure

Total project cost: **$40.42** across 24 spot sessions. Current g6.2xlarge at $0.42/hr (57% savings).

**Spot reliability issues:** 15+ reclaims between steps 19k-25k (Mar 9). Stabilized with g6.2xlarge instances for final 10k steps. No interruptions during final training phase.

**Uptime:** 20 min current session, stable sync process.

---

# What's Next

Training complete at 50k steps. **Ready for v3 benchmarks:** LAMBADA, WikiText-103 evaluation. Compare v1→v3 AR improvements and S1 performance regression analysis. Investigate confidence head calibration given excellent ECE performance. Deploy checkpoint for production inference testing.