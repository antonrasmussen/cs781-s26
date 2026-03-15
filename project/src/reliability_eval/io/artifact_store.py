"""Minimal artifact writing for MVP runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def ensure_run_dir(artifact_root: str, run_id: str) -> Path:
    """Create and return run directory."""
    run_dir = Path(artifact_root) / run_id
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
