"""Tests for apply_calibration dispatch and temperature scaling."""

import math

import pytest

from reliability_eval.calibration.apply import apply_calibration
from reliability_eval.calibration.temperature_scaling import fit_temperature
from reliability_eval.metrics.calibration import expected_calibration_error_from_confidence


def test_apply_none_returns_copy():
    probs = [{"A": 0.7, "B": 0.3}]
    out = apply_calibration(probs, None)
    assert out == probs
    assert out is not probs
    assert out[0] is not probs[0]


def test_apply_none_string():
    probs = [{"A": 1.0}]
    out = apply_calibration(probs, "none")
    assert out[0] == {"A": 1.0}


def test_apply_temperature_scaling():
    probs = [{"A": 0.5, "B": 0.5}]
    out = apply_calibration(
        probs,
        "temperature_scaling",
        calibrator_params={"temperature": 2.0},
    )
    assert len(out) == 1
    assert math.isclose(sum(out[0].values()), 1.0)
    assert set(out[0]) == {"A", "B"}


def test_apply_temperature_scaling_requires_temperature():
    with pytest.raises(ValueError, match="temperature"):
        apply_calibration([{"A": 1.0}], "temperature_scaling", calibrator_params={})


def test_apply_isotonic_identity():
    probs = [{"A": 0.2, "B": 0.8}]
    out = apply_calibration(
        probs,
        "isotonic",
        calibrator_params={"transform": lambda x: x},
    )
    assert out[0] == pytest.approx({"A": 0.2, "B": 0.8})


def test_apply_isotonic_requires_transform():
    with pytest.raises(ValueError, match="transform"):
        apply_calibration([{"A": 1.0}], "isotonic", calibrator_params={})


def test_apply_object_uses_transform():
    class Cal:
        def transform(self, p):
            return [{"A": 1.0}]

    probs = [{"A": 0.5, "B": 0.5}]
    out = apply_calibration(probs, Cal())
    assert out == [{"A": 1.0}]


def test_apply_unknown_string():
    with pytest.raises(ValueError, match="Unsupported"):
        apply_calibration([{"A": 1.0}], "platt")


def test_apply_unknown_object():
    with pytest.raises(ValueError, match="Unsupported"):
        apply_calibration([{"A": 1.0}], object())


def test_fit_temperature_single_row():
    probs_calib = [{"A": 0.9, "B": 0.1}]
    labels_calib = ["A"]
    t = fit_temperature(probs_calib, labels_calib)
    assert 1e-2 <= t <= 100.0


def test_fit_temperature_length_mismatch():
    with pytest.raises(ValueError, match="mismatch"):
        fit_temperature([{"A": 1.0}], [])


def test_temperature_one_preserves_ece():
    probs = [
        {"A": 0.9, "B": 0.1},
        {"A": 0.2, "B": 0.8},
        {"A": 0.6, "B": 0.4},
    ]
    correctness = [1, 1, 0]
    conf_before = [max(row.values()) for row in probs]
    ece_before = expected_calibration_error_from_confidence(
        confidences=conf_before,
        correctness=correctness,
        n_bins=5,
    )
    scaled = apply_calibration(
        probs,
        "temperature_scaling",
        calibrator_params={"temperature": 1.0},
    )
    conf_after = [max(row.values()) for row in scaled]
    ece_after = expected_calibration_error_from_confidence(
        confidences=conf_after,
        correctness=correctness,
        n_bins=5,
    )
    assert ece_after == pytest.approx(ece_before)
