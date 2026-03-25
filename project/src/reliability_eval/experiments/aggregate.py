"""Aggregate metrics across runs for tables and figures.

TODO: Load all run metrics; build comparison tables; optional Flyte task.
"""

from __future__ import annotations

from typing import List, Optional


def aggregate_metrics(artifact_root: str, run_ids: Optional[List[str]] = None) -> dict:
    """Return combined metrics. TODO: Implement."""
    raise NotImplementedError("TODO: implement experiments.aggregate.aggregate_metrics")
