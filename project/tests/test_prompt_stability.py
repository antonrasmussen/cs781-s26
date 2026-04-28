"""Tests for Fleiss' kappa (prompt templates as raters)."""

import pytest

from reliability_eval.metrics.prompt_stability import fleiss_kappa, fleiss_kappa_bootstrap_ci


def test_fleiss_kappa_perfect_agreement():
    # Two templates, two subjects, labels A and B; full agreement
    predictions = [["A", "B"], ["A", "B"]]
    k = fleiss_kappa(predictions)
    assert k == pytest.approx(1.0)


def test_fleiss_kappa_full_disagreement_two_templates():
    predictions = [["A", "B"], ["B", "A"]]
    k = fleiss_kappa(predictions)
    assert k == pytest.approx(-1.0)


def test_fleiss_kappa_requires_two_raters():
    with pytest.raises(ValueError, match="at least two raters"):
        fleiss_kappa([["A", "B"]])


def test_fleiss_kappa_requires_two_categories():
    with pytest.raises(ValueError, match="at least two distinct"):
        fleiss_kappa([["A", "A"], ["A", "A"]])


def test_fleiss_kappa_row_length_mismatch():
    with pytest.raises(ValueError, match="equal length"):
        fleiss_kappa([["A"], ["A", "B"]])


def test_fleiss_kappa_empty_templates():
    with pytest.raises(ValueError, match="non-empty"):
        fleiss_kappa([])


def test_fleiss_kappa_bootstrap_ci_contains_point():
    predictions = [["A", "B", "A", "B"], ["A", "B", "A", "B"], ["A", "B", "A", "B"]]
    out = fleiss_kappa_bootstrap_ci(predictions, n_resamples=200, seed=42)
    assert out["ci_low"] <= out["point"] <= out["ci_high"]
