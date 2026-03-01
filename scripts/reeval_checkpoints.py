"""Re-evaluate all historical checkpoints with the fixed AR PPL computation.

Downloads checkpoints from S3 as needed, runs the full evaluator against each,
and writes corrected eval metrics to eval_metrics/ JSON files and appends
corrected [eval] lines to the wandb output log.
"""

import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import torch
import yaml

# Ensure project is importable
sys.path.insert(0, "/home/ubuntu/KahnemanHybridExperiment")

from src.model.dual_process_gpt2 import DualProcessGPT2
from src.data.openwebtext import create_eval_dataloader
from src.evaluation.evaluator import evaluate


def main():
    project_dir = Path("/home/ubuntu/KahnemanHybridExperiment")
    config_path = project_dir / "configs" / "tiny.yaml"
    checkpoint_dir = Path("/opt/dlami/nvme/ml-lab/checkpoints")
    eval_metrics_dir = project_dir / "eval_metrics"
    eval_metrics_dir.mkdir(exist_ok=True)

    s3_prefix = "s3://ml-lab-004507070771/dual-system-research-data/checkpoints"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.bfloat16 if device.type == "cuda" else torch.float32

    # All checkpoint steps available in S3
    all_steps = [50, 100, 1000, 2000, 3000, 4000, 5000, 6000, 7000]

    # Create eval dataloader once (same for all checkpoints)
    eval_dataloader = create_eval_dataloader(config, smoke_test=False)

    results = []

    for step in all_steps:
        ckpt_path = checkpoint_dir / f"step_{step}.pt"

        # Download from S3 if not local
        if not ckpt_path.exists():
            s3_key = f"{s3_prefix}/step_{step}.pt"
            print(f"\n[download] {s3_key} -> {ckpt_path}")
            subprocess.run(
                ["aws", "s3", "cp", s3_key, str(ckpt_path)],
                check=True,
            )

        print(f"\n{'='*60}")
        print(f"Evaluating step {step}")
        print(f"{'='*60}")

        # Load model fresh from pretrained + checkpoint
        model = DualProcessGPT2(config, pretrained=True).to(device)
        ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
        model.load_state_dict(ckpt["model_state_dict"])
        model.eval()

        # Run full evaluation
        metrics = evaluate(model, eval_dataloader, config)

        print(f"  AR PPL:       {metrics['ar_perplexity']:.2f}")
        print(f"  Diff Loss:    {metrics['diff_loss']:.4f}")
        print(f"  S1 Tok Acc:   {metrics['s1_token_accuracy']:.4f}")
        print(f"  Conf Acc:     {metrics['conf_accuracy']:.4f}")
        print(f"  Conf ECE:     {metrics['conf_ece']:.4f}")
        print(f"  Conf AUROC:   {metrics['conf_auroc']:.4f}")

        # Save to eval_metrics JSON
        metrics_record = {
            "step": step,
            "ar_perplexity": metrics["ar_perplexity"],
            "diff_loss": metrics["diff_loss"],
            "s1_token_accuracy": metrics["s1_token_accuracy"],
            "conf_accuracy": metrics["conf_accuracy"],
            "conf_ece": metrics["conf_ece"],
            "conf_auroc": metrics["conf_auroc"],
            "timestamp": time.time(),
            "reeval": True,
        }
        json_path = eval_metrics_dir / f"step_{step}.json"
        with open(json_path, "w") as f:
            json.dump(metrics_record, f, indent=2)
        print(f"  Saved: {json_path}")

        results.append(metrics_record)

        # Free GPU memory
        del model, ckpt
        torch.cuda.empty_cache()

        # Remove downloaded checkpoint if it wasn't originally local
        # (keep steps 5000, 6000, 7000 which were already there)
        if step not in [5000, 6000, 7000]:
            ckpt_path.unlink(missing_ok=True)
            print(f"  Cleaned up: {ckpt_path.name}")

    # Print summary table
    print(f"\n{'='*80}")
    print("CORRECTED EVAL METRICS SUMMARY")
    print(f"{'='*80}")
    print(f"{'Step':>6} {'AR PPL':>10} {'Diff Loss':>10} {'S1 Acc':>8} {'Conf Acc':>9} {'ECE':>8} {'AUROC':>7}")
    print("-" * 80)
    for r in results:
        print(
            f"{r['step']:>6} "
            f"{r['ar_perplexity']:>10.2f} "
            f"{r['diff_loss']:>10.4f} "
            f"{r['s1_token_accuracy']*100:>7.1f}% "
            f"{r['conf_accuracy']*100:>8.1f}% "
            f"{r['conf_ece']:>8.4f} "
            f"{r['conf_auroc']:>7.4f}"
        )

    # Write corrected [eval] lines to a separate log for the dashboard to pick up
    corrected_log = project_dir / "eval_corrected.log"
    with open(corrected_log, "w") as f:
        for r in results:
            f.write(
                f"[eval] step: {r['step']} | "
                f"ar_ppl: {r['ar_perplexity']:.2f} | "
                f"diff_loss: {r['diff_loss']:.4f} | "
                f"s1_tok_acc: {r['s1_token_accuracy']:.4f} | "
                f"conf_acc: {r['conf_accuracy']:.4f} | "
                f"conf_ece: {r['conf_ece']:.4f} | "
                f"conf_auroc: {r['conf_auroc']:.4f}\n"
            )
    print(f"\nCorrected eval lines written to: {corrected_log}")
    print("Done.")


if __name__ == "__main__":
    main()
