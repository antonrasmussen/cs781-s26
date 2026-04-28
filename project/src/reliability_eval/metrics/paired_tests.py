"""Small paired-stat helpers used by final report script."""

from __future__ import annotations

from collections.abc import Sequence

from reliability_eval.metrics.bootstrap import bootstrap_ci


def paired_bootstrap_ci(
    deltas: Sequence[float], *, n_resamples: int = 1000, seed: int = 42
) -> dict[str, float]:
    """Bootstrap CI for the mean of paired deltas."""
    return bootstrap_ci(
        list(deltas),
        lambda xs: sum(xs) / len(xs),
        n_resamples=n_resamples,
        seed=seed,
    )


def recovery_ratio(*, ece_uncal: float, ece_cal: float, ece_fp16: float) -> float:
    """Fraction of quantization-induced miscalibration recovered by calibration."""
    denom = float(ece_uncal) - float(ece_fp16)
    if abs(denom) <= 1e-12:
        raise ValueError("recovery_ratio undefined when ece_uncal == ece_fp16")
    return (float(ece_uncal) - float(ece_cal)) / denom
