"""Run metadata manifest helpers.

Artifact contract: metadata.json must include these provenance fields for
cross-mode comparability: run_id, created_at_utc, config_hash, execution_mode,
compute_env, code_version, dataset_source, inference_mode, n_examples, figure.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone


def _get_code_version() -> str:
    """Return git commit hash if available, else 'unknown'."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def create_manifest(
    run_id: str,
    config: dict,
    *,
    n_examples: int = 0,
    figure_path: str = "",
    dataset_source: str = "",
    inference_mode: str = "",
) -> dict:
    """Build run metadata manifest with required provenance fields."""
    config_str = json.dumps(config, sort_keys=True)
    config_hash = hashlib.sha256(config_str.encode("utf-8")).hexdigest()[:12]

    manifest = {
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "config_hash": config_hash,
        "execution_mode": config.get("execution_mode", "unknown"),
        "compute_env": config.get("compute_env", "unknown"),
        "code_version": _get_code_version(),
        "dataset_source": dataset_source or "unknown",
        "inference_mode": inference_mode
        or config.get("inference_mode")
        or config.get("mode", "unknown"),
        "n_examples": n_examples,
        "figure": figure_path,
    }
    return manifest
