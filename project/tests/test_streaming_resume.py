from __future__ import annotations

import json
from pathlib import Path

import pytest

from reliability_eval.config.resolve import resolve_mvp_config
from reliability_eval.experiments.run_single import run_single


def _count_jsonl(path: Path) -> int:
    with path.open("r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def test_streaming_and_resume_after_interrupted_mock_run(tmp_path, monkeypatch):
    from reliability_eval.experiments import run_single as run_single_mod

    project_root = Path(__file__).resolve().parent.parent
    config = resolve_mvp_config(project_root, sample_size=6, template_id="pubmed_t1")
    config["artifact_root"] = str(tmp_path / "runs")
    run_id = "resume_mock_test"

    original = run_single_mod.mock_score_example
    calls = {"n": 0}

    def flaky_mock_score_example(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 4:
            raise RuntimeError("injected failure")
        return original(*args, **kwargs)

    monkeypatch.setattr(run_single_mod, "mock_score_example", flaky_mock_score_example)
    with pytest.raises(RuntimeError, match="injected failure"):
        run_single(config=config, run_id=run_id)

    run_dir = Path(config["artifact_root"]) / run_id
    pred_path = run_dir / "predictions.jsonl"
    assert pred_path.exists()
    assert _count_jsonl(pred_path) == 3

    monkeypatch.setattr(run_single_mod, "mock_score_example", original)
    run_single(config=config, run_id=run_id)
    assert _count_jsonl(pred_path) == 6
    with (run_dir / "metrics.json").open("r", encoding="utf-8") as f:
        metrics = json.load(f)
    assert metrics["n_examples"] == 6
