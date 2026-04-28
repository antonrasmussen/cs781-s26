import pytest

from reliability_eval.metrics.ace import adaptive_calibration_error


def test_ace_zero_for_perfectly_calibrated_binary_points():
    confidences = [1.0, 0.0, 1.0, 0.0]
    correctness = [1, 0, 1, 0]
    ace = adaptive_calibration_error(confidences=confidences, correctness=correctness, n_bins=2)
    assert ace == pytest.approx(0.0)


def test_ace_positive_for_miscalibration():
    confidences = [0.9, 0.8, 0.7, 0.6]
    correctness = [0, 0, 0, 0]
    ace = adaptive_calibration_error(confidences=confidences, correctness=correctness, n_bins=2)
    assert ace > 0.0
