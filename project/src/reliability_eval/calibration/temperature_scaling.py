"""Temperature scaling (Guo et al.): scalar T on calibration logits / probabilities."""

from __future__ import annotations

import math
from collections.abc import Hashable, Mapping, Sequence

Row = Mapping[Hashable, float]


def _softmax(logits: Sequence[float]) -> list[float]:
    if not logits:
        return []
    m = max(logits)
    exps = [math.exp(x - m) for x in logits]
    s = sum(exps)
    return [e / s for e in exps]


def _row_temperature_softmax(row: Row, temperature: float) -> dict[Hashable, float]:
    keys = list(row.keys())
    logits = [math.log(max(float(row[k]), 1e-12)) for k in keys]
    scaled = [x / temperature for x in logits]
    probs = _softmax(scaled)
    return dict(zip(keys, probs, strict=True))


def apply_temperature_scaling(probs: list, calibrator_params: dict) -> list:
    """Apply softmax temperature scaling to each probability row (mapping of class -> prob)."""
    t = calibrator_params.get("temperature")
    if t is None:
        raise ValueError("calibrator_params must include 'temperature' for temperature_scaling")
    t_f = float(t)
    if t_f <= 0:
        raise ValueError("'temperature' must be positive")
    return [_row_temperature_softmax(row, t_f) for row in probs]


def fit_temperature(probs_calib: Sequence[Row], labels_calib: Sequence[Hashable]) -> float:
    """Fit a positive scalar temperature T minimizing mean NLL on the calibration set.

    Uses a fixed geometric grid on ``T`` in ``[1e-2, 100]`` (pure Python, no SciPy).

    Args:
        probs_calib: Sequence of row-wise class-probability mappings (keys = class ids).
        labels_calib: True class key per row; each key must exist in the corresponding row.
    """
    if len(probs_calib) != len(labels_calib):
        raise ValueError("probs_calib and labels_calib length mismatch")
    if not probs_calib:
        raise ValueError("empty calibration set")

    def nll(temperature: float) -> float:
        total = 0.0
        for row, y in zip(probs_calib, labels_calib, strict=True):
            if y not in row:
                raise ValueError(
                    f"label {y!r} not in probability row keys {set(row)!r}"
                )
            scaled_row = _row_temperature_softmax(row, temperature)
            p = max(float(scaled_row[y]), 1e-12)
            total += -math.log(p)
        return total / len(probs_calib)

    lo, hi = 1e-2, 100.0
    best_t, best_score = 1.0, nll(1.0)
    n_steps = 64
    factor = (hi / lo) ** (1.0 / (n_steps - 1))
    t = lo
    for _ in range(n_steps):
        score = nll(t)
        if score < best_score:
            best_score = score
            best_t = t
        t *= factor
        if t > hi:
            break
    return float(best_t)
