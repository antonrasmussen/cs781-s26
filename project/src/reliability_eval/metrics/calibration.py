"""Minimal calibration metrics for MVP (ECE + bin stats)."""

from __future__ import annotations

from typing import Dict, List, Sequence


def _validate_confidences(confidences: Sequence[float]) -> None:
    for i, c in enumerate(confidences):
        if isinstance(c, bool) or not isinstance(c, (int, float)):
            raise ValueError(
                f"All confidences must be numeric in [0.0, 1.0]; index {i} has {c!r}"
            )
        cf = float(c)
        if cf < 0.0 or cf > 1.0:
            raise ValueError(
                f"All confidences must be in [0.0, 1.0]; index {i} has {c!r}"
            )


def reliability_bins(
    confidences: Sequence[float],
    correctness: Sequence[int],
    n_bins: int = 15,
) -> List[Dict]:
    """Return per-bin confidence/accuracy/count for a reliability diagram."""
    if len(confidences) != len(correctness):
        raise ValueError("confidences and correctness length mismatch")
    if n_bins <= 0:
        raise ValueError("n_bins must be positive")
    _validate_confidences(confidences)

    bins: List[Dict] = []
    for i in range(n_bins):
        left = i / n_bins
        right = (i + 1) / n_bins
        is_last = i == (n_bins - 1)
        if is_last:
            idx = [j for j, c in enumerate(confidences) if left <= c <= right]
        else:
            idx = [j for j, c in enumerate(confidences) if left <= c < right]
        if idx:
            bin_conf = sum(confidences[j] for j in idx) / len(idx)
            bin_acc = sum(correctness[j] for j in idx) / len(idx)
        else:
            bin_conf = 0.0
            bin_acc = 0.0
        bins.append(
            {
                "left": left,
                "right": right,
                "count": len(idx),
                "avg_confidence": bin_conf,
                "avg_accuracy": bin_acc,
            }
        )
    return bins


def expected_calibration_error_from_confidence(
    confidences: Sequence[float],
    correctness: Sequence[int],
    n_bins: int = 15,
) -> float:
    """Compute ECE from confidences and correctness."""
    bins = reliability_bins(confidences, correctness, n_bins=n_bins)
    n = len(confidences)
    if n == 0:
        raise ValueError("No examples")
    ece = 0.0
    for b in bins:
        if b["count"] == 0:
            continue
        weight = b["count"] / n
        ece += weight * abs(b["avg_accuracy"] - b["avg_confidence"])
    return float(ece)


def expected_calibration_error(y_true, y_pred, confidences, n_bins: int = 15) -> float:
    """Compute ECE from true labels, predictions, and confidences."""
    if not (len(y_true) == len(y_pred) == len(confidences)):
        raise ValueError("Input length mismatch")
    correctness = [1 if t == p else 0 for t, p in zip(y_true, y_pred, strict=True)]
    return expected_calibration_error_from_confidence(
        confidences=confidences,
        correctness=correctness,
        n_bins=n_bins,
    )
