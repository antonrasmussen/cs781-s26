"""Tests for calibration metrics guards."""

import pytest

from reliability_eval.metrics.calibration import (
    expected_calibration_error,
    expected_calibration_error_from_confidence,
    reliability_bins,
)


def test_reliability_bins_rejects_out_of_range_confidence():
    with pytest.raises(ValueError, match="\\[0\\.0, 1\\.0\\]"):
        reliability_bins([0.5, 1.5], [1, 0], n_bins=5)


def test_expected_calibration_error_rejects_length_mismatch():
    """Guards against unequal sequence lengths before pairing labels."""
    with pytest.raises(ValueError, match="Input length mismatch"):
        expected_calibration_error(
            y_true=["A", "B"],
            y_pred=["A"],
            confidences=[0.5, 0.6],
        )


def test_expected_calibration_error_from_confidence_validates_range():
    with pytest.raises(ValueError, match="\\[0\\.0, 1\\.0\\]"):
        expected_calibration_error_from_confidence(
            confidences=[0.2, -0.1],
            correctness=[1, 0],
            n_bins=5,
        )
