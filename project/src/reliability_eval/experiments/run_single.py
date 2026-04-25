"""Execute one full run from resolved config: load data, model, run eval, save artifacts.

This is the canonical plain-Python pipeline. All execution modes (local, Flyte sandbox,
ODU) should call this function rather than duplicating orchestration logic.
"""

from __future__ import annotations

import json
from pathlib import Path

from reliability_eval.calibration.apply import apply_calibration
from reliability_eval.calibration.temperature_scaling import fit_temperature
from reliability_eval.data.dataset_registry import get_loader
from reliability_eval.data.splits import make_calibration_split
from reliability_eval.inference.batch_runner import run_eval
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
from reliability_eval.models.load_model import load_biomistral
from reliability_eval.prompting.label_codes import get_label_codes
from reliability_eval.prompting.render import render
from reliability_eval.reporting.reliability_diagrams import plot_reliability


def _load_dataset_examples(
    dataset_cfg: dict,
    *,
    sample_size: int | None,
    split: str = "test",
) -> list:
    """Load examples for the configured dataset."""
    dataset_id = dataset_cfg.get("dataset_id", "pubmed_rct")
    path_or_hf_id = dataset_cfg.get("path_or_hf_id")
    hf_revision = dataset_cfg.get("hf_revision")

    try:
        loader = get_loader(dataset_id)
    except KeyError as e:
        raise ValueError(f"Unsupported dataset_id: {dataset_id!r}") from e

    if dataset_id == "pubmed_rct":
        return loader(
            path_or_hf_id=path_or_hf_id,
            split=split,
            sample_size=sample_size,
            hf_revision=hf_revision,
        )
    if dataset_id == "mednli":
        try:
            examples = loader(path_or_hf_id=path_or_hf_id, split=split)
        except NotImplementedError as e:
            raise ValueError(
                "MedNLI dataset loading is not implemented yet; use dataset_id "
                "'pubmed_rct' or implement load_mednli."
            ) from e
        if sample_size is not None:
            return examples[: max(0, int(sample_size))]
        return examples

    raise ValueError(
        f"dataset_id {dataset_id!r} is registered but not wired in _load_dataset_examples"
    )


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
    calibration_cfg = config.get("calibration", {})
    calibration_method = str(calibration_cfg.get("calibration", "none")).lower()
    calibration_sample_size = int(config.get("calibration_sample_size", sample_size or 200))

    # Load dataset
    dataset_cfg = config.get("dataset", {})
    path_or_hf_id = dataset_cfg.get("path_or_hf_id")
    examples = _load_dataset_examples(dataset_cfg, sample_size=sample_size, split="test")

    inference_mode = config.get("inference_mode") or config.get("mode", "mock_inference")
    config_dir = config.get("config_dir")
    if inference_mode == "mock_inference":
        model = None
        tokenizer = None
        label_codes = get_label_codes(task)
        predictions = []
        y_true = []
        y_pred = []
        confidences = []
        for ex in examples:
            prompt = render(
                template_id=template_id,
                task=task,
                text=ex["text"],
                label_codes=label_codes,
                config_dir=config_dir,
            )
            result = mock_score_example(
                prompt=prompt,
                task=task,
                example_id=ex["example_id"],
                true_label=ex["label"],
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
    elif inference_mode == "real_inference":
        model_cfg = config.get("model", {})
        precision_cfg = config.get("precision", {})
        model, tokenizer = load_biomistral(
            precision=precision_cfg.get("precision", "fp16"),
            name_or_path=model_cfg.get("name_or_path", "BioMistral/BioMistral-7B"),
            revision=model_cfg.get("revision"),
            device_map=config.get("hardware", {}).get("device_map", "auto"),
        )
        outputs = run_eval(
            model=model,
            tokenizer=tokenizer,
            dataset=examples,
            template_id=template_id,
            task=task,
            config_dir=config_dir,
            run_generation_sanity_check=bool(config.get("sanity_check_generation", False)),
        )
        predictions = outputs["predictions"]
        y_true = outputs["y_true"]
        y_pred = outputs["y_pred"]
        confidences = outputs["confidences"]
    else:
        raise ValueError(f"Unsupported inference_mode: {inference_mode}")

    # Compute metrics (uncalibrated)
    metrics = compute_metrics(y_true=y_true, y_pred=y_pred)
    metrics["ece"] = expected_calibration_error(
        y_true=y_true,
        y_pred=y_pred,
        confidences=confidences,
        n_bins=n_bins,
    )

    if calibration_method == "temperature_scaling":
        if inference_mode != "real_inference":
            raise ValueError(
                "temperature_scaling requires inference_mode=real_inference "
                "to fit on a calibration split"
            )
        probs_test = _prediction_probs(predictions=predictions)
        probs_calib, labels_calib_codes = _load_calibration_probabilities(
            config=config,
            model=model,
            tokenizer=tokenizer,
            task=task,
            template_id=template_id,
            config_dir=config_dir,
            sample_size=calibration_sample_size,
        )
        temperature = fit_temperature(probs_calib=probs_calib, labels_calib=labels_calib_codes)
        calibrated_probs = apply_calibration(
            probs_test,
            "temperature_scaling",
            calibrator_params={"temperature": float(temperature)},
        )
        calibrated_eval = _preds_and_conf_from_probs(
            probs=calibrated_probs,
            task=task,
        )
        metrics["ece_calibrated"] = expected_calibration_error(
            y_true=y_true,
            y_pred=calibrated_eval["y_pred"],
            confidences=calibrated_eval["confidences"],
            n_bins=n_bins,
        )
        metrics["temperature"] = float(temperature)
        _save_calibration_probs(run_dir=run_dir, probs_calib=probs_calib, labels_calib=labels_calib_codes)

    # Generate reliability diagram
    correctness = [1 if t == p else 0 for t, p in zip(y_true, y_pred, strict=True)]
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
    if "temperature" in metrics:
        metadata["temperature"] = metrics["temperature"]
        metadata["calibration_method"] = calibration_method
        metadata["calibration_sample_size"] = calibration_sample_size
    save_metadata(run_dir, metadata)

    return run_id


def _infer_dataset_source(config: dict, path_or_hf_id: str | None) -> str:
    """Infer dataset source for provenance metadata."""
    if path_or_hf_id and Path(path_or_hf_id).exists():
        return str(path_or_hf_id)
    if path_or_hf_id:
        revision = config.get("dataset", {}).get("hf_revision")
        if revision:
            return f"hf://{path_or_hf_id}@{revision}"
        return f"hf://{path_or_hf_id}"
    dataset_id = config.get("dataset", {}).get("dataset_id", "unknown")
    return f"{dataset_id}_tiny"


def _prediction_probs(*, predictions: list[dict]) -> list[dict]:
    return [dict(row["probabilities"]) for row in predictions]


def _preds_and_conf_from_probs(*, probs: list[dict], task: str) -> dict:
    code_to_label = {v: k for k, v in get_label_codes(task).items()}
    y_pred = []
    confidences = []
    for row in probs:
        pred_code = max(row, key=row.get)
        y_pred.append(code_to_label[pred_code])
        confidences.append(float(row[pred_code]))
    return {"y_pred": y_pred, "confidences": confidences}


def _load_calibration_probabilities(
    *,
    config: dict,
    model,
    tokenizer,
    task: str,
    template_id: str,
    config_dir: str | None,
    sample_size: int,
) -> tuple[list[dict], list[str]]:
    dataset_cfg = config.get("dataset", {})
    splits_cfg = dataset_cfg.get("splits") or {}
    val_split = splits_cfg.get("val", "validation")
    cal_frac = float(splits_cfg.get("calibration_fraction", 0.15))

    examples_val = _load_dataset_examples(
        dataset_cfg,
        sample_size=None,
        split=val_split,
    )
    partitioned = make_calibration_split(
        examples_val,
        seed=42,
        calibration_fraction=cal_frac,
    )
    examples_calib = partitioned["calibration"]
    if sample_size is not None and len(examples_calib) > int(sample_size):
        examples_calib = examples_calib[: int(sample_size)]
    outputs_calib = run_eval(
        model=model,
        tokenizer=tokenizer,
        dataset=examples_calib,
        template_id=template_id,
        task=task,
        config_dir=config_dir,
        run_generation_sanity_check=False,
    )
    label_to_code = get_label_codes(task)
    probs_calib = [dict(row["probabilities"]) for row in outputs_calib["predictions"]]
    labels_calib = [label_to_code[label] for label in outputs_calib["y_true"]]
    return probs_calib, labels_calib


def _save_calibration_probs(*, run_dir: Path, probs_calib: list[dict], labels_calib: list[str]) -> None:
    path = run_dir / "calibration_probs.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for i in range(len(probs_calib)):
            row = {"index": i, "true_code": labels_calib[i], "probabilities": probs_calib[i]}
            f.write(json.dumps(row) + "\n")
