"""Tests for scripts/benchmark.py — runs on random-init model with small data."""

import torch
import yaml
import pytest

from src.model.dual_process_gpt2 import DualProcessGPT2
from transformers import GPT2Tokenizer


@pytest.fixture
def config():
    with open("configs/tiny.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture
def model(config):
    model = DualProcessGPT2(config, pretrained=False)
    model.eval()
    return model


@pytest.fixture
def tokenizer():
    return GPT2Tokenizer.from_pretrained("gpt2")


class TestBenchmarkLoadModel:
    def test_load_pretrained(self, config):
        from scripts.benchmark import load_model
        model = load_model(config, checkpoint_path=None)
        assert model is not None
        assert not model.training

    def test_load_random_init(self, config):
        """Verify we can create a model without a checkpoint."""
        model = DualProcessGPT2(config, pretrained=False)
        model.eval()
        assert model is not None


class TestLambdaEval:
    def test_runs_and_returns_metrics(self, model, tokenizer, config):
        from scripts.benchmark import eval_lambada
        results = eval_lambada(model, tokenizer, config, max_examples=5)
        assert "s2_accuracy" in results
        assert "s2_perplexity" in results
        assert "s1_accuracy" in results
        assert 0 <= results["s2_accuracy"] <= 100
        assert 0 <= results["s1_accuracy"] <= 100
        assert results["s2_perplexity"] > 0

    def test_zero_examples(self, model, tokenizer, config):
        from scripts.benchmark import eval_lambada
        results = eval_lambada(model, tokenizer, config, max_examples=0)
        assert results["s2_accuracy"] == 0.0
        assert results["s1_accuracy"] == 0.0


class TestWikitextEval:
    def test_runs_and_returns_metrics(self, model, tokenizer, config):
        from scripts.benchmark import eval_wikitext
        results = eval_wikitext(model, tokenizer, config, max_tokens=2048)
        assert "s2_perplexity" in results
        assert "s1_loss" in results
        assert results["s2_perplexity"] > 0
        assert results["s1_loss"] > 0


class TestPrintResults:
    def test_print_does_not_crash(self, capsys):
        from scripts.benchmark import print_results
        lambada = {"s2_accuracy": 12.5, "s2_perplexity": 45.2, "s1_accuracy": 8.3}
        wikitext = {"s2_perplexity": 30.1, "s1_loss": 5.432}
        print_results(lambada, wikitext, "1000")
        captured = capsys.readouterr()
        assert "BENCHMARK RESULTS" in captured.out
        assert "12.5" in captured.out
