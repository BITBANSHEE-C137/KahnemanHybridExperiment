"""Lean tokenizer: reads cached parquet files one at a time to avoid OOM.

Processes each parquet shard independently, tokenizes, and appends to the
output binary. Uses pyarrow for parquet reading (already installed with HF).
Peak memory usage: ~1 parquet shard (~500MB) + tokenizer.
"""

import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
from transformers import GPT2Tokenizer

EVAL_DOCS = 5000
S3_BUCKET = "ml-lab-004507070771"
S3_PREFIX = "dual-system-research-data/preprocessed"

CACHE_DIR = os.environ.get("HF_HOME", "/opt/dlami/nvme/ml-lab/hf_cache")
OUTPUT_DIR = os.environ.get("PREPROCESSED_DATA_DIR", "/opt/dlami/nvme/ml-lab/preprocessed")

# Find parquet files
parquet_dir = Path(CACHE_DIR) / "hub/datasets--openwebtext/snapshots"
snapshot_dirs = list(parquet_dir.iterdir())
if not snapshot_dirs:
    print("ERROR: No cached parquet files found")
    sys.exit(1)

parquet_files = sorted((snapshot_dirs[0] / "plain_text").glob("train-*.parquet"))
print(f"Found {len(parquet_files)} parquet shards")

output_path = Path(OUTPUT_DIR)
output_path.mkdir(parents=True, exist_ok=True)

train_path = output_path / "openwebtext_train.bin"
eval_path = output_path / "openwebtext_eval.bin"
meta_path = output_path / "openwebtext_meta.json"

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
eos_id = tokenizer.eos_token_id

# Check for partial progress (resume from where we left off)
start_shard = 0
train_tokens = 0
total_docs = 0

progress_path = output_path / ".progress.json"
if progress_path.exists():
    progress = json.loads(progress_path.read_text())
    start_shard = progress["next_shard"]
    train_tokens = progress["train_tokens"]
    total_docs = progress["total_docs"]
    print(f"[resume] Resuming from shard {start_shard}, {total_docs:,} docs, {train_tokens:,} tokens")
    write_mode = "ab"
else:
    write_mode = "wb"

t0 = time.time()

# Process one shard at a time
with open(train_path, write_mode) as f_train:
    for shard_idx, pf in enumerate(parquet_files):
        if shard_idx < start_shard:
            continue

        table = pq.read_table(pf, columns=["text"])
        texts = table.column("text").to_pylist()
        del table  # free memory immediately

        shard_tokens = 0
        for text in texts:
            tokens = tokenizer.encode(text)
            tokens.append(eos_id)
            f_train.write(np.array(tokens, dtype=np.uint16).tobytes())
            shard_tokens += len(tokens)
            total_docs += 1

        train_tokens += shard_tokens
        del texts

        elapsed = time.time() - t0
        print(
            f"  shard {shard_idx + 1}/{len(parquet_files)} | "
            f"{total_docs:>10,} docs | "
            f"{train_tokens:>13,} train tokens | "
            f"{elapsed:.0f}s elapsed"
        )
        sys.stdout.flush()

        # Save progress after each shard
        progress_path.write_text(json.dumps({
            "next_shard": shard_idx + 1,
            "train_tokens": train_tokens,
            "total_docs": total_docs,
        }))

print(f"\nTotal: {total_docs:,} docs, {train_tokens:,} tokens")
print(f"Train file: {train_path} ({train_path.stat().st_size / (1024**3):.2f} GB)")

# Write eval split from last EVAL_DOCS of the final shard data
# Re-read the last shard to get eval docs
print(f"\nWriting eval split ({EVAL_DOCS} docs from last shard)...")
last_table = pq.read_table(parquet_files[-1], columns=["text"])
last_texts = last_table.column("text").to_pylist()
del last_table

eval_texts = last_texts[-EVAL_DOCS:]
eval_tokens = 0
with open(eval_path, "wb") as f_eval:
    for text in eval_texts:
        tokens = tokenizer.encode(text)
        tokens.append(eos_id)
        f_eval.write(np.array(tokens, dtype=np.uint16).tobytes())
        eval_tokens += len(tokens)
del last_texts, eval_texts

print(f"Eval file: {eval_path} ({eval_path.stat().st_size / (1024**3):.4f} GB)")

# Metadata
elapsed = time.time() - t0
meta = {
    "total_docs": total_docs,
    "train_docs": total_docs,
    "eval_docs": EVAL_DOCS,
    "train_tokens": train_tokens,
    "eval_tokens": eval_tokens,
    "dtype": "uint16",
    "tokenizer": "gpt2",
    "vocab_size": tokenizer.vocab_size,
    "elapsed_seconds": round(elapsed, 1),
}
meta_path.write_text(json.dumps(meta, indent=2))
print(f"\nMetadata: {meta_path}")
print(f"Total time: {elapsed:.0f}s")

# Clean up progress file
progress_path.unlink(missing_ok=True)

# Upload to S3
print("\nUploading to S3...")
import subprocess
s3_dest = f"s3://{S3_BUCKET}/{S3_PREFIX}/"
subprocess.run(
    ["aws", "s3", "sync", str(output_path), s3_dest,
     "--region", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
     "--exclude", "*", "--include", "*.bin", "--include", "*.json"],
    check=True,
)
print("Upload complete.")
