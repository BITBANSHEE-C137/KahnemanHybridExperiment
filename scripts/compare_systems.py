"""System 1 vs System 2 comparison analysis.

Runs escalation rate, speed, quality, and confidence calibration analyses.

Usage:
    python3 -m scripts.compare_systems --checkpoint checkpoints/step_50000.pt --config configs/tiny.yaml
    python3 -m scripts.compare_systems --config configs/tiny.yaml  # pretrained baseline
"""

import argparse
import math
import time

import torch
import torch.nn.functional as F
import yaml
from transformers import GPT2Tokenizer

from src.model.dual_process_gpt2 import DualProcessGPT2
from src.model.masking import create_mask
from src.inference.generator import generate_system1, generate_system2, generate_hybrid
from src.evaluation.evaluator import compute_calibration_error
from src.evaluation.metrics import compute_auroc


def load_model(config: dict, checkpoint_path: str | None = None) -> DualProcessGPT2:
    """Load model from checkpoint or pretrained GPT-2."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if checkpoint_path:
        model = DualProcessGPT2(config, pretrained=False)
        ckpt = torch.load(checkpoint_path, map_location=device, weights_only=False)
        model.load_state_dict(ckpt["model_state_dict"])
        print(f"Loaded checkpoint: {checkpoint_path} (step {ckpt.get('step', '?')})")
    else:
        model = DualProcessGPT2(config, pretrained=True)
        print("Using pretrained GPT-2 baseline")

    model.to(device)
    model.eval()
    return model


def get_step_from_checkpoint(checkpoint_path: str | None) -> str:
    """Extract step number from checkpoint path for display."""
    if checkpoint_path is None:
        return "pretrained"
    try:
        ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
        return str(ckpt.get("step", "?"))
    except Exception:
        return "?"


@torch.no_grad()
def analyze_escalation(
    model: DualProcessGPT2,
    tokenizer: GPT2Tokenizer,
    config: dict,
    thresholds: list[float] | None = None,
    num_examples: int = 200,
) -> dict[float, float]:
    """Measure what % of tokens would be escalated at various confidence thresholds.

    Runs eval data through System 1 and checks confidence scores.

    Args:
        model: Dual-process model in eval mode.
        tokenizer: GPT-2 tokenizer.
        config: Full config dict.
        thresholds: Confidence thresholds to test.
        num_examples: Number of random sequences to evaluate.

    Returns:
        Dict mapping threshold -> escalation rate (0-100%).
    """
    if thresholds is None:
        thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]

    device = next(model.parameters()).device
    block_size = config["model"]["block_size"]
    mask_token_id = config["training"]["mask_token_id"]
    seq_len = min(128, block_size)

    all_confidences = []

    for _ in range(num_examples):
        # Generate random token sequences (approximates eval data without needing dataset)
        input_ids = torch.randint(0, config["model"]["vocab_size"], (1, seq_len), device=device)

        # Mask ~50% of tokens
        mask = torch.rand(1, seq_len, device=device) < 0.5
        if not mask.any():
            mask[0, 0] = True
        masked_ids = input_ids.clone()
        masked_ids[mask] = mask_token_id

        _, confidence, _ = model.forward_system1(masked_ids, mask)
        conf_probs = torch.sigmoid(confidence)
        all_confidences.append(conf_probs[mask].cpu())

    all_conf = torch.cat(all_confidences)

    results = {}
    for t in thresholds:
        escalated = (all_conf < t).float().mean().item() * 100
        results[t] = escalated

    return results


@torch.no_grad()
def compare_speed(
    model: DualProcessGPT2,
    config: dict,
    seq_len: int = 64,
    num_trials: int = 5,
    warmup: int = 2,
) -> dict[str, tuple[float, float]]:
    """Compare generation speed across System 1, System 2, and Hybrid.

    Args:
        model: Dual-process model in eval mode.
        config: Full config dict.
        seq_len: Length of sequences to generate.
        num_trials: Number of timed trials.
        warmup: Number of warmup runs before timing.

    Returns:
        Dict mapping mode name -> (mean_tokens_per_sec, std_tokens_per_sec).
    """
    device = next(model.parameters()).device
    mask_token_id = config["training"]["mask_token_id"]
    threshold = config["training"].get("confidence_threshold", 0.8)

    results = {}

    # --- System 1 (diffusion) ---
    speeds = []
    for trial in range(warmup + num_trials):
        if device.type == "cuda":
            torch.cuda.synchronize()
        t0 = time.time()
        generate_system1(model, seq_len, mask_token_id, num_steps=10, device=device)
        if device.type == "cuda":
            torch.cuda.synchronize()
        elapsed = time.time() - t0
        if trial >= warmup:
            speeds.append(seq_len / elapsed)
    mean_s1 = sum(speeds) / len(speeds)
    std_s1 = (sum((s - mean_s1) ** 2 for s in speeds) / len(speeds)) ** 0.5
    results["System 1 (diffusion)"] = (mean_s1, std_s1)

    # --- System 2 (AR) ---
    speeds = []
    prompt = torch.randint(0, config["model"]["vocab_size"], (1, 1), device=device)
    for trial in range(warmup + num_trials):
        if device.type == "cuda":
            torch.cuda.synchronize()
        t0 = time.time()
        generate_system2(model, prompt, max_new_tokens=seq_len - 1)
        if device.type == "cuda":
            torch.cuda.synchronize()
        elapsed = time.time() - t0
        if trial >= warmup:
            speeds.append(seq_len / elapsed)
    mean_s2 = sum(speeds) / len(speeds)
    std_s2 = (sum((s - mean_s2) ** 2 for s in speeds) / len(speeds)) ** 0.5
    results["System 2 (AR)"] = (mean_s2, std_s2)

    # --- Hybrid ---
    speeds = []
    for trial in range(warmup + num_trials):
        if device.type == "cuda":
            torch.cuda.synchronize()
        t0 = time.time()
        generate_hybrid(
            model, seq_len, mask_token_id,
            confidence_threshold=threshold,
            num_diffusion_steps=10,
            max_ar_tokens=seq_len,
            device=device,
        )
        if device.type == "cuda":
            torch.cuda.synchronize()
        elapsed = time.time() - t0
        if trial >= warmup:
            speeds.append(seq_len / elapsed)
    mean_h = sum(speeds) / len(speeds)
    std_h = (sum((s - mean_h) ** 2 for s in speeds) / len(speeds)) ** 0.5
    results[f"Hybrid (thresh={threshold})"] = (mean_h, std_h)

    return results


@torch.no_grad()
def compare_quality(
    model: DualProcessGPT2,
    config: dict,
    num_samples: int = 10,
    seq_len: int = 64,
) -> dict[str, float]:
    """Compare quality of generated text across modes.

    Generates text with each mode, then scores perplexity using System 2.

    Args:
        model: Dual-process model in eval mode.
        config: Full config dict.
        num_samples: Number of sequences to generate per mode.
        seq_len: Length of generated sequences.

    Returns:
        Dict mapping mode name -> perplexity of generated text.
    """
    device = next(model.parameters()).device
    mask_token_id = config["training"]["mask_token_id"]
    threshold = config["training"].get("confidence_threshold", 0.8)

    def score_perplexity(generated_ids: torch.Tensor) -> float:
        """Score perplexity of generated text using AR mode."""
        if generated_ids.size(1) < 2:
            return float("inf")
        # GPT2LMHeadModel.forward(labels=) auto-shifts internally
        loss = model.compute_ar_loss(generated_ids, generated_ids)
        return math.exp(min(loss.item(), 100.0))

    results = {}

    # System 1
    total_ppl = 0.0
    for _ in range(num_samples):
        ids = generate_system1(model, seq_len, mask_token_id, num_steps=10, device=device)
        total_ppl += score_perplexity(ids)
    results["System 1"] = total_ppl / num_samples

    # System 2
    total_ppl = 0.0
    for _ in range(num_samples):
        prompt = torch.randint(0, config["model"]["vocab_size"], (1, 1), device=device)
        ids = generate_system2(model, prompt, max_new_tokens=seq_len - 1)
        total_ppl += score_perplexity(ids)
    results["System 2"] = total_ppl / num_samples

    # Hybrid
    total_ppl = 0.0
    for _ in range(num_samples):
        ids, _ = generate_hybrid(
            model, seq_len, mask_token_id,
            confidence_threshold=threshold,
            num_diffusion_steps=10,
            max_ar_tokens=seq_len,
            device=device,
        )
        total_ppl += score_perplexity(ids)
    results["Hybrid"] = total_ppl / num_samples

    return results


@torch.no_grad()
def analyze_confidence(
    model: DualProcessGPT2,
    config: dict,
    num_examples: int = 200,
) -> dict[str, float]:
    """Analyze confidence calibration, AUROC, and mean confidence.

    Args:
        model: Dual-process model in eval mode.
        config: Full config dict.
        num_examples: Number of examples to evaluate.

    Returns:
        Dict with ece, auroc, mean_confidence.
    """
    device = next(model.parameters()).device
    mask_token_id = config["training"]["mask_token_id"]
    seq_len = min(128, config["model"]["block_size"])

    all_confidences = []
    all_correct = []

    for _ in range(num_examples):
        input_ids = torch.randint(0, config["model"]["vocab_size"], (1, seq_len), device=device)

        mask = torch.rand(1, seq_len, device=device) < 0.5
        if not mask.any():
            mask[0, 0] = True
        masked_ids = input_ids.clone()
        masked_ids[mask] = mask_token_id

        logits, confidence, _ = model.forward_system1(masked_ids, mask)
        conf_probs = torch.sigmoid(confidence)
        predicted_ids = logits.argmax(dim=-1)
        correct = (predicted_ids == input_ids).float()

        all_confidences.append(conf_probs[mask].cpu())
        all_correct.append(correct[mask].cpu())

    all_conf = torch.cat(all_confidences)
    all_corr = torch.cat(all_correct)

    ece = compute_calibration_error(all_conf, all_corr)
    auroc = compute_auroc(all_conf, all_corr)
    mean_conf = all_conf.mean().item()

    return {
        "ece": ece,
        "auroc": auroc,
        "mean_confidence": mean_conf,
    }


def print_results(
    escalation: dict[float, float],
    speed: dict[str, tuple[float, float]],
    quality: dict[str, float],
    confidence: dict[str, float],
    step: str,
) -> None:
    """Print formatted comparison results table."""
    w = 63
    print()
    print("\u2554" + "\u2550" * w + "\u2557")
    print(f"\u2551{'SYSTEM 1 vs SYSTEM 2 COMPARISON — step ' + step:^{w}}\u2551")
    print("\u2560" + "\u2550" * w + "\u2563")

    # Escalation
    print(f"\u2551{'':{w}}\u2551")
    print(f"\u2551  {'ESCALATION ANALYSIS':<{w-2}}\u2551")
    for thresh, rate in sorted(escalation.items()):
        line = f"    Threshold {thresh}:  {rate:.1f}% tokens escalated"
        print(f"\u2551  {line:<{w-2}}\u2551")

    # Speed
    print(f"\u2551{'':{w}}\u2551")
    print(f"\u2551  {'GENERATION SPEED (tokens/sec)':<{w-2}}\u2551")
    for mode, (mean, std) in speed.items():
        line = f"    {mode}:  {mean:.1f} \u00b1 {std:.1f}"
        print(f"\u2551  {line:<{w-2}}\u2551")

    # Quality
    print(f"\u2551{'':{w}}\u2551")
    print(f"\u2551  {'GENERATION QUALITY (perplexity of output)':<{w-2}}\u2551")
    for mode, ppl in quality.items():
        line = f"    {mode}:  {ppl:.1f}"
        print(f"\u2551  {line:<{w-2}}\u2551")

    # Confidence
    print(f"\u2551{'':{w}}\u2551")
    print(f"\u2551  {'CONFIDENCE CALIBRATION':<{w-2}}\u2551")
    print(f"\u2551    {'ECE:':<20}{confidence['ece']:>8.3f}{'':>{w-30}}\u2551")
    print(f"\u2551    {'AUROC:':<20}{confidence['auroc']:>8.3f}{'':>{w-30}}\u2551")
    print(f"\u2551    {'Mean confidence:':<20}{confidence['mean_confidence']:>8.3f}{'':>{w-30}}\u2551")

    print(f"\u2551{'':{w}}\u2551")
    print("\u255a" + "\u2550" * w + "\u255d")
    print()


def log_to_wandb(
    escalation: dict[float, float],
    speed: dict[str, tuple[float, float]],
    quality: dict[str, float],
    confidence: dict[str, float],
    step: str,
) -> None:
    """Log comparison results to W&B if available."""
    try:
        import wandb
        if wandb.run is None:
            wandb.init(project="dual-process-lm", name=f"compare-{step}", job_type="eval")

        summary = {}
        for thresh, rate in escalation.items():
            summary[f"compare/escalation_rate_{thresh}"] = rate
        for mode, (mean, std) in speed.items():
            key = mode.split("(")[0].strip().lower().replace(" ", "_")
            summary[f"compare/speed_{key}_mean"] = mean
            summary[f"compare/speed_{key}_std"] = std
        for mode, ppl in quality.items():
            key = mode.lower().replace(" ", "_")
            summary[f"compare/quality_{key}_ppl"] = ppl
        summary["compare/confidence_ece"] = confidence["ece"]
        summary["compare/confidence_auroc"] = confidence["auroc"]
        summary["compare/confidence_mean"] = confidence["mean_confidence"]

        wandb.summary.update(summary)
        wandb.finish()
        print("Results logged to W&B")
    except Exception as e:
        print(f"W&B logging skipped: {e}")


def main() -> None:
    """CLI entry point for system comparison."""
    parser = argparse.ArgumentParser(description="System 1 vs System 2 comparison")
    parser.add_argument("--config", type=str, required=True, help="Path to YAML config")
    parser.add_argument("--checkpoint", type=str, default=None, help="Path to model checkpoint")
    parser.add_argument("--num_examples", type=int, default=200, help="Examples for escalation/confidence analysis")
    parser.add_argument("--num_speed_trials", type=int, default=5, help="Timed trials for speed comparison")
    parser.add_argument("--num_quality_samples", type=int, default=10, help="Samples for quality comparison")
    parser.add_argument("--seq_len", type=int, default=64, help="Sequence length for generation tests")
    parser.add_argument("--no_wandb", action="store_true", help="Disable W&B logging")
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    step = get_step_from_checkpoint(args.checkpoint)
    model = load_model(config, args.checkpoint)

    tokenizer = GPT2Tokenizer.from_pretrained(config["model"]["name"])

    print("\n1/4 Escalation analysis...")
    t0 = time.time()
    escalation = analyze_escalation(model, tokenizer, config, num_examples=args.num_examples)
    print(f"  Done in {time.time() - t0:.1f}s")

    print("2/4 Speed comparison...")
    t0 = time.time()
    speed = compare_speed(model, config, seq_len=args.seq_len, num_trials=args.num_speed_trials)
    print(f"  Done in {time.time() - t0:.1f}s")

    print("3/4 Quality comparison...")
    t0 = time.time()
    quality = compare_quality(model, config, num_samples=args.num_quality_samples, seq_len=args.seq_len)
    print(f"  Done in {time.time() - t0:.1f}s")

    print("4/4 Confidence analysis...")
    t0 = time.time()
    confidence = analyze_confidence(model, config, num_examples=args.num_examples)
    print(f"  Done in {time.time() - t0:.1f}s")

    print_results(escalation, speed, quality, confidence, step)

    if not args.no_wandb:
        log_to_wandb(escalation, speed, quality, confidence, step)


if __name__ == "__main__":
    main()
