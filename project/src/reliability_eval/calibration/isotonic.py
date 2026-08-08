"""Isotonic regression per class (Zadrozny & Elkan).

Manuscript scope: apply path exists for a supplied ``transform`` callable;
``fit_isotonic`` is **deferred / not implemented**. Temperature scaling is the
only fitted calibrator in the current evidence package
(see ``docs/manuscript_claim_boundaries.md``).
"""

from __future__ import annotations

from collections.abc import Callable


def isotonic_calibration(probs: list, calibrator_params: dict) -> list:
    """Apply a monotone 1D calibration to each component of every probability row.

    After mapping, probabilities are renormalized per row to sum to 1 when possible.

    Args:
        probs: List of per-row mappings ``class_id -> probability``.
        calibrator_params: Must include ``transform``, a ``float -> float`` callable
            (e.g. output of a fitted isotonic regressor on a scalar score).

    Raises:
        ValueError: If ``transform`` is missing or not callable.
    """
    transform = calibrator_params.get("transform")
    if transform is None or not callable(transform):
        raise ValueError(
            "isotonic calibration requires calibrator_params['transform'] to be a callable"
        )
    return _apply_monotone_then_renorm(probs, transform)


def _apply_monotone_then_renorm(probs: list, transform: Callable[[float], float]) -> list:
    out: list = []
    for row in probs:
        if not isinstance(row, dict):
            raise TypeError("each probability row must be a mapping (e.g. dict)")
        raw = {k: max(float(transform(float(v))), 0.0) for k, v in row.items()}
        s = sum(raw.values())
        if s <= 0:
            raise ValueError("isotonic transform produced no positive mass for a row")
        out.append({k: raw[k] / s for k in raw})
    return out


def fit_isotonic(probs_calib, labels_calib):
    """Return fitted isotonic mapper(s).

    Not implemented for the current manuscript package (deferred).
    """
    raise NotImplementedError(
        "isotonic.fit_isotonic is deferred; see docs/manuscript_claim_boundaries.md"
    )
