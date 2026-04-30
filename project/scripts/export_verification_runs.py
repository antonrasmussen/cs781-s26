#!/usr/bin/env python3
"""Export a small, tracked verification subset from artifacts/runs.

Usage example:
  python scripts/export_verification_runs.py \
    --run-id final_pubmed_reliabi_20260427T152058_146948Z_a7088d \
    --run-id final_pubmed_reliabi_20260428T142308_358498Z_334b78 \
    --predictions-limit 200
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path


def _read_run_ids(path: Path) -> list[str]:
    out: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line)
    return out


def _copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def _copy_predictions_sample(src: Path, dst: Path, limit: int) -> int:
    if not src.exists():
        return 0
    count = 0
    dst.parent.mkdir(parents=True, exist_ok=True)
    with src.open("r", encoding="utf-8") as in_f, dst.open("w", encoding="utf-8") as out_f:
        for line in in_f:
            if not line.strip():
                continue
            out_f.write(line)
            count += 1
            if count >= limit:
                break
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="Export verification subset from artifacts/runs.")
    parser.add_argument(
        "--run-id",
        action="append",
        default=[],
        help="Run ID to export (repeat flag for multiple runs).",
    )
    parser.add_argument(
        "--run-id-file",
        default=None,
        help="Optional text file with one run ID per line.",
    )
    parser.add_argument(
        "--source-root",
        default="artifacts/runs",
        help="Root containing full run artifacts.",
    )
    parser.add_argument(
        "--dest-root",
        default="artifacts/verification_runs",
        help="Destination root for tracked verification subset.",
    )
    parser.add_argument(
        "--predictions-limit",
        type=int,
        default=200,
        help="Number of prediction rows to copy into predictions_sample.jsonl.",
    )
    parser.add_argument(
        "--include-figure",
        action="store_true",
        help="Also copy figures/reliability.png when present.",
    )
    args = parser.parse_args()

    run_ids = list(args.run_id)
    if args.run_id_file:
        run_ids.extend(_read_run_ids(Path(args.run_id_file)))
    run_ids = sorted(set(run_ids))

    if not run_ids:
        raise SystemExit("No run IDs provided. Use --run-id and/or --run-id-file.")
    if args.predictions_limit <= 0:
        raise SystemExit("--predictions-limit must be > 0.")

    source_root = Path(args.source_root)
    dest_root = Path(args.dest_root)
    dest_root.mkdir(parents=True, exist_ok=True)

    summary: dict[str, object] = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source_root": str(source_root),
        "dest_root": str(dest_root),
        "predictions_limit": args.predictions_limit,
        "run_count": len(run_ids),
        "runs": [],
    }

    for run_id in run_ids:
        src_dir = source_root / run_id
        if not src_dir.exists():
            raise SystemExit(f"Run not found: {src_dir}")
        dst_dir = dest_root / run_id
        dst_dir.mkdir(parents=True, exist_ok=True)

        copied = {
            "run_id": run_id,
            "copied_files": [],
            "prediction_rows_copied": 0,
        }

        for name in ("metadata.json", "metrics.json", "resolved_config.yaml"):
            if _copy_if_exists(src_dir / name, dst_dir / name):
                copied["copied_files"].append(name)

        copied["prediction_rows_copied"] = _copy_predictions_sample(
            src=src_dir / "predictions.jsonl",
            dst=dst_dir / "predictions_sample.jsonl",
            limit=args.predictions_limit,
        )
        if copied["prediction_rows_copied"] > 0:
            copied["copied_files"].append("predictions_sample.jsonl")

        if _copy_if_exists(src_dir / "calibration_probs.jsonl", dst_dir / "calibration_probs_sample.jsonl"):
            copied["copied_files"].append("calibration_probs_sample.jsonl")

        if args.include_figure and _copy_if_exists(
            src_dir / "figures" / "reliability.png",
            dst_dir / "figures" / "reliability.png",
        ):
            copied["copied_files"].append("figures/reliability.png")

        summary["runs"].append(copied)

    manifest_path = dest_root / "manifest.json"
    manifest_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"wrote {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
