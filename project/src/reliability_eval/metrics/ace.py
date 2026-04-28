"""Adaptive calibration error with equal-mass binning."""

from __future__ import annotations

from collections.abc import Sequence


def adaptive_calibration_error(
    *,
    confidences: Sequence[float],
    correctness: Sequence[int],
    n_bins: int = 15,
) -> float:
    """Compute ACE by splitting examples into equal-mass confidence bins."""
    if len(confidences) != len(correctness):
        raise ValueError("confidences and correctness length mismatch")
    if not confidences:
        raise ValueError("No examples")
    if n_bins <= 0:
        raise ValueError("n_bins must be positive")
    pairs = sorted(
        [(float(c), int(ok)) for c, ok in zip(confidences, correctness, strict=True)],
        key=lambda x: x[0],
    )
    n = len(pairs)
    n_bins = min(n_bins, n)
    base = n // n_bins
    rem = n % n_bins
    idx = 0
    ace = 0.0
    for b in range(n_bins):
        size = base + (1 if b < rem else 0)
        chunk = pairs[idx : idx + size]
        idx += size
        conf = sum(c for c, _ in chunk) / size
        acc = sum(ok for _, ok in chunk) / size
        ace += (size / n) * abs(acc - conf)
    return float(ace)
