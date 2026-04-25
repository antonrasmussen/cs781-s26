#!/usr/bin/env python3
"""Inspect a run directory for collapse-gate quick checks."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect predictions/metrics for one run directory.")
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        help="Path to run directory (defaults to $RUN_DIR if set).",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    run_dir = args.run_dir or (Path(os.environ["RUN_DIR"]) if "RUN_DIR" in os.environ else None)
    if run_dir is None:
        raise SystemExit("Provide --run-dir or set RUN_DIR")

    rows = [json.loads(line) for line in (run_dir / "predictions.jsonl").open(encoding="utf-8")]
    metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))

    print("run_dir =", run_dir)
    print("inference_mode =", metadata.get("inference_mode"))
    print("n =", len(rows))
    print("gold =", Counter(r["true_label"] for r in rows))
    print("pred =", Counter(r["predicted_label"] for r in rows))
    print("macro_f1 =", metrics.get("macro_f1"))
    print("accuracy =", metrics.get("accuracy"))
    print("ece =", metrics.get("ece"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
