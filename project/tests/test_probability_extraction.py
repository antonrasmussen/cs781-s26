"""Tests for mock class-code probability extraction."""

import math

from reliability_eval.inference.score_class_codes import mock_score_example


def test_mock_score_probabilities_sum_to_one():
    """Mock scorer returns a normalized probability distribution."""
    result = mock_score_example(
        prompt="Classify sentence.",
        task="pubmed_rct",
        example_id="ex1",
        true_label="METHODS",
    )
    probs = result["probabilities"]
    assert set(probs.keys()) == {"A", "B", "C", "D", "E"}
    assert math.isclose(sum(probs.values()), 1.0, rel_tol=1e-9, abs_tol=1e-9)
    assert result["predicted_code"] in probs
    assert 0.0 <= result["confidence"] <= 1.0
