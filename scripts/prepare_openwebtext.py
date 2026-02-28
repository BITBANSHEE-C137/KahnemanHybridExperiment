"""Pre-tokenize OpenWebText into uint16 binary files for fast training.

Streams from HuggingFace (no disk needed for raw data), tokenizes with GPT-2
tokenizer, writes flat uint16 binary files. GPT-2 vocab size (50257) fits in
uint16 (max 65535).

Output layout:
    openwebtext_train.bin   (~16 GB, uint16)
    openwebtext_eval.bin    (~10 MB, uint16, last 5000 docs)
    openwebtext_meta.json   (token counts, split info)

Usage:
    python -m scripts.prepare_openwebtext --output_dir /tmp/preprocessed
    python -m scripts.prepare_openwebtext --output_dir /tmp/preprocessed --upload_s3
"""

import argparse
import json
import subprocess
import time
from pathlib import Path

import numpy as np
from datasets import load_dataset
from transformers import GPT2Tokenizer


EVAL_DOCS = 5000
S3_BUCKET = "ml-lab-004507070771"
S3_PREFIX = "dual-system-research-data/preprocessed"


def tokenize_and_write(output_dir: str) -> dict:
    """Stream OpenWebText, tokenize, and write train/eval binary files.

    Two-pass approach to avoid loading entire dataset into memory:
      Pass 1: Stream and write all docs to train file, buffer last EVAL_DOCS
      Pass 2: Write eval docs from buffer

    Args:
        output_dir: Directory to write .bin and .json files.

    Returns:
        Metadata dict with token counts and split info.
    """
    from collections import deque

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    eos_id = tokenizer.eos_token_id

    train_path = output_path / "openwebtext_train.bin"
    eval_path = output_path / "openwebtext_eval.bin"
    meta_path = output_path / "openwebtext_meta.json"

    print("Loading OpenWebText from HuggingFace (streaming mode)...")
    dataset = load_dataset("openwebtext", split="train", streaming=True)

    train_tokens = 0
    eval_tokens = 0
    docs_processed = 0
    t0 = time.time()

    # Keep a rolling buffer of the last EVAL_DOCS tokenized documents
    eval_buffer = deque(maxlen=EVAL_DOCS)

    print(f"\nWriting train split (streaming)...")
    print(f"  Train: {train_path}")
    with open(train_path, "wb") as f_train:
        for example in dataset:
            tokens = tokenizer.encode(example["text"])
            tokens.append(eos_id)
            token_bytes = np.array(tokens, dtype=np.uint16).tobytes()

            f_train.write(token_bytes)
            train_tokens += len(tokens)
            docs_processed += 1

            # Buffer for eval split
            eval_buffer.append(token_bytes)

            if docs_processed % 100_000 == 0:
                elapsed = time.time() - t0
                docs_per_sec = docs_processed / elapsed
                print(
                    f"  {docs_processed:>10,} docs | "
                    f"{train_tokens:>13,} train tokens | "
                    f"{docs_per_sec:,.0f} docs/sec | "
                    f"{elapsed:.0f}s elapsed"
                )

    total_docs = docs_processed
    print(f"\nTotal documents streamed: {total_docs:,}")
    print(f"Train split: {train_tokens:,} tokens")

    # Write eval split from buffer
    print(f"\nWriting eval split ({len(eval_buffer)} docs)...")
    print(f"  Eval: {eval_path}")
    with open(eval_path, "wb") as f_eval:
        for token_bytes in eval_buffer:
            eval_tokens += len(token_bytes) // 2  # uint16 = 2 bytes per token
            f_eval.write(token_bytes)

    print(f"Eval split: {eval_tokens:,} tokens")

    elapsed = time.time() - t0
    meta = {
        "total_docs": total_docs,
        "train_docs": total_docs,
        "eval_docs": len(eval_buffer),
        "train_tokens": train_tokens,
        "eval_tokens": eval_tokens,
        "dtype": "uint16",
        "tokenizer": "gpt2",
        "vocab_size": tokenizer.vocab_size,
        "elapsed_seconds": round(elapsed, 1),
    }

    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"\nMetadata written to {meta_path}")
    print(f"Total time: {elapsed:.0f}s")

    # Print file sizes
    for p in [train_path, eval_path]:
        size_gb = p.stat().st_size / (1024**3)
        print(f"  {p.name}: {size_gb:.2f} GB")

    return meta


def upload_to_s3(output_dir: str, region: str = "us-east-1") -> None:
    """Upload preprocessed files to S3.

    Args:
        output_dir: Directory containing .bin and .json files.
        region: AWS region for S3 bucket.
    """
    s3_dest = f"s3://{S3_BUCKET}/{S3_PREFIX}/"
    print(f"\nUploading to {s3_dest}...")

    cmd = [
        "aws", "s3", "sync",
        output_dir, s3_dest,
        "--region", region,
        "--exclude", "*",
        "--include", "*.bin",
        "--include", "*.json",
    ]
    subprocess.run(cmd, check=True)
    print("Upload complete.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pre-tokenize OpenWebText into uint16 binary files."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="/tmp/preprocessed",
        help="Directory to write output files.",
    )
    parser.add_argument(
        "--upload_s3",
        action="store_true",
        help="Upload results to S3 after processing.",
    )
    parser.add_argument(
        "--region",
        type=str,
        default="us-east-1",
        help="AWS region for S3 upload.",
    )
    args = parser.parse_args()

    meta = tokenize_and_write(args.output_dir)

    if args.upload_s3:
        upload_to_s3(args.output_dir, args.region)

    print("\nDone!")
    print(f"  Train: {meta['train_tokens']:,} tokens ({meta['train_docs']:,} docs)")
    print(f"  Eval:  {meta['eval_tokens']:,} tokens ({meta['eval_docs']:,} docs)")


if __name__ == "__main__":
    main()
