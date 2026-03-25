"""Registry of dataset ids to loader callables.

Use :data:`DATASET_REGISTRY` and :func:`get_loader` to resolve loaders from config
without hard-coding imports at every call site.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from reliability_eval.data.mednli import load_mednli
from reliability_eval.data.pubmed_rct import load_pubmed_rct

DATASET_REGISTRY: dict[str, Callable[..., Any]] = {
    "pubmed_rct": load_pubmed_rct,
    "mednli": load_mednli,
}


def get_loader(dataset_id: str) -> Callable[..., Any]:
    """Return the loader callable for ``dataset_id``.

    Raises:
        KeyError: If ``dataset_id`` is not registered in :data:`DATASET_REGISTRY`.
    """
    if dataset_id not in DATASET_REGISTRY:
        known = ", ".join(sorted(DATASET_REGISTRY))
        raise KeyError(f"Unknown dataset_id {dataset_id!r}; registered: {known}")
    return DATASET_REGISTRY[dataset_id]
