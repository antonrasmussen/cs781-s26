"""End-to-end test for the tiny MVP runner."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_mvp_runner_creates_artifacts(tmp_path):
    project_root = Path(__file__).resolve().parent.parent
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root / "src")
    env["RELIABILITY_ARTIFACT_ROOT"] = str(tmp_path / "runs")

    cmd = [sys.executable, "experiments/run_mvp.py", "--sample-size", "6", "--template-id", "pubmed_t1"]
    completed = subprocess.run(
        cmd,
        cwd=str(project_root),
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    run_dir = Path(lines[0])
    assert run_dir.exists()
    assert (run_dir / "resolved_config.yaml").exists()
    assert (run_dir / "metadata.json").exists()
    assert (run_dir / "predictions.jsonl").exists()
    assert (run_dir / "metrics.json").exists()
    assert (run_dir / "figures" / "reliability.png").exists()
