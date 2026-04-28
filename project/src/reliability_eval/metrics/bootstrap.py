"""Small bootstrap helpers for report-time confidence intervals."""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence


def bootstrap_ci(
    values: Sequence,
    statistic: Callable[[list], float],
    *,
    n_resamples: int = 1000,
    seed: int = 42,
    ci: float = 0.95,
) -> dict[str, float]:
    """Return point estimate and percentile bootstrap CI for a statistic."""
    data = list(values)
    if not data:
        raise ValueError("values must be non-empty")
    if n_resamples <= 0:
        raise ValueError("n_resamples must be positive")
    if not (0.0 < ci < 1.0):
        raise ValueError("ci must be in (0, 1)")
    point = float(statistic(data))
    rng = random.Random(seed)
    samples = []
    for _ in range(n_resamples):
        draw = rng.choices(data, k=len(data))
        samples.append(float(statistic(draw)))
    samples.sort()
    alpha = (1.0 - ci) / 2.0
    lo_idx = int(alpha * (n_resamples - 1))
    hi_idx = int((1.0 - alpha) * (n_resamples - 1))
    return {"point": point, "ci_low": samples[lo_idx], "ci_high": samples[hi_idx]}
