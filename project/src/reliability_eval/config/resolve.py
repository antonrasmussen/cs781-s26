"""Centralized config resolution with execution profiles."""

from __future__ import annotations

import os
import warnings
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def _load_yaml(path: Path) -> dict:
    """Load YAML file; return empty dict on error or missing file.

    Non-mapping document roots (e.g. a list or scalar) are treated as invalid and
    return {} with a warning.
    """
    try:
        import yaml  # type: ignore
    except ImportError:
        return {}
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        loaded = yaml.safe_load(f)
    if loaded is None:
        return {}
    if not isinstance(loaded, Mapping):
        warnings.warn(
            f"YAML root at {path} is not a mapping; using empty dict",
            stacklevel=2,
        )
        return {}
    return dict(loaded)


def _deep_merge(base: dict, overlay: dict) -> dict:
    """Merge overlay into base recursively. Overlay values override base."""
    result = dict(base)
    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _validated_sample_size(sample_size: Any) -> int:
    """Return a positive int sample_size or raise ValueError."""
    if isinstance(sample_size, bool):
        raise ValueError("sample_size must be a positive integer, not bool")
    if isinstance(sample_size, int):
        n = sample_size
    else:
        try:
            n = int(sample_size)
        except (TypeError, ValueError) as e:
            raise ValueError(
                f"sample_size must be a positive integer, got {sample_size!r}"
            ) from e
    if n <= 0:
        raise ValueError(f"sample_size must be positive, got {n}")
    return n


def resolve_config(
    project_root: Path,
    *,
    sweep_id: str | None = None,
    dataset_id: str = "pubmed_rct",
    model_id: str = "biomistral_7b",
    precision_id: str = "fp16",
    template_id: str = "pubmed_t1",
    calibration_id: str = "none",
    execution_profile: str = "local",
    sample_size: int | None = None,
    experiment_name: str | None = None,
) -> dict[str, Any]:
    """Resolve a full experiment config from layered YAML files.

    Args:
        project_root: Project root directory (contains configs/).
        sweep_id: Optional sweep config id (e.g. mvp_pubmed) to extend.
        dataset_id: Dataset config id.
        model_id: Model config id.
        precision_id: Precision config id.
        template_id: Prompt template id.
        calibration_id: Calibration config id.
        execution_profile: One of local, flyte_sandbox, odu.
        sample_size: Optional cap for small runs.
        experiment_name: Override experiment name.

    Returns:
        Fully resolved config dict suitable for run_single().
    """
    configs_dir = project_root / "configs"

    # Base
    base = _load_yaml(configs_dir / "base.yaml") or {
        "seed": 42,
        "artifact_root": "artifacts/runs",
        "evaluation": {"ece_bins": 15},
    }

    # Sweep overlay (if any)
    if sweep_id:
        sweep_path = configs_dir / "sweeps" / f"{sweep_id}.yaml"
        if sweep_path.exists():
            sweep = _load_yaml(sweep_path)
            base = _deep_merge(base, sweep)

    # Component configs
    dataset_cfg = _load_yaml(configs_dir / "datasets" / f"{dataset_id}.yaml") or {
        "dataset_id": dataset_id,
        "task": dataset_id,
        "path_or_hf_id": None,
    }
    model_cfg = _load_yaml(configs_dir / "models" / f"{model_id}.yaml") or {
        "model_id": model_id,
        "name_or_path": f"unknown/{model_id}",
    }
    precision_cfg = _load_yaml(configs_dir / "precisions" / f"{precision_id}.yaml") or {
        "precision": precision_id,
    }
    calibration_cfg = _load_yaml(configs_dir / "calibration" / f"{calibration_id}.yaml") or {
        "calibration": calibration_id,
    }

    # Execution profile (required; typos must not silently fall back)
    profile_path = configs_dir / "execution" / f"{execution_profile}.yaml"
    if not profile_path.exists():
        raise FileNotFoundError(
            f"Execution profile {execution_profile!r} not found: {profile_path.resolve()}"
        )
    profile_cfg = _load_yaml(profile_path)

    # Artifact root: env override > sweep output > base
    artifact_root = os.environ.get(
        "RELIABILITY_ARTIFACT_ROOT",
        base.get("output", {}).get("artifact_root")
        or base.get("artifact_root", "artifacts/runs"),
    )

    # Assemble
    resolved: dict[str, Any] = {
        "config_dir": str(configs_dir),
        "experiment_name": experiment_name
        or base.get("experiment_name", "reliability_eval"),
        "seed": base.get("seed", 42),
        "task": dataset_cfg.get("task", dataset_id),
        "dataset": dataset_cfg,
        "model": model_cfg,
        "precision": precision_cfg,
        "calibration": calibration_cfg,
        "template_id": template_id,
        "artifact_root": artifact_root,
        "evaluation": base.get("evaluation", {}),
        "hardware": _deep_merge(
            base.get("hardware", {}),
            profile_cfg.get("hardware", {}),
        ),
    }

    if sample_size is not None:
        resolved["sample_size"] = _validated_sample_size(sample_size)

    inference_mode = profile_cfg.get("inference_mode", "mock_inference")
    # Execution profile overlay
    resolved["execution_mode"] = profile_cfg.get("execution_mode", execution_profile)
    resolved["compute_env"] = profile_cfg.get("compute_env", execution_profile)
    resolved["mode"] = inference_mode
    resolved["inference_mode"] = inference_mode

    return resolved


def resolve_mvp_config(
    project_root: Path,
    sample_size: int = 8,
    template_id: str = "pubmed_t1",
    execution_profile: str = "local",
) -> dict[str, Any]:
    """Resolve MVP-specific config (PubMed, FP16, mock inference)."""
    return resolve_config(
        project_root,
        sweep_id="mvp_pubmed",
        dataset_id="pubmed_rct",
        model_id="biomistral_7b",
        precision_id="fp16",
        template_id=template_id,
        calibration_id="none",
        execution_profile=execution_profile,
        sample_size=sample_size,
        experiment_name="mvp_pubmed_reliability",
    )
