"""Execute one full run from resolved config: load data, model, run eval, save artifacts.

This is the canonical plain-Python pipeline. All execution modes (local, Flyte sandbox,
ODU) should call this function rather than duplicating orchestration logic.
"""

from __future__ import annotations

from pathlib import Path

from reliability_eval.data.pubmed_rct import load_pubmed_rct
from reliability_eval.inference.score_class_codes import mock_score_example
from reliability_eval.io.artifact_store import (
    ensure_run_dir,
    save_metadata,
    save_metrics,
    save_predictions,
    save_resolved_config,
)
from reliability_eval.io.paths import make_run_id
from reliability_eval.io.run_manifest import create_manifest
from reliability_eval.metrics.calibration import expected_calibration_error
from reliability_eval.metrics.classification import compute_metrics
from reliability_eval.prompting.label_codes import get_label_codes
from reliability_eval.prompting.render import render
from reliability_eval.reporting.reliability_diagrams import plot_reliability


def run_single(config: dict, run_id: str | None = None) -> str:
    """Run one experiment from resolved config; return run_id.

    Args:
        config: Fully resolved experiment config (task, dataset, model, precision,
            template_id, sample_size, artifact_root, evaluation, mode, etc.).
        run_id: Optional run identifier. If None, one is generated.

    Returns:
        The run_id used for this run.
    """
    if run_id is None:
        prefix = config.get("experiment_name", "run").replace(" ", "_").lower()[:20]
        run_id = make_run_id(prefix=prefix)

    run_dir = ensure_run_dir(config["artifact_root"], run_id)
    task = config.get("task", "pubmed_rct")
    template_id = config.get("template_id", "pubmed_t1")
    sample_size = config.get("sample_size")
    eval_cfg = config.get("evaluation", {})
    n_bins = int(eval_cfg.get("ece_bins", 15))

    # Load dataset
    dataset_cfg = config.get("dataset", {})
    path_or_hf_id = dataset_cfg.get("path_or_hf_id")
    examples = load_pubmed_rct(
        path_or_hf_id=path_or_hf_id,
        split="test",
        sample_size=sample_size,
    )

    label_codes = get_label_codes(task)
    predictions = []
    y_true = []
    y_pred = []
    confidences = []

    # Run inference (mock path for MVP; real model path will replace this)
    inference_mode = config.get("mode", "mock_inference")
    config_dir = config.get("config_dir")
    for ex in examples:
        prompt = render(
            template_id=template_id,
            task=task,
            text=ex["text"],
            label_codes=label_codes,
            config_dir=config_dir,
        )
        if inference_mode == "mock_inference":
            result = mock_score_example(
                prompt=prompt,
                task=task,
                example_id=ex["example_id"],
                true_label=ex["label"],
            )
        else:
            raise NotImplementedError(
                f"Real inference not yet implemented; mode={inference_mode}"
            )

        y_true.append(ex["label"])
        y_pred.append(result["predicted_label"])
        confidences.append(float(result["confidence"]))
        predictions.append(
            {
                "example_id": ex["example_id"],
                "text": ex["text"],
                "true_label": ex["label"],
                "template_id": template_id,
                "prompt": prompt,
                "predicted_label": result["predicted_label"],
                "predicted_code": result["predicted_code"],
                "confidence": result["confidence"],
                "probabilities": result["probabilities"],
            }
        )

    # Compute metrics
    metrics = compute_metrics(y_true=y_true, y_pred=y_pred)
    metrics["ece"] = expected_calibration_error(
        y_true=y_true,
        y_pred=y_pred,
        confidences=confidences,
        n_bins=n_bins,
    )

    # Generate reliability diagram
    correctness = [1 if t == p else 0 for t, p in zip(y_true, y_pred)]
    figure_path = run_dir / "figures" / "reliability.png"
    plot_reliability(
        confidences=confidences,
        correctness=correctness,
        n_bins=n_bins,
        path=str(figure_path),
    )

    # Write artifacts
    save_resolved_config(run_dir, config)
    save_predictions(run_dir, predictions)
    save_metrics(run_dir, metrics)

    dataset_source = _infer_dataset_source(config, path_or_hf_id)
    metadata = create_manifest(
        run_id=run_id,
        config=config,
        n_examples=len(examples),
        figure_path=str(figure_path),
        dataset_source=dataset_source,
        inference_mode=inference_mode,
    )
    save_metadata(run_dir, metadata)

    return run_id


def _infer_dataset_source(config: dict, path_or_hf_id: str | None) -> str:
    """Infer dataset source for provenance metadata."""
    if path_or_hf_id and Path(path_or_hf_id).exists():
        return str(path_or_hf_id)
    dataset_id = config.get("dataset", {}).get("dataset_id", "unknown")
    return f"{dataset_id}_tiny"
