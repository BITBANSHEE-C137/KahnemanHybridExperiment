"""Benchmark evaluation: LAMBADA and WikiText-103.

Evaluates System 1 (diffusion) and System 2 (AR) on standard LM benchmarks.

Usage:
    python3 -m scripts.benchmark --checkpoint checkpoints/step_50000.pt --config configs/tiny.yaml
    python3 -m scripts.benchmark --config configs/tiny.yaml  # pretrained GPT-2 baseline
"""

import argparse
import json
import math
import os
import time
from pathlib import Path

import torch
import torch.nn.functional as F
import yaml
from datasets import load_dataset
from transformers import GPT2Tokenizer

from src.model.dual_process_gpt2 import DualProcessGPT2
from src.utils.s3_sync import upload_benchmark_results, DATA_DIR


def load_model(config: dict, checkpoint_path: str | None = None) -> DualProcessGPT2:
    """Load model from checkpoint or pretrained GPT-2.

    Args:
        config: Model configuration dict.
        checkpoint_path: Path to .pt checkpoint, or None for pretrained.

    Returns:
        Model in eval mode on appropriate device.
    """
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
def eval_lambada(
    model: DualProcessGPT2,
    tokenizer: GPT2Tokenizer,
    config: dict,
    max_examples: int = 500,
) -> dict[str, float]:
    """Evaluate on LAMBADA last-word prediction.

    For each example, the model sees the context and must predict the final word.
    System 2 (AR): standard next-token prediction of last word's tokens.
    System 1 (diffusion): unmask the last word given full context.

    Args:
        model: Dual-process model in eval mode.
        tokenizer: GPT-2 tokenizer.
        config: Full config dict.
        max_examples: Cap on number of examples to evaluate.

    Returns:
        Dict with s2_accuracy, s2_perplexity, s1_accuracy.
    """
    device = next(model.parameters()).device
    mask_token_id = config["training"]["mask_token_id"]
    block_size = config["model"]["block_size"]

    dataset = load_dataset("EleutherAI/lambada_openai", "default", split="test", trust_remote_code=True)

    s2_correct = 0
    s2_total_loss = 0.0
    s2_total_tokens = 0
    s1_correct = 0
    total = 0

    for i, example in enumerate(dataset):
        if i >= max_examples:
            break

        text = example["text"]
        tokens = tokenizer.encode(text)
        if len(tokens) < 2 or len(tokens) > block_size:
            continue

        # Split into context + last word
        # The last word is the final whitespace-separated token
        words = text.rsplit(" ", 1)
        if len(words) < 2:
            continue
        context_text = words[0] + " "
        last_word = words[1]

        context_ids = tokenizer.encode(context_text)
        last_word_ids = tokenizer.encode(last_word)
        if not last_word_ids or len(context_ids) + len(last_word_ids) > block_size:
            continue

        full_ids = context_ids + last_word_ids
        input_tensor = torch.tensor([full_ids], dtype=torch.long, device=device)

        # --- System 2 (AR): predict last word tokens ---
        logits_s2, _ = model.forward_system2(input_tensor)

        # Check if each token of last_word is correctly predicted
        s2_word_correct = True
        word_loss = 0.0
        for j, target_id in enumerate(last_word_ids):
            pos = len(context_ids) - 1 + j  # position predicting this token
            if pos >= logits_s2.size(1):
                s2_word_correct = False
                break
            pred_id = logits_s2[0, pos].argmax().item()
            if pred_id != target_id:
                s2_word_correct = False
            log_prob = F.log_softmax(logits_s2[0, pos], dim=-1)
            word_loss -= log_prob[target_id].item()
            s2_total_tokens += 1

        if s2_word_correct:
            s2_correct += 1
        s2_total_loss += word_loss

        # --- System 1 (diffusion): unmask last word ---
        masked_input = input_tensor.clone()
        mask_positions = torch.zeros_like(input_tensor, dtype=torch.bool)
        for j in range(len(last_word_ids)):
            pos = len(context_ids) + j
            masked_input[0, pos] = mask_token_id
            mask_positions[0, pos] = True

        logits_s1, _, _ = model.forward_system1(masked_input, mask_positions)

        s1_word_correct = True
        for j in range(len(last_word_ids)):
            pos = len(context_ids) + j
            pred_id = logits_s1[0, pos].argmax().item()
            if pred_id != last_word_ids[j]:
                s1_word_correct = False
                break

        if s1_word_correct:
            s1_correct += 1

        total += 1

    results = {
        "s2_accuracy": s2_correct / max(total, 1) * 100,
        "s2_perplexity": math.exp(s2_total_loss / max(s2_total_tokens, 1)),
        "s1_accuracy": s1_correct / max(total, 1) * 100,
    }
    return results


@torch.no_grad()
def eval_wikitext(
    model: DualProcessGPT2,
    tokenizer: GPT2Tokenizer,
    config: dict,
    max_tokens: int = 100_000,
) -> dict[str, float]:
    """Evaluate perplexity on WikiText-103 test set.

    System 2 (AR): standard autoregressive perplexity.
    System 1 (diffusion): average diffusion loss on masked chunks.

    Args:
        model: Dual-process model in eval mode.
        tokenizer: GPT-2 tokenizer.
        config: Full config dict.
        max_tokens: Maximum number of tokens to evaluate on.

    Returns:
        Dict with s2_perplexity and s1_loss.
    """
    device = next(model.parameters()).device
    block_size = config["model"]["block_size"]
    mask_token_id = config["training"]["mask_token_id"]

    dataset = load_dataset("wikitext", "wikitext-103-v1", split="test", trust_remote_code=True)

    # Concatenate all text and tokenize
    all_tokens = []
    for example in dataset:
        text = example["text"]
        if text.strip():
            all_tokens.extend(tokenizer.encode(text))
        if len(all_tokens) >= max_tokens:
            break
    all_tokens = all_tokens[:max_tokens]

    # Chunk into block_size sequences
    chunks = []
    for i in range(0, len(all_tokens) - block_size, block_size):
        chunks.append(all_tokens[i : i + block_size])

    if not chunks:
        return {"s2_perplexity": float("inf"), "s1_loss": float("inf")}

    # --- System 2: AR perplexity ---
    total_ar_loss = 0.0
    total_ar_tokens = 0

    for chunk in chunks:
        input_ids = torch.tensor([chunk], dtype=torch.long, device=device)
        labels = input_ids.clone()
        labels[:, :-1] = input_ids[:, 1:]
        labels[:, -1] = -100
        loss = model.compute_ar_loss(input_ids, labels)
        total_ar_loss += loss.item() * (len(chunk) - 1)
        total_ar_tokens += len(chunk) - 1

    ar_ppl = math.exp(total_ar_loss / max(total_ar_tokens, 1))

    # --- System 1: diffusion loss ---
    total_diff_loss = 0.0
    num_chunks = 0

    for chunk in chunks:
        input_ids = torch.tensor([chunk], dtype=torch.long, device=device)
        # Mask 50% of tokens for consistent evaluation
        mask = torch.rand(1, len(chunk), device=device) < 0.5
        masked_ids = input_ids.clone()
        masked_ids[mask] = mask_token_id
        diff_loss = model.compute_diffusion_loss(input_ids, masked_ids, mask)
        total_diff_loss += diff_loss.item()
        num_chunks += 1

    avg_diff_loss = total_diff_loss / max(num_chunks, 1)

    return {
        "s2_perplexity": ar_ppl,
        "s1_loss": avg_diff_loss,
    }


def print_results(lambada: dict, wikitext: dict, step: str) -> None:
    """Print formatted benchmark results table."""
    print()
    print("\u2554" + "\u2550" * 55 + "\u2557")
    print(f"\u2551{'BENCHMARK RESULTS — step ' + step:^55}\u2551")
    print("\u2560" + "\u2550" * 55 + "\u2563")
    print(f"\u2551{'':55}\u2551")
    print(f"\u2551  {'LAMBADA (last-word prediction)':<53}\u2551")
    print(f"\u2551    {'System 2 (AR) accuracy:':<35}{lambada['s2_accuracy']:>6.1f}%{'':12}\u2551")
    print(f"\u2551    {'System 2 (AR) perplexity:':<35}{lambada['s2_perplexity']:>8.1f}{'':10}\u2551")
    print(f"\u2551    {'System 1 (Diff) accuracy:':<35}{lambada['s1_accuracy']:>6.1f}%{'':12}\u2551")
    print(f"\u2551{'':55}\u2551")
    print(f"\u2551  {'WikiText-103 (perplexity)':<53}\u2551")
    print(f"\u2551    {'System 2 (AR) perplexity:':<35}{wikitext['s2_perplexity']:>8.1f}{'':10}\u2551")
    print(f"\u2551    {'System 1 (Diff) loss:':<35}{wikitext['s1_loss']:>8.3f}{'':10}\u2551")
    print(f"\u2551{'':55}\u2551")
    print("\u255a" + "\u2550" * 55 + "\u255d")
    print()


def log_to_wandb(lambada: dict, wikitext: dict, step: str) -> None:
    """Log benchmark results to W&B if available."""
    try:
        import wandb
        if wandb.run is None:
            wandb.init(project="dual-process-lm", name=f"benchmark-{step}", job_type="eval")
        wandb.summary.update({
            "benchmark/lambada_s2_accuracy": lambada["s2_accuracy"],
            "benchmark/lambada_s2_perplexity": lambada["s2_perplexity"],
            "benchmark/lambada_s1_accuracy": lambada["s1_accuracy"],
            "benchmark/wikitext_s2_perplexity": wikitext["s2_perplexity"],
            "benchmark/wikitext_s1_loss": wikitext["s1_loss"],
        })
        wandb.finish()
        print("Results logged to W&B")
    except Exception as e:
        print(f"W&B logging skipped: {e}")


def main() -> None:
    """CLI entry point for benchmark evaluation."""
    parser = argparse.ArgumentParser(description="Benchmark evaluation (LAMBADA + WikiText-103)")
    parser.add_argument("--config", type=str, required=True, help="Path to YAML config")
    parser.add_argument("--checkpoint", type=str, default=None, help="Path to model checkpoint")
    parser.add_argument("--max_lambada", type=int, default=500, help="Max LAMBADA examples")
    parser.add_argument("--max_wikitext_tokens", type=int, default=100_000, help="Max WikiText tokens")
    parser.add_argument("--no_wandb", action="store_true", help="Disable W&B logging")
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    step = get_step_from_checkpoint(args.checkpoint)
    model = load_model(config, args.checkpoint)
    tokenizer = GPT2Tokenizer.from_pretrained(config["model"]["name"])

    print("Running LAMBADA evaluation...")
    t0 = time.time()
    lambada = eval_lambada(model, tokenizer, config, max_examples=args.max_lambada)
    print(f"  LAMBADA done in {time.time() - t0:.1f}s")

    print("Running WikiText-103 evaluation...")
    t0 = time.time()
    wikitext = eval_wikitext(model, tokenizer, config, max_tokens=args.max_wikitext_tokens)
    print(f"  WikiText-103 done in {time.time() - t0:.1f}s")

    print_results(lambada, wikitext, step)

    # Save results JSON and upload to S3
    try:
        benchmarks_dir = DATA_DIR / "benchmarks"
        benchmarks_dir.mkdir(parents=True, exist_ok=True)
        results_path = benchmarks_dir / f"benchmark_step_{step}_{int(time.time())}.json"
        results = {
            "step": step,
            "timestamp": time.time(),
            "lambada": lambada,
            "wikitext": wikitext,
        }
        results_path.write_text(json.dumps(results, indent=2))
        upload_benchmark_results(results_path)
        print(f"Benchmark results saved: {results_path}")
    except Exception as e:
        print(f"Failed to save benchmark results: {e}")

    if not args.no_wandb:
        log_to_wandb(lambada, wikitext, step)


if __name__ == "__main__":
    main()
