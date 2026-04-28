#!/usr/bin/env python3
"""Apply post-hoc calibration to an existing run directory."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import yaml

from reliability_eval.calibration.apply import apply_calibration
from reliability_eval.calibration.temperature_scaling import fit_temperature
from reliability_eval.data.splits import make_calibration_split
from reliability_eval.experiments.run_single import _load_dataset_examples
from reliability_eval.inference.batch_runner import run_eval
from reliability_eval.io.artifact_store import save_metadata, save_metrics, save_predictions, save_resolved_config
from reliability_eval.metrics.ace import adaptive_calibration_error
from reliability_eval.metrics.calibration import expected_calibration_error
from reliability_eval.metrics.classification import compute_metrics
from reliability_eval.models.load_model import load_biomistral
from reliability_eval.prompting.label_codes import get_label_codes


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _prediction_probs(rows: list[dict]) -> list[dict]:
    return [dict(r["probabilities"]) for r in rows]


def _preds_from_probs(*, probs: list[dict], task: str) -> tuple[list[str], list[float]]:
    code_to_label = {v: k for k, v in get_label_codes(task).items()}
    y_pred = []
    conf = []
    for row in probs:
        code = max(row, key=row.get)
        y_pred.append(code_to_label[code])
        conf.append(float(row[code]))
    return y_pred, conf


def _fit_temperature_from_validation(
    *,
    config: dict,
    task: str,
    template_id: str,
    sample_size: int,
) -> tuple[float, list[dict], list[str]]:
    dataset_cfg = config.get("dataset", {})
    splits_cfg = dataset_cfg.get("splits") or {}
    val_split = splits_cfg.get("val", "validation")
    cal_frac = float(splits_cfg.get("calibration_fraction", 0.15))
    examples_val = _load_dataset_examples(dataset_cfg, sample_size=None, split=val_split)
    partitioned = make_calibration_split(examples_val, seed=42, calibration_fraction=cal_frac)
    examples_calib = partitioned["calibration"]
    if sample_size is not None and len(examples_calib) > int(sample_size):
        examples_calib = examples_calib[: int(sample_size)]

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
        dataset=examples_calib,
        template_id=template_id,
        task=task,
        config_dir=config.get("config_dir"),
        run_generation_sanity_check=False,
    )
    probs_calib = [dict(row["probabilities"]) for row in outputs["predictions"]]
    label_to_code = get_label_codes(task)
    labels_calib = [label_to_code[label] for label in outputs["y_true"]]
    temperature = fit_temperature(probs_calib=probs_calib, labels_calib=labels_calib)
    return float(temperature), probs_calib, labels_calib


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply calibration to an existing run.")
    parser.add_argument("--run-dir", required=True, help="Path to an existing run directory")
    parser.add_argument(
        "--method",
        default="temperature_scaling",
        choices=["temperature_scaling"],
        help="Calibration method",
    )
    parser.add_argument(
        "--calibration-sample-size",
        type=int,
        default=None,
        help="Optional cap for calibration-set examples",
    )
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")

    cfg = yaml.safe_load((run_dir / "resolved_config.yaml").read_text(encoding="utf-8")) or {}
    pred_rows = _read_jsonl(run_dir / "predictions.jsonl")
    parent_meta = _read_json(run_dir / "metadata.json")
    task = cfg.get("task", "pubmed_rct")
    template_id = cfg.get("template_id", "pubmed_t1")

    probs_test = _prediction_probs(pred_rows)
    y_true = [row["true_label"] for row in pred_rows]
    sample_size = args.calibration_sample_size or int(cfg.get("calibration_sample_size", len(pred_rows)))
    temperature, probs_calib, labels_calib = _fit_temperature_from_validation(
        config=cfg,
        task=task,
        template_id=template_id,
        sample_size=sample_size,
    )
    calibrated_probs = apply_calibration(
        probs_test,
        args.method,
        calibrator_params={"temperature": temperature},
    )
    y_pred_cal, conf_cal = _preds_from_probs(probs=calibrated_probs, task=task)
    metrics = compute_metrics(y_true=y_true, y_pred=y_pred_cal)
    metrics["ece"] = expected_calibration_error(y_true=y_true, y_pred=y_pred_cal, confidences=conf_cal, n_bins=15)
    correctness = [1 if t == p else 0 for t, p in zip(y_true, y_pred_cal, strict=True)]
    metrics["ace"] = adaptive_calibration_error(confidences=conf_cal, correctness=correctness, n_bins=15)
    metrics["temperature"] = temperature

    new_run_id = f"{run_dir.name}_cal_temp"
    new_run_dir = run_dir.parent / new_run_id
    new_run_dir.mkdir(parents=True, exist_ok=True)
    (new_run_dir / "figures").mkdir(exist_ok=True)

    cfg["calibration"] = {"calibration": args.method}
    save_resolved_config(new_run_dir, cfg)
    save_predictions(new_run_dir, pred_rows)
    save_metrics(new_run_dir, metrics)

    cal_path = new_run_dir / "calibration_probs.jsonl"
    with cal_path.open("w", encoding="utf-8") as f:
        for i in range(len(probs_calib)):
            f.write(json.dumps({"index": i, "true_code": labels_calib[i], "probabilities": probs_calib[i]}) + "\n")

    metadata = dict(parent_meta)
    metadata["run_id"] = new_run_id
    metadata["parent_run_id"] = run_dir.name
    metadata["calibration_method"] = args.method
    metadata["temperature"] = temperature
    save_metadata(new_run_dir, metadata)
    print(str(new_run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
