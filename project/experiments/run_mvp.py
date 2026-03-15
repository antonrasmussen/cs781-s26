#!/usr/bin/env python3
"""Run one tiny end-to-end MVP artifact-producing PubMed experiment.

This is intentionally local, thin, and mock-inference-based.
TODO: Replace mock inference with real BioMistral scoring.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

src = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src))

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


def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore
    except Exception:
        # Fallback defaults are used when PyYAML is unavailable.
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _resolve_mvp_config(project_root: Path, sample_size: int, template_id: str) -> dict:
    base_cfg = _load_yaml(project_root / "configs" / "base.yaml") or {
        "seed": 42,
        "artifact_root": "artifacts/runs",
        "evaluation": {"ece_bins": 15},
    }
    sweep_cfg = _load_yaml(project_root / "configs" / "sweeps" / "mvp_pubmed.yaml") or {
        "experiment_name": "mvp_pubmed_reliability",
        "output": {"artifact_root": "artifacts/runs"},
    }
    dataset_cfg = _load_yaml(project_root / "configs" / "datasets" / "pubmed_rct.yaml") or {
        "dataset_id": "pubmed_rct",
        "task": "pubmed_rct",
        "path_or_hf_id": "",
    }
    model_cfg = _load_yaml(project_root / "configs" / "models" / "biomistral_7b.yaml") or {
        "model_id": "biomistral_7b",
        "name_or_path": "BioMistral/BioMistral-7B",
    }
    precision_cfg = _load_yaml(project_root / "configs" / "precisions" / "fp16.yaml") or {
        "precision": "fp16"
    }

    artifact_root = os.environ.get(
        "RELIABILITY_ARTIFACT_ROOT",
        sweep_cfg.get("output", {}).get("artifact_root", base_cfg.get("artifact_root", "artifacts/runs")),
    )
    return {
        "experiment_name": sweep_cfg.get("experiment_name", "mvp_pubmed_reliability"),
        "seed": base_cfg.get("seed", 42),
        "task": "pubmed_rct",
        "dataset": dataset_cfg,
        "model": model_cfg,
        "precision": precision_cfg,
        "template_id": template_id,
        "sample_size": sample_size,
        "artifact_root": artifact_root,
        "evaluation": base_cfg.get("evaluation", {}),
        "mode": "mock_inference",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run tiny PubMed MVP slice.")
    parser.add_argument("--sample-size", type=int, default=8, help="Number of examples from tiny sample.")
    parser.add_argument("--template-id", type=str, default="pubmed_t1", choices=["pubmed_t1", "pubmed_t2"])
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    config = _resolve_mvp_config(project_root, sample_size=args.sample_size, template_id=args.template_id)
    run_id = make_run_id(prefix="mvp_pubmed")
    run_dir = ensure_run_dir(config["artifact_root"], run_id)

    dataset_path = config["dataset"].get("path_or_hf_id")
    examples = load_pubmed_rct(path_or_hf_id=dataset_path, split="test", sample_size=config["sample_size"])

    label_codes = get_label_codes("pubmed_rct")
    predictions = []
    y_true = []
    y_pred = []
    confidences = []

    for ex in examples:
        prompt = render(
            template_id=config["template_id"],
            task="pubmed_rct",
            text=ex["text"],
            label_codes=label_codes,
        )
        mock = mock_score_example(
            prompt=prompt,
            task="pubmed_rct",
            example_id=ex["example_id"],
            true_label=ex["label"],
        )
        y_true.append(ex["label"])
        y_pred.append(mock["predicted_label"])
        confidences.append(float(mock["confidence"]))
        predictions.append(
            {
                "example_id": ex["example_id"],
                "text": ex["text"],
                "true_label": ex["label"],
                "template_id": config["template_id"],
                "prompt": prompt,
                "predicted_label": mock["predicted_label"],
                "predicted_code": mock["predicted_code"],
                "confidence": mock["confidence"],
                "probabilities": mock["probabilities"],
            }
        )

    metrics = compute_metrics(y_true=y_true, y_pred=y_pred)
    metrics["ece"] = expected_calibration_error(
        y_true=y_true,
        y_pred=y_pred,
        confidences=confidences,
        n_bins=int(config["evaluation"].get("ece_bins", 15)),
    )

    correctness = [1 if t == p else 0 for t, p in zip(y_true, y_pred)]
    figure_path = run_dir / "figures" / "reliability.png"
    plot_reliability(
        confidences=confidences,
        correctness=correctness,
        n_bins=int(config["evaluation"].get("ece_bins", 15)),
        path=str(figure_path),
    )

    save_resolved_config(run_dir, config)
    save_predictions(run_dir, predictions)
    save_metrics(run_dir, metrics)

    metadata = create_manifest(run_id=run_id, config=config)
    metadata["n_examples"] = len(examples)
    metadata["figure"] = str(figure_path)
    metadata["mode"] = config.get("mode", "unknown")
    metadata["dataset_source"] = "pubmed_rct_tiny"  # MVP uses in-repo sample
    save_metadata(run_dir, metadata)

    print(str(run_dir))
    print(json.dumps({"run_id": run_id, "n_examples": len(examples), "ece": metrics["ece"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
