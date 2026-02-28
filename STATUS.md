# Project Status — Dual-Process Language Model

**Last updated:** 2026-02-26

## Infrastructure

| Component | Status | Details |
|---|---|---|
| S3 bucket | Migrated | `s3://ml-lab-004507070771/dual-system-research-data/` |
| Instance type | Active | g5.2xlarge — NVIDIA A10G (24GB VRAM) |
| EBS root volume | 100GB | OS + Python 3.12 + ML stack (37GB used) |
| Ephemeral NVMe | 419GB | `/opt/dlami/nvme` — runtime data (HF cache, checkpoints) |
| Deploy scripts | Updated | bootstrap.sh, sync-checkpoints.sh, dashboard.py in S3 |

## Environment (baked into AMI)

| Package | Version |
|---|---|
| Python | 3.12.10 |
| PyTorch | 2.6.0+cu124 |
| CUDA | 12.4 (driver 580.126.09) |
| transformers | 5.2.0 |
| datasets | 4.6.0 |
| accelerate | 1.12.0 |
| wandb | 0.25.0 |
| safetensors | 0.7.0 |
| einops | 0.8.2 |
| scipy | 1.17.1 |

## Completed

- [x] S3 bucket consolidation — moved from standalone `dual-system-research-data` bucket to `ml-lab-004507070771/dual-system-research-data/`
- [x] Deploy scripts updated with correct bucket paths
- [x] Python 3.12 set as default `python3`
- [x] Full ML stack installed to EBS (persistent across stop/start)
- [x] GPU verified — A10G detected, CUDA matmul confirmed
- [x] requirements.txt created

## Next Steps

- [ ] Build project source code (src/, configs/, tests/)
- [ ] Create AMI snapshot with current environment
- [ ] First smoke test on tiny config
