"""End-to-end test for the tiny MVP runner."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# Subprocess guard: MVP runner should finish quickly; avoids hung CI
TIMEOUT_SEC = 120

# Required provenance fields in metadata.json (artifact contract)
REQUIRED_METADATA_KEYS = [
    "run_id",
    "created_at_utc",
    "config_hash",
    "execution_mode",
    "compute_env",
    "code_version",
    "dataset_source",
    "inference_mode",
    "n_examples",
    "figure",
]


def test_mvp_runner_creates_artifacts(tmp_path):
    project_root = Path(__file__).resolve().parent.parent
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root / "src")
    env["RELIABILITY_ARTIFACT_ROOT"] = str(tmp_path / "runs")

    cmd = [sys.executable, "experiments/run_mvp.py", "--sample-size", "6", "--template-id", "pubmed_t1"]
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(project_root),
            env=env,
            capture_output=True,
            text=True,
            check=True,
            timeout=TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired as e:
        raise AssertionError(f"MVP runner timed out after {TIMEOUT_SEC}s") from e

    lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    assert lines, (
        "MVP runner produced no stdout lines; "
        f"stderr={completed.stderr!r}"
    )
    run_dir = Path(lines[0])
    assert run_dir.exists()
    assert (run_dir / "resolved_config.yaml").exists()
    assert (run_dir / "metadata.json").exists()
    assert (run_dir / "predictions.jsonl").exists()
    assert (run_dir / "metrics.json").exists()
    assert (run_dir / "figures" / "reliability.png").exists()


def test_metadata_has_required_provenance_fields(tmp_path):
    """Artifact contract: metadata.json must include all provenance fields."""
    project_root = Path(__file__).resolve().parent.parent
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root / "src")
    env["RELIABILITY_ARTIFACT_ROOT"] = str(tmp_path / "runs")

    try:
        subprocess.run(
            [sys.executable, "experiments/run_mvp.py", "--sample-size", "4", "--template-id", "pubmed_t2"],
            cwd=str(project_root),
            env=env,
            capture_output=True,
            text=True,
            check=True,
            timeout=TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired as e:
        raise AssertionError(f"MVP runner timed out after {TIMEOUT_SEC}s") from e

    run_dirs = list((tmp_path / "runs").iterdir())
    assert len(run_dirs) >= 1
    metadata_path = run_dirs[0] / "metadata.json"
    assert metadata_path.exists()

    with metadata_path.open("r", encoding="utf-8") as f:
        metadata = json.load(f)

    for key in REQUIRED_METADATA_KEYS:
        assert key in metadata, f"metadata.json missing required key: {key}"

    assert metadata["execution_mode"] == "local"
    assert metadata["inference_mode"] == "mock_inference"
    assert metadata["dataset_source"] in {
        "pubmed_rct_tiny",
        "hf://armanc/pubmed-rct20k@main",
    }


def test_flyte_task_produces_same_artifact_structure_as_run_single(tmp_path):
    """Parity: Flyte task path produces same artifact structure as plain run_single."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

    from reliability_eval.config.resolve import resolve_mvp_config
    from reliability_eval.experiments.run_single import run_single
    from reliability_eval.flyte.tasks import run_single_task
    from reliability_eval.io.paths import make_run_id

    project_root = Path(__file__).resolve().parent.parent
    config = resolve_mvp_config(project_root, sample_size=4, template_id="pubmed_t1")
    config["artifact_root"] = str(tmp_path / "runs")
    config["execution_mode"] = "flyte_sandbox"
    config["compute_env"] = "flyte_sandbox"

    # Run via plain run_single
    run_id_plain = make_run_id(prefix="parity_plain")
    run_single(config=config, run_id=run_id_plain)

    # Run via Flyte task (thin wrapper; same code path when flytekit not installed)
    run_id_flyte = make_run_id(prefix="parity_flyte")
    run_single_task(config=config, run_id=run_id_flyte)

    # Both should produce identical artifact structure
    for run_id in (run_id_plain, run_id_flyte):
        run_dir = tmp_path / "runs" / run_id
        assert run_dir.exists()
        assert (run_dir / "resolved_config.yaml").exists()
        assert (run_dir / "metadata.json").exists()
        assert (run_dir / "predictions.jsonl").exists()
        assert (run_dir / "metrics.json").exists()
        assert (run_dir / "figures" / "reliability.png").exists()

        with (run_dir / "metadata.json").open("r") as f:
            meta = json.load(f)
        for key in REQUIRED_METADATA_KEYS:
            assert key in meta, f"Flyte path missing {key}"
