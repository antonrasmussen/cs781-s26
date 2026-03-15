"""Tests for config loading and sweep expansion.

TODO: Load base + dataset + precision; merge; expand_sweep returns list of configs.
"""
from pathlib import Path


def test_base_config_loadable():
    """Base config file exists and contains expected seed key."""
    path = Path(__file__).resolve().parent.parent / "configs" / "base.yaml"
    text = path.read_text(encoding="utf-8")
    assert "seed:" in text
    assert "42" in text
