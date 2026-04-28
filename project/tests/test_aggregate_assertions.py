import json
from pathlib import Path

import pytest

from reliability_eval.experiments.aggregate import aggregate_metrics


def _write_min_run(root: Path, run_id: str) -> None:
    run_dir = root / run_id
    (run_dir / "figures").mkdir(parents=True, exist_ok=True)
    (run_dir / "resolved_config.yaml").write_text(
        "precision:\n  precision: fp16\ntemplate_id: pubmed_t1\n",
        encoding="utf-8",
    )
    (run_dir / "metadata.json").write_text(
        json.dumps({"inference_mode": "real_inference", "n_examples": 2}),
        encoding="utf-8",
    )
    (run_dir / "metrics.json").write_text(
        json.dumps({"accuracy": 1.0, "macro_f1": 1.0, "ece": 0.0}),
        encoding="utf-8",
    )


def test_aggregate_expected_count_passes(tmp_path):
    _write_min_run(tmp_path, "run_a")
    payload = aggregate_metrics(str(tmp_path), expected_count=1)
    assert payload["n_runs"] == 1


def test_aggregate_expected_count_raises(tmp_path):
    _write_min_run(tmp_path, "run_a")
    with pytest.raises(ValueError, match="Expected 2 aggregated runs"):
        aggregate_metrics(str(tmp_path), expected_count=2)
