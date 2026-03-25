"""Expand sweep config into per-run configs; run or queue each."""

from __future__ import annotations

import itertools
from pathlib import Path
from typing import Any

from reliability_eval.config.resolve import resolve_config


def _combination_values(key: str, raw: Any) -> list[Any]:
    """Normalize a sweep combination value to a non-empty list."""
    if raw is None:
        raise ValueError(f'Sweep "combinations" entry {key!r} must not be null')
    if isinstance(raw, dict):
        raise ValueError(f'Sweep "combinations" entry {key!r} cannot be a mapping')
    if isinstance(raw, (str, bytes)):
        return [raw]
    if isinstance(raw, bool):
        return [raw]
    if isinstance(raw, int):
        return [raw]
    if isinstance(raw, float):
        return [raw]
    if isinstance(raw, (list, tuple)):
        if len(raw) == 0:
            raise ValueError(f'Sweep "combinations" entry {key!r} must be non-empty')
        return list(raw)
    try:
        seq = list(raw)
    except TypeError:
        return [raw]
    if len(seq) == 0:
        raise ValueError(f'Sweep "combinations" entry {key!r} must be non-empty')
    return seq


def _load_sweep_file(sweep_path: Path) -> dict[str, Any]:
    """Load sweep YAML; missing file -> empty dict; parse errors propagate with context."""
    if not sweep_path.exists():
        return {}
    import yaml

    with sweep_path.open("r", encoding="utf-8") as f:
        try:
            loaded = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid sweep YAML {sweep_path}: {e}") from e
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Sweep root must be a mapping: {sweep_path}")
    return loaded


def expand_sweep(
    project_root: Path,
    sweep_id: str,
    *,
    execution_profile: str = "local",
    sample_size: int | None = None,
) -> list[dict]:
    """Expand sweep combinations into list of resolved run configs.

    Args:
        project_root: Project root (contains configs/).
        sweep_id: Sweep config id (e.g. mvp_pubmed).
        execution_profile: local, flyte_sandbox, or odu.
        sample_size: Optional cap for small runs.

    Returns:
        List of fully resolved config dicts for run_single().
    """
    sweep_path = project_root / "configs" / "sweeps" / f"{sweep_id}.yaml"
    sweep = _load_sweep_file(sweep_path)
    combinations = sweep.get("combinations", {})
    experiment_name = sweep.get("experiment_name", sweep_id)

    # Cartesian product over combination keys
    keys = list(combinations.keys())
    if not keys:
        return [resolve_config(project_root, sweep_id=sweep_id, execution_profile=execution_profile, sample_size=sample_size)]

    value_lists = [_combination_values(k, combinations[k]) for k in keys]
    configs = []
    for values in itertools.product(*value_lists):
        combo = dict(zip(keys, values))
        dataset_id = combo.get("dataset", "pubmed_rct")
        model_id = combo.get("model", "biomistral_7b")
        precision_id = combo.get("precision", "fp16")
        template_id = combo.get("prompt_template", "pubmed_t1")
        calibration_id = combo.get("calibration", "none")

        cfg = resolve_config(
            project_root,
            sweep_id=sweep_id,
            dataset_id=dataset_id,
            model_id=model_id,
            precision_id=precision_id,
            template_id=template_id,
            calibration_id=calibration_id,
            execution_profile=execution_profile,
            sample_size=sample_size,
            experiment_name=experiment_name,
        )
        configs.append(cfg)
    return configs
