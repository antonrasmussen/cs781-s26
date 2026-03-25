#!/usr/bin/env python3
"""Run full config grid (e.g. 3 precisions x 2 tasks x 5 templates).

Thin wrapper over reliability_eval.experiments.run_single and expand_sweep.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

src = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src))

from reliability_eval.experiments.run_grid import expand_sweep
from reliability_eval.experiments.run_single import run_single


def main() -> int:
    parser = argparse.ArgumentParser(description="Run sweep grid (local harness).")
    parser.add_argument("--sweep", type=str, default="mvp_pubmed", help="Sweep config id")
    parser.add_argument("--profile", type=str, default="local", choices=["local", "flyte_sandbox", "odu"])
    parser.add_argument("--sample-size", type=int, default=None, help="Cap examples per run")
    parser.add_argument("--dry-run", action="store_true", help="Only expand configs, do not run")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    configs = expand_sweep(
        project_root,
        args.sweep,
        execution_profile=args.profile,
        sample_size=args.sample_size,
    )

    if args.dry_run:
        print(f"Would run {len(configs)} configs")
        for i, cfg in enumerate(configs):
            print(f"  {i+1}: {cfg.get('precision', {}).get('precision')} / {cfg.get('template_id')}")
        return 0

    run_ids = []
    for config in configs:
        run_id = run_single(config=config)
        run_ids.append(run_id)
        print(run_id)

    print(f"Completed {len(run_ids)} runs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
