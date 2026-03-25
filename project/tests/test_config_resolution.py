"""Tests for config loading and sweep expansion.

TODO: Load base + dataset + precision; merge; expand_sweep returns list of configs.
"""
import warnings
from pathlib import Path

import pytest


def test_base_config_loadable():
    """Base config file exists and contains expected seed key."""
    path = Path(__file__).resolve().parent.parent / "configs" / "base.yaml"
    text = path.read_text(encoding="utf-8")
    assert "seed:" in text
    assert "42" in text


def test_resolve_config_raises_on_missing_execution_profile():
    from reliability_eval.config.resolve import resolve_config

    project_root = Path(__file__).resolve().parent.parent
    with pytest.raises(FileNotFoundError, match="not_a_real_profile"):
        resolve_config(project_root, execution_profile="not_a_real_profile")


def test_load_yaml_non_mapping_root_returns_empty(tmp_path):
    from reliability_eval.config.resolve import _load_yaml

    p = tmp_path / "bad.yaml"
    p.write_text("[1, 2, 3]\n", encoding="utf-8")
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        out = _load_yaml(p)
    assert out == {}
    assert len(rec) >= 1


def test_combination_values_wraps_scalar_string():
    from reliability_eval.experiments.run_grid import _combination_values

    assert _combination_values("dataset", "pubmed_rct") == ["pubmed_rct"]
