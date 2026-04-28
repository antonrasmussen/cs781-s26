#!/usr/bin/env python3
"""Live progress monitor for final_pubmed matrix runs."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import yaml


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _expected_cells() -> list[tuple[str, str]]:
    precisions = ["fp16", "int8", "int4"]
    templates = ["pubmed_t1", "pubmed_t2", "pubmed_t3", "pubmed_t4", "pubmed_t5"]
    return [(p, t) for p in precisions for t in templates]


def _scan_runs(artifact_root: Path, sample_size: int) -> tuple[dict, list[str]]:
    complete: dict[tuple[str, str], str] = {}
    in_progress: list[str] = []
    if not artifact_root.exists():
        return complete, in_progress

    for run_dir in sorted([p for p in artifact_root.iterdir() if p.is_dir()]):
        cfg_path = run_dir / "resolved_config.yaml"
        meta_path = run_dir / "metadata.json"
        metrics_path = run_dir / "metrics.json"
        preds_path = run_dir / "predictions.jsonl"
        if not cfg_path.exists():
            if run_dir.name.startswith("final_pubmed_reliabi") and preds_path.exists():
                in_progress.append(run_dir.name)
            continue
        cfg = _load_yaml(cfg_path)
        if cfg.get("experiment_name") != "final_pubmed_reliability":
            continue
        if int(cfg.get("sample_size", 0)) != int(sample_size):
            continue

        precision = cfg.get("precision", {}).get("precision", "unknown")
        template = cfg.get("template_id", "unknown")
        key = (precision, template)

        if meta_path.exists() and metrics_path.exists():
            meta = _load_json(meta_path)
            if meta.get("inference_mode") == "real_inference":
                complete[key] = run_dir.name
            continue

        if preds_path.exists():
            in_progress.append(run_dir.name)

    return complete, in_progress


def _render(artifact_root: Path, sample_size: int) -> str:
    expected = _expected_cells()
    complete, in_progress = _scan_runs(artifact_root, sample_size)
    done = len(complete)
    total = len(expected)
    pending = [cell for cell in expected if cell not in complete]

    lines = []
    lines.append(f"artifact_root: {artifact_root}")
    lines.append(f"sample_size: {sample_size}")
    lines.append(f"progress: {done}/{total} complete")
    if pending:
        lines.append("pending_cells:")
        for precision, template in pending:
            lines.append(f"  - {precision} / {template}")
    else:
        lines.append("pending_cells: none")
    if in_progress:
        lines.append("in_progress_run_dirs:")
        for run_id in in_progress:
            lines.append(f"  - {run_id}")
    else:
        lines.append("in_progress_run_dirs: none")
    lines.append("")
    lines.append("completed_cells:")
    for precision, template in expected:
        run_id = complete.get((precision, template))
        if run_id:
            lines.append(f"  - {precision} / {template}: {run_id}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor matrix progress from artifact directories.")
    parser.add_argument("--artifact-root", default="artifacts/runs")
    parser.add_argument("--sample-size", type=int, default=2000)
    parser.add_argument("--watch", type=int, default=0, help="Refresh interval seconds (0 = one-shot)")
    args = parser.parse_args()

    artifact_root = Path(args.artifact_root)
    if args.watch <= 0:
        print(_render(artifact_root, args.sample_size))
        return 0

    try:
        while True:
            print("=" * 80)
            print(time.strftime("%Y-%m-%d %H:%M:%S"))
            print(_render(artifact_root, args.sample_size))
            time.sleep(args.watch)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
