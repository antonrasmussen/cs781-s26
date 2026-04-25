#!/usr/bin/env python3
"""Run one tiny end-to-end MVP artifact-producing PubMed experiment.

Thin wrapper over reliability_eval.experiments.run_single.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

src = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src))

from reliability_eval.config.resolve import resolve_mvp_config
from reliability_eval.experiments.run_single import run_single
from reliability_eval.io.paths import make_run_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Run tiny PubMed MVP slice.")
    parser.add_argument("--sample-size", type=int, default=8, help="Number of examples from tiny sample.")
    parser.add_argument("--template-id", type=str, default="pubmed_t1", choices=["pubmed_t1", "pubmed_t2"])
    parser.add_argument(
        "--profile",
        type=str,
        default="local",
        choices=["local", "local_real", "flyte_sandbox", "odu"],
    )
    parser.add_argument(
        "--calibration",
        type=str,
        default="none",
        choices=["none", "temperature_scaling", "isotonic"],
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    config = resolve_mvp_config(
        project_root,
        sample_size=args.sample_size,
        template_id=args.template_id,
        execution_profile=args.profile,
    )
    config["calibration"] = {"calibration": args.calibration}
    run_id = make_run_id(prefix="mvp_pubmed")

    run_id = run_single(config=config, run_id=run_id)

    run_dir = Path(config["artifact_root"]) / run_id
    print(str(run_dir))

    # Load metrics for summary output
    metrics_path = run_dir / "metrics.json"
    if metrics_path.exists():
        with metrics_path.open("r", encoding="utf-8") as f:
            metrics = json.load(f)
        print(json.dumps({"run_id": run_id, "n_examples": metrics.get("n_examples", 0), "ece": metrics.get("ece")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
