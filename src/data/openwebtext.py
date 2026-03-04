"""Data loading for OpenWebText.

Supports two backends:
1. Pre-processed uint16 binary files (fast, zero-copy via numpy memmap)
2. HuggingFace datasets streaming fallback (slow, used for smoke tests)

The binary format is produced by scripts/prepare_openwebtext.py.
"""

import os
import random
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import GPT2Tokenizer
from datasets import load_dataset
from typing import Optional

PREPROCESSED_DATA_DIR = os.environ.get(
    "PREPROCESSED_DATA_DIR", "/opt/dlami/nvme/ml-lab/preprocessed"
)


def _preprocessed_available(split: str = "train") -> Optional[Path]:
    """Check if preprocessed binary file exists for the given split.

    Args:
        split: "train" or "eval".

    Returns:
        Path to the .bin file if it exists, None otherwise.
    """
    filename = f"openwebtext_{split}.bin"
    path = Path(PREPROCESSED_DATA_DIR) / filename
    if path.exists() and path.stat().st_size > 0:
        return path
    return None


class MemmapTokenDataset(Dataset):
    """Dataset backed by a pre-tokenized uint16 binary file.

    Uses numpy memmap for zero-copy, lazy-loading access. The binary file
    is a flat array of uint16 token IDs produced by prepare_openwebtext.py.

    Args:
        bin_path: Path to the .bin file (uint16 flat array).
        max_length: Tokens per sample (chunk size).
        max_chunks: Optional cap on number of chunks.
    """

    def __init__(
        self,
        bin_path: str | Path,
        max_length: int = 1024,
        max_chunks: Optional[int] = None,
    ) -> None:
        self.max_length = max_length
        self.data = np.memmap(bin_path, dtype=np.uint16, mode="r")
        self.num_chunks = len(self.data) // max_length
        if max_chunks is not None:
            self.num_chunks = min(self.num_chunks, max_chunks)
        print(
            f"[data] Using pre-processed binary: {bin_path} "
            f"({len(self.data):,} tokens, {self.num_chunks:,} chunks)"
        )

    def __len__(self) -> int:
        return self.num_chunks

    def __getitem__(self, idx: int) -> torch.Tensor:
        start = idx * self.max_length
        end = start + self.max_length
        chunk = self.data[start:end].astype(np.int64)
        return torch.from_numpy(chunk)


class OpenWebTextDataset(Dataset):
    """Tokenized, chunked OpenWebText dataset.

    Loads OpenWebText from HuggingFace, tokenizes with GPT-2 tokenizer,
    and chunks into fixed-length sequences.

    Args:
        max_length: Maximum sequence length (tokens per sample).
        split: Dataset split to load.
        max_samples: Optional cap on number of raw documents to load.
    """

    def __init__(
        self,
        max_length: int = 1024,
        split: str = "train",
        max_samples: Optional[int] = None,
    ) -> None:
        self.max_length = max_length
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

        # Load dataset
        if max_samples is not None:
            raw = load_dataset("openwebtext", split=f"{split}[:{max_samples}]")
        else:
            raw = load_dataset("openwebtext", split=split)

        # Tokenize and concatenate all texts into one long token stream,
        # then chunk into max_length sequences
        self.chunks = self._tokenize_and_chunk(raw)

    def _tokenize_and_chunk(self, raw_dataset) -> list[list[int]]:
        """Tokenize all documents and chunk into fixed-length sequences.

        Args:
            raw_dataset: HuggingFace dataset with 'text' field.

        Returns:
            List of token ID lists, each of length max_length.
        """
        all_tokens: list[int] = []

        for example in raw_dataset:
            tokens = self.tokenizer.encode(example["text"])
            all_tokens.extend(tokens)
            all_tokens.append(self.tokenizer.eos_token_id)

        # Chunk into fixed-length sequences
        chunks = []
        for i in range(0, len(all_tokens) - self.max_length, self.max_length):
            chunks.append(all_tokens[i : i + self.max_length])

        return chunks

    def __len__(self) -> int:
        return len(self.chunks)

    def __getitem__(self, idx: int) -> torch.Tensor:
        return torch.tensor(self.chunks[idx], dtype=torch.long)


def create_dataloader(config: dict, smoke_test: bool = False) -> DataLoader:
    """Create a DataLoader from config.

    Uses pre-processed binary if available, otherwise falls back to
    HuggingFace streaming. Smoke tests always use HuggingFace fallback
    (no S3 dependency).

    Args:
        config: Full configuration dictionary.
        smoke_test: If True, load a small subset for quick testing.

    Returns:
        DataLoader yielding batches of token ID tensors.
    """
    data_cfg = config["data"]
    train_cfg = config["smoke_test"] if smoke_test else config["training"]
    max_length = data_cfg.get("max_length", 1024)
    seed = config.get("seed", config.get("training", {}).get("seed", 42))

    bin_path = _preprocessed_available("train")
    if bin_path is not None and not smoke_test:
        dataset = MemmapTokenDataset(
            bin_path=bin_path,
            max_length=max_length,
        )
    else:
        max_samples = 1000 if smoke_test else None
        dataset = OpenWebTextDataset(
            max_length=max_length,
            split="train",
            max_samples=max_samples,
        )

    generator = torch.Generator()
    generator.manual_seed(seed)

    def worker_init_fn(worker_id: int) -> None:
        worker_seed = seed + worker_id
        np.random.seed(worker_seed)
        random.seed(worker_seed)

    return DataLoader(
        dataset,
        batch_size=train_cfg["batch_size"],
        shuffle=True,
        num_workers=data_cfg.get("num_workers", 4),
        pin_memory=True,
        drop_last=True,
        generator=generator,
        worker_init_fn=worker_init_fn,
    )


def create_eval_dataloader(config: dict, smoke_test: bool = False) -> DataLoader:
    """Create a DataLoader for evaluation.

    NOTE: The pre-processed eval binary (openwebtext_eval.bin) overlaps with
    the training data. lean_preprocess.py writes all docs to the train file,
    then extracts the last 5000 docs of the final shard into the eval file.
    Eval therefore tracks memorization/learning, not generalization.

    Uses pre-processed eval binary if available, otherwise falls back to
    HuggingFace (last N documents of OpenWebText). Smoke tests always use
    HuggingFace fallback.

    Args:
        config: Full configuration dictionary.
        smoke_test: If True, use a smaller eval set.

    Returns:
        DataLoader yielding batches of token ID tensors.
    """
    data_cfg = config["data"]
    train_cfg = config["smoke_test"] if smoke_test else config["training"]
    max_length = data_cfg.get("max_length", 1024)
    seed = config.get("seed", config.get("training", {}).get("seed", 42))

    bin_path = _preprocessed_available("eval")
    if bin_path is not None and not smoke_test:
        dataset = MemmapTokenDataset(
            bin_path=bin_path,
            max_length=max_length,
        )
    else:
        eval_samples = 500 if smoke_test else 5000
        dataset = OpenWebTextDataset(
            max_length=max_length,
            split=f"train[-{eval_samples}:]",
            max_samples=None,
        )

    generator = torch.Generator()
    generator.manual_seed(seed)

    def worker_init_fn(worker_id: int) -> None:
        worker_seed = seed + worker_id
        np.random.seed(worker_seed)
        random.seed(worker_seed)

    return DataLoader(
        dataset,
        batch_size=train_cfg["batch_size"],
        shuffle=False,
        num_workers=data_cfg.get("num_workers", 4),
        pin_memory=True,
        drop_last=True,
        generator=generator,
        worker_init_fn=worker_init_fn,
    )
