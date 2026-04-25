"""Offline tests for PubMed RCT loader (no Hugging Face network)."""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

from reliability_eval.data import pubmed_rct


def _tiny_path() -> Path:
    return Path(pubmed_rct.__file__).resolve().parents[3] / "data" / "samples" / "pubmed_rct_tiny.jsonl"


def test_normalize_record_uses_abstract_sentence_ids():
    from reliability_eval.data.pubmed_rct import _normalize_record

    ex = _normalize_record(
        {
            "abstract_id": 24845963,
            "sentence_id": 0,
            "text": "Hello world.",
            "label": "background",
        },
        idx=99,
    )
    assert ex["example_id"] == "24845963_0"
    assert ex["label"] == "BACKGROUND"


def test_load_pubmed_rct_from_local_jsonl():
    examples = pubmed_rct.load_pubmed_rct(path_or_hf_id=str(_tiny_path()), split="test")
    assert len(examples) == 8
    labels = {ex["label"] for ex in examples}
    assert labels == {
        "BACKGROUND",
        "OBJECTIVE",
        "METHODS",
        "RESULTS",
        "CONCLUSIONS",
    }


def test_read_hf_split_int_labels(monkeypatch):
    """Simulate HF row with integer label index."""
    fake_rows = [
        {"sentence": "S0", "label": 0, "example_id": "h0"},
        {"sentence": "S4", "label": 4, "example_id": "h4"},
    ]

    class _FakeDS:
        def __iter__(self):
            return iter(fake_rows)

    def fake_load_dataset(*_a, **_k):
        return _FakeDS()

    fake_mod = types.ModuleType("datasets")
    fake_mod.load_dataset = fake_load_dataset
    monkeypatch.setitem(sys.modules, "datasets", fake_mod)

    examples = pubmed_rct._read_hf_split("dummy/id", split="train")
    assert len(examples) == 2
    assert examples[0]["label"] == "BACKGROUND"
    assert examples[0]["text"] == "S0"
    assert examples[1]["label"] == "CONCLUSIONS"


def test_read_hf_split_label_text(monkeypatch):
    fake_rows = [
        {"text": "T1", "label_text": "RESULTS", "example_id": "x1"},
        {"text": "T2", "label_text": "OBJECTIVES", "example_id": "x2"},
    ]

    class _FakeDS:
        def __iter__(self):
            return iter(fake_rows)

    def fake_load_dataset(*_a, **_k):
        return _FakeDS()

    fake_mod = types.ModuleType("datasets")
    fake_mod.load_dataset = fake_load_dataset
    monkeypatch.setitem(sys.modules, "datasets", fake_mod)

    examples = pubmed_rct._read_hf_split("dummy/id", split="test")
    assert examples[0]["label"] == "RESULTS"
    assert examples[1]["label"] == "OBJECTIVE"
