#!/usr/bin/env python3
"""Run a single experiment from a resolved config (local harness).

Thin wrapper over reliability_eval.experiments.run_single.

Run with the package on ``PYTHONPATH`` (repository ``src`` layout), for example::

    PYTHONPATH=src python experiments/run_local.py

From the project root after ``pip install -e ".[dev]"``, ``python -m pytest`` uses
``pyproject.toml``'s ``pythonpath``; for this script, set ``PYTHONPATH=src`` explicitly.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from reliability_eval.config.resolve import resolve_config
from reliability_eval.experiments.run_single import run_single


def main() -> int:
    parser = argparse.ArgumentParser(description="Run single experiment (local harness).")
    parser.add_argument("--sweep", type=str, default="mvp_pubmed", help="Sweep config id")
    parser.add_argument("--dataset", type=str, default="pubmed_rct")
    parser.add_argument("--model", type=str, default="biomistral_7b")
    parser.add_argument("--precision", type=str, default="fp16")
    parser.add_argument("--template", type=str, default="pubmed_t1")
    parser.add_argument("--calibration", type=str, default="none")
    parser.add_argument("--profile", type=str, default="local", choices=["local", "flyte_sandbox", "odu"])
    parser.add_argument("--sample-size", type=int, default=None, help="Cap examples for small runs")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    config = resolve_config(
        project_root,
        sweep_id=args.sweep,
        dataset_id=args.dataset,
        model_id=args.model,
        precision_id=args.precision,
        template_id=args.template,
        calibration_id=args.calibration,
        execution_profile=args.profile,
        sample_size=args.sample_size,
    )

    run_id = run_single(config=config)
    print(run_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
