"""Fleiss' kappa across templates; per-sample flip rate."""


from __future__ import annotations

import random


def fleiss_kappa(predictions_per_template: list) -> float:
    """Fleiss' kappa treating each prompt template as a rater.

    Args:
        predictions_per_template: Non-empty list of iterables; each iterable has one
            categorical label per subject, and all iterables must have the same length.

    Returns:
        Fleiss' kappa in ``[-1, 1]`` (typically ``[0, 1]`` for structured tasks).

    Raises:
        ValueError: Invalid shape, fewer than two categories, or fewer than two raters.
    """
    if not predictions_per_template:
        raise ValueError("predictions_per_template must be non-empty")
    rows = [list(r) for r in predictions_per_template]
    n_raters = len(rows)
    if n_raters < 2:
        raise ValueError("Fleiss kappa requires at least two raters (templates)")
    n_subjects = len(rows[0])
    if n_subjects == 0:
        raise ValueError("each template must assign at least one subject")
    for i, r in enumerate(rows):
        if len(r) != n_subjects:
            raise ValueError(
                f"template rows must have equal length; row 0 has {n_subjects}, "
                f"row {i} has {len(r)}"
            )

    categories = sorted({x for r in rows for x in r})
    k = len(categories)
    if k < 2:
        raise ValueError("need at least two distinct categories for Fleiss kappa")

    cat_index = {c: i for i, c in enumerate(categories)}
    counts = [[0] * k for _ in range(n_subjects)]
    for r in rows:
        for s, label in enumerate(r):
            counts[s][cat_index[label]] += 1

    n = n_raters
    for s in range(n_subjects):
        row_sum = sum(counts[s])
        if row_sum != n:
            raise ValueError(
                f"subject {s} has {row_sum} assignments but expected {n} (one per rater)"
            )

    p_per_subject: list[float] = []
    for s in range(n_subjects):
        acc = sum(c * c for c in counts[s])
        p_i = (acc - n) / (n * (n - 1))
        p_per_subject.append(p_i)

    p_bar = sum(p_per_subject) / n_subjects

    p_j = [0.0] * k
    for j in range(k):
        p_j[j] = sum(counts[s][j] for s in range(n_subjects)) / (n_subjects * n)

    p_e = sum(x * x for x in p_j)
    denom = 1.0 - p_e
    if denom <= 1e-15:
        if abs(p_bar - 1.0) <= 1e-12:
            return 1.0
        raise ValueError(
            "cannot compute Fleiss kappa: chance agreement is 1.0 but subjects are not all unanimous"
        )

    return (p_bar - p_e) / denom


def fleiss_kappa_bootstrap_ci(
    predictions_per_template: list,
    *,
    n_resamples: int = 1000,
    seed: int = 42,
) -> dict[str, float]:
    """Bootstrap CI for Fleiss' kappa by resampling subject indices."""
    if n_resamples <= 0:
        raise ValueError("n_resamples must be positive")
    rows = [list(r) for r in predictions_per_template]
    if not rows or not rows[0]:
        raise ValueError("predictions_per_template must be non-empty")
    n_subjects = len(rows[0])
    for row in rows:
        if len(row) != n_subjects:
            raise ValueError("all template rows must have equal length")
    point = fleiss_kappa(rows)
    rng = random.Random(seed)
    samples = []
    for _ in range(n_resamples):
        idxs = [rng.randrange(n_subjects) for _ in range(n_subjects)]
        boot = [[row[i] for i in idxs] for row in rows]
        if len({label for row in boot for label in row}) < 2:
            # Degenerate resample with one class only; treat as perfect agreement.
            samples.append(1.0)
            continue
        samples.append(fleiss_kappa(boot))
    samples.sort()
    lo_idx = int(0.025 * (n_resamples - 1))
    hi_idx = int(0.975 * (n_resamples - 1))
    return {"point": point, "ci_low": samples[lo_idx], "ci_high": samples[hi_idx]}
