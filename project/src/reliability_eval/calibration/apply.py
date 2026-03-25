"""Apply fitted calibration to test-time probabilities."""

from __future__ import annotations

from reliability_eval.calibration.isotonic import isotonic_calibration
from reliability_eval.calibration.temperature_scaling import apply_temperature_scaling


def apply_calibration(
    probs: list,
    calibrator,
    *,
    calibrator_params: dict | None = None,
) -> list:
    """Apply ``calibrator`` to probability rows (list of per-class dicts).

    Args:
        probs: List of mappings ``class_key -> probability``.
        calibrator: ``None``, the string ``"none"``, a method name string, or a calibrator object.
        calibrator_params: Extra parameters for string methods (e.g. ``temperature``).

    Returns:
        Calibrated probability rows (new list).

    Raises:
        ValueError: Unknown string/object calibrator or invalid parameters.
    """
    params = calibrator_params if calibrator_params is not None else {}

    if calibrator is None or (
        isinstance(calibrator, str) and calibrator.lower() == "none"
    ):
        return [dict(row) for row in probs]

    if isinstance(calibrator, str):
        key = calibrator.lower().replace("-", "_")
        if key == "temperature_scaling":
            return apply_temperature_scaling(probs, params)
        if key == "isotonic":
            return isotonic_calibration(probs, params)
        raise ValueError(f"Unsupported calibrator string: {calibrator!r}")

    for name in ("temperature_scale", "transform", "calibrate"):
        fn = getattr(calibrator, name, None)
        if callable(fn):
            return fn(probs)

    raise ValueError(
        f"Unsupported calibrator object {type(calibrator)!r}: "
        "expected a method temperature_scale, transform, or calibrate"
    )
