#!/usr/bin/env python3
"""Build minimal Milestone 3 table + reliability figure from real runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from reliability_eval.experiments.aggregate import aggregate_metrics
from reliability_eval.metrics.calibration import reliability_bins
from reliability_eval.reporting.tables import metrics_table


def _run_rows(artifact_root: Path, run_ids: list[str] | None) -> list[dict]:
    payload = aggregate_metrics(str(artifact_root), run_ids=run_ids)
    return payload["runs"]


def _write_metrics_table(rows: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(metrics_table(rows), encoding="utf-8")


def _plot_reliability(rows: list[dict], artifact_root: Path, out_path: Path, n_bins: int = 15) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError:
        out_path.write_bytes(b"")
        return

    fig, axes = plt.subplots(1, max(1, len(rows)), figsize=(5 * max(1, len(rows)), 4), squeeze=False)
    for idx, row in enumerate(rows):
        run_id = row["run_id"]
        pred_path = artifact_root / run_id / "predictions.jsonl"
        confidences = []
        correctness = []
        with pred_path.open("r", encoding="utf-8") as f:
            for line in f:
                ex = json.loads(line)
                confidences.append(float(ex["confidence"]))
                correctness.append(1 if ex["true_label"] == ex["predicted_label"] else 0)
        bins = reliability_bins(confidences, correctness, n_bins=n_bins)
        xs = [0.5 * (b["left"] + b["right"]) for b in bins]
        ys = [b["avg_accuracy"] for b in bins]
        ax = axes[0, idx]
        ax.plot([0, 1], [0, 1], linestyle="--", linewidth=1, color="gray")
        ax.plot(xs, ys, marker="o", linewidth=1.5)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ece = row.get("ece")
        ece_text = f"{float(ece):.3f}" if isinstance(ece, (int, float)) else "na"
        ax.set_title(f"{run_id}\n{row['precision']} ece={ece_text}")
        ax.set_xlabel("Confidence")
        ax.set_ylabel("Accuracy")

    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Milestone 3 summary artifacts.")
    parser.add_argument(
        "--artifact-root",
        default="artifacts/runs",
        help="Root directory containing run artifacts",
    )
    parser.add_argument(
        "--run-id",
        action="append",
        default=None,
        help="Optional run id filter (repeat flag for multiple runs)",
    )
    parser.add_argument("--table-out", default="reports/m3_metrics.md")
    parser.add_argument("--figure-out", default="reports/figures/m3_reliability.png")
    args = parser.parse_args()

    artifact_root = Path(args.artifact_root)
    rows = _run_rows(artifact_root, args.run_id)
    _write_metrics_table(rows, Path(args.table_out))
    _plot_reliability(rows, artifact_root, Path(args.figure_out))
    print(f"wrote table: {args.table_out}")
    print(f"wrote figure: {args.figure_out}")
    print(f"rows: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
