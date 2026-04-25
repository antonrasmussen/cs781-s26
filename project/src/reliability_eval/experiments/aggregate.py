"""Aggregate metrics across runs for tables and figures.

TODO: Load all run metrics; build comparison tables; optional Flyte task.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional


def aggregate_metrics(artifact_root: str, run_ids: Optional[List[str]] = None) -> dict:
    """Return combined metrics for real-inference runs under artifact_root."""
    root = Path(artifact_root)
    if not root.exists():
        raise FileNotFoundError(f"Artifact root not found: {artifact_root}")

    selected = set(run_ids) if run_ids else None
    rows = []
    for run_dir in sorted([p for p in root.iterdir() if p.is_dir()]):
        if selected is not None and run_dir.name not in selected:
            continue
        meta_path = run_dir / "metadata.json"
        metrics_path = run_dir / "metrics.json"
        if not (meta_path.exists() and metrics_path.exists()):
            continue
        with meta_path.open("r", encoding="utf-8") as f:
            metadata = json.load(f)
        if metadata.get("inference_mode") != "real_inference":
            continue
        with metrics_path.open("r", encoding="utf-8") as f:
            metrics = json.load(f)
        with (run_dir / "resolved_config.yaml").open("r", encoding="utf-8") as f:
            import yaml

            cfg = yaml.safe_load(f) or {}
        rows.append(
            {
                "run_id": run_dir.name,
                "precision": cfg.get("precision", {}).get("precision", "unknown"),
                "template_id": cfg.get("template_id", "unknown"),
                "n_examples": int(metadata.get("n_examples", metrics.get("n_examples", 0))),
                "accuracy": metrics.get("accuracy"),
                "macro_f1": metrics.get("macro_f1"),
                "ece": metrics.get("ece"),
                "ece_calibrated": metrics.get("ece_calibrated"),
                "temperature": metadata.get("temperature", metrics.get("temperature")),
            }
        )

    return {"n_runs": len(rows), "runs": rows}
