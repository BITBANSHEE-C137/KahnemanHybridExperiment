"""Data loading for OpenWebText via HuggingFace datasets.

Tokenizes and chunks text into fixed-length sequences for training.
"""

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import GPT2Tokenizer
from datasets import load_dataset
from typing import Optional


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
            raw = load_dataset("openwebtext", split=f"{split}[:{max_samples}]", trust_remote_code=True)
        else:
            raw = load_dataset("openwebtext", split=split, trust_remote_code=True)

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

    Args:
        config: Full configuration dictionary.
        smoke_test: If True, load a small subset for quick testing.

    Returns:
        DataLoader yielding batches of token ID tensors.
    """
    data_cfg = config["data"]
    train_cfg = config["smoke_test"] if smoke_test else config["training"]

    max_samples = 1000 if smoke_test else None

    dataset = OpenWebTextDataset(
        max_length=data_cfg.get("max_length", 1024),
        split="train",
        max_samples=max_samples,
    )

    return DataLoader(
        dataset,
        batch_size=train_cfg["batch_size"],
        shuffle=True,
        num_workers=data_cfg.get("num_workers", 4),
        pin_memory=True,
        drop_last=True,
    )
