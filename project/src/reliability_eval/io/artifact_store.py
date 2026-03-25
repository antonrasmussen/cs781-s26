"""Minimal artifact writing for MVP runs."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable


def _safe_run_id_segment(run_id: str) -> str:
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id must be a non-empty string")
    if ".." in run_id:
        raise ValueError(f"Invalid run_id {run_id!r}: parent segments ('..') are not allowed")
    if os.sep in run_id or (os.altsep and os.altsep in run_id):
        raise ValueError(f"Invalid run_id {run_id!r}: path separators are not allowed")
    safe = Path(run_id).name
    if safe != run_id or safe in (".", ".."):
        raise ValueError(f"Invalid run_id {run_id!r}: must be a single path segment")
    return safe


def ensure_run_dir(artifact_root: str, run_id: str) -> Path:
    """Create and return run directory under artifact_root.

    run_id must be a single path segment (no ``..`` or separators) so the run
    directory cannot escape artifact_root after resolution.
    """
    root = Path(artifact_root).resolve()
    safe_name = _safe_run_id_segment(run_id)
    run_dir = (root / safe_name).resolve()
    if not run_dir.is_relative_to(root):
        raise ValueError(
            f"Resolved run directory {run_dir} is outside artifact root {root}"
        )
    (run_dir / "figures").mkdir(parents=True, exist_ok=True)
    return run_dir


def save_resolved_config(run_dir: str | Path, config: dict) -> None:
    """Write resolved_config.yaml. Uses PyYAML when available for proper YAML."""
    path = Path(run_dir) / "resolved_config.yaml"
    try:
        import yaml  # type: ignore
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
    except ImportError:
        with path.open("w", encoding="utf-8") as f:
            f.write(json.dumps(config, indent=2))


def save_metadata(run_dir: str | Path, metadata: dict) -> None:
    """Write metadata.json."""
    path = Path(run_dir) / "metadata.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def save_predictions(run_dir: str | Path, predictions: Iterable[dict]) -> None:
    """Write predictions.jsonl."""
    path = Path(run_dir) / "predictions.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for row in predictions:
            f.write(json.dumps(row) + "\n")


def save_metrics(run_dir: str | Path, metrics: dict) -> None:
    """Write metrics.json under run_dir."""
    path = Path(run_dir) / "metrics.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
