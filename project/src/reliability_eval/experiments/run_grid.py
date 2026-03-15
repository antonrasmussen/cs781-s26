"""Expand sweep config into per-run configs; run or queue each."""

from __future__ import annotations

import itertools
from pathlib import Path

from reliability_eval.config.resolve import resolve_config


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
    try:
        import yaml
        if sweep_path.exists():
            with sweep_path.open("r") as f:
                sweep = yaml.safe_load(f) or {}
        else:
            sweep = {}
    except Exception:
        sweep = {}
    combinations = sweep.get("combinations", {})
    experiment_name = sweep.get("experiment_name", sweep_id)

    # Cartesian product over combination keys
    keys = list(combinations.keys())
    if not keys:
        return [resolve_config(project_root, sweep_id=sweep_id, execution_profile=execution_profile, sample_size=sample_size)]

    value_lists = [combinations[k] for k in keys]
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
