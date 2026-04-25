"""Train/val/calibration/test split helpers.

Calibration examples are a deterministic subset of the validation split
(see ``docs/experiment_protocol.md``).
"""

from __future__ import annotations

import random
from typing import Any, List, Mapping


def make_calibration_split(
    examples: List[Mapping[str, Any]],
    *,
    seed: int = 42,
    calibration_fraction: float = 0.15,
) -> dict[str, list]:
    """Partition ``examples`` into calibration vs remaining validation.

    Shuffles **indices** with ``random.Random(seed)``, takes the first
    ``int(len(examples) * calibration_fraction)`` indices for calibration,
    then sorts indices within each side so **original example order** is
    preserved inside each output list.

    Args:
        examples: Normalized records (e.g. from ``load_pubmed_rct``).
        seed: RNG seed (default 42).
        calibration_fraction: Fraction of ``examples`` for calibration (default 0.15).

    Returns:
        ``{"calibration": [...], "remaining_val": [...]}`` — disjoint lists whose
        concatenation in index order is not guaranteed to match input order;
        together they partition the multiset of examples.
    """
    n = len(examples)
    if n == 0:
        return {"calibration": [], "remaining_val": []}

    idxs = list(range(n))
    shuffled = idxs.copy()
    random.Random(seed).shuffle(shuffled)

    k = int(n * float(calibration_fraction))
    k = max(0, min(k, n))

    cal_set = set(shuffled[:k])
    rem_set = set(shuffled[k:])

    cal_sorted = sorted(cal_set)
    rem_sorted = sorted(rem_set)

    return {
        "calibration": [examples[i] for i in cal_sorted],
        "remaining_val": [examples[i] for i in rem_sorted],
    }


def get_splits(dataset_id: str, seed: int = 42) -> list[str]:
    """Return conceptual split names (legacy shim).

    Prefer :func:`make_calibration_split` for calibration partitioning.
    """
    _ = dataset_id, seed
    return ["train", "val", "calibration", "test"]
