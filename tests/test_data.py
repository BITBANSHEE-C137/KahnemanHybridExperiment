"""Tests for MemmapTokenDataset and preprocessed data path logic."""

import json
import tempfile
from pathlib import Path

import numpy as np
import pytest
import torch

from src.data.openwebtext import MemmapTokenDataset, _preprocessed_available


@pytest.fixture
def sample_bin(tmp_path: Path) -> Path:
    """Create a sample uint16 binary file with known token values."""
    # 10240 tokens = exactly 10 chunks of 1024
    tokens = np.arange(10240, dtype=np.uint16)
    bin_path = tmp_path / "openwebtext_train.bin"
    tokens.tofile(bin_path)
    return bin_path


@pytest.fixture
def odd_bin(tmp_path: Path) -> Path:
    """Create a binary file with tokens that don't divide evenly into chunks."""
    # 10500 tokens = 10 full chunks of 1024 + 260 remainder
    tokens = np.arange(10500, dtype=np.uint16)
    bin_path = tmp_path / "openwebtext_train.bin"
    tokens.tofile(bin_path)
    return bin_path


class TestMemmapTokenDataset:
    def test_correct_chunk_count(self, sample_bin: Path) -> None:
        """Dataset with 10240 tokens / 1024 chunk size = exactly 10 chunks."""
        ds = MemmapTokenDataset(sample_bin, max_length=1024)
        assert len(ds) == 10

    def test_remainder_tokens_dropped(self, odd_bin: Path) -> None:
        """10500 tokens / 1024 = 10 full chunks, 260 remainder dropped."""
        ds = MemmapTokenDataset(odd_bin, max_length=1024)
        assert len(ds) == 10

    def test_returns_long_tensors(self, sample_bin: Path) -> None:
        """Each sample should be a torch.long tensor."""
        ds = MemmapTokenDataset(sample_bin, max_length=1024)
        sample = ds[0]
        assert isinstance(sample, torch.Tensor)
        assert sample.dtype == torch.long

    def test_correct_shape(self, sample_bin: Path) -> None:
        """Each sample should have shape (max_length,)."""
        ds = MemmapTokenDataset(sample_bin, max_length=1024)
        sample = ds[0]
        assert sample.shape == (1024,)

    def test_values_preserved(self, sample_bin: Path) -> None:
        """Token values should survive uint16 -> int64 conversion."""
        ds = MemmapTokenDataset(sample_bin, max_length=1024)
        # First chunk should be [0, 1, 2, ..., 1023]
        first = ds[0]
        expected = torch.arange(1024, dtype=torch.long)
        assert torch.equal(first, expected)
        # Second chunk should be [1024, 1025, ..., 2047]
        second = ds[1]
        expected2 = torch.arange(1024, 2048, dtype=torch.long)
        assert torch.equal(second, expected2)

    def test_max_chunks_cap(self, sample_bin: Path) -> None:
        """max_chunks should limit the number of chunks returned."""
        ds = MemmapTokenDataset(sample_bin, max_length=1024, max_chunks=3)
        assert len(ds) == 3
        # Should still return valid data
        sample = ds[2]
        assert sample.shape == (1024,)

    def test_max_chunks_larger_than_available(self, sample_bin: Path) -> None:
        """max_chunks larger than available chunks should not error."""
        ds = MemmapTokenDataset(sample_bin, max_length=1024, max_chunks=999)
        assert len(ds) == 10  # only 10 chunks available

    def test_small_chunk_size(self, sample_bin: Path) -> None:
        """Smaller chunk size should produce more chunks."""
        ds = MemmapTokenDataset(sample_bin, max_length=128)
        assert len(ds) == 80  # 10240 / 128 = 80

    def test_gpt2_vocab_range(self, tmp_path: Path) -> None:
        """Values up to 50256 (GPT-2 vocab) should be preserved correctly."""
        tokens = np.array([0, 50256, 50257, 65535], dtype=np.uint16)
        # Pad to at least max_length
        padded = np.zeros(1024, dtype=np.uint16)
        padded[: len(tokens)] = tokens
        bin_path = tmp_path / "vocab_test.bin"
        padded.tofile(bin_path)

        ds = MemmapTokenDataset(bin_path, max_length=1024)
        sample = ds[0]
        assert sample[0].item() == 0
        assert sample[1].item() == 50256
        assert sample[2].item() == 50257
        assert sample[3].item() == 65535


class TestPreprocessedAvailable:
    def test_returns_path_when_exists(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return path when bin file exists and is non-empty."""
        monkeypatch.setattr("src.data.openwebtext.PREPROCESSED_DATA_DIR", str(tmp_path))
        bin_file = tmp_path / "openwebtext_train.bin"
        bin_file.write_bytes(b"\x00" * 100)
        result = _preprocessed_available("train")
        assert result == bin_file

    def test_returns_none_when_missing(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return None when bin file doesn't exist."""
        monkeypatch.setattr("src.data.openwebtext.PREPROCESSED_DATA_DIR", str(tmp_path))
        result = _preprocessed_available("train")
        assert result is None

    def test_returns_none_when_empty(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should return None when bin file exists but is empty."""
        monkeypatch.setattr("src.data.openwebtext.PREPROCESSED_DATA_DIR", str(tmp_path))
        bin_file = tmp_path / "openwebtext_train.bin"
        bin_file.write_bytes(b"")
        result = _preprocessed_available("train")
        assert result is None

    def test_eval_split(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Should look for openwebtext_eval.bin for eval split."""
        monkeypatch.setattr("src.data.openwebtext.PREPROCESSED_DATA_DIR", str(tmp_path))
        bin_file = tmp_path / "openwebtext_eval.bin"
        bin_file.write_bytes(b"\x00" * 100)
        result = _preprocessed_available("eval")
        assert result == bin_file
