#!/usr/bin/env python3
"""Build final metrics tables, hypothesis tests, and figures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from reliability_eval.experiments.aggregate import aggregate_metrics
from reliability_eval.metrics.ace import adaptive_calibration_error
from reliability_eval.metrics.bootstrap import bootstrap_ci
from reliability_eval.metrics.calibration import expected_calibration_error_from_confidence, reliability_bins
from reliability_eval.metrics.paired_tests import paired_bootstrap_ci, recovery_ratio
from reliability_eval.metrics.prompt_stability import fleiss_kappa_bootstrap_ci


def _read_predictions(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _metrics_with_ci(rows: list[dict]) -> dict:
    y_true = [r["true_label"] for r in rows]
    y_pred = [r["predicted_label"] for r in rows]
    conf = [float(r["confidence"]) for r in rows]
    correctness = [1 if t == p else 0 for t, p in zip(y_true, y_pred, strict=True)]
    acc = sum(correctness) / len(correctness)
    labels = sorted(set(y_true) | set(y_pred))
    per_class = {}
    for label in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred, strict=True) if t == label and p == label)
        fp = sum(1 for t, p in zip(y_true, y_pred, strict=True) if t != label and p == label)
        fn = sum(1 for t, p in zip(y_true, y_pred, strict=True) if t == label and p != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        per_class[label] = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    macro_f1 = sum(per_class.values()) / len(per_class)
    ece = expected_calibration_error_from_confidence(confidences=conf, correctness=correctness, n_bins=15)
    ace = adaptive_calibration_error(confidences=conf, correctness=correctness, n_bins=15)
    return {
        "accuracy": acc,
        "macro_f1": macro_f1,
        "ece": ece,
        "ace": ace,
        "accuracy_ci": bootstrap_ci(correctness, lambda xs: sum(xs) / len(xs), n_resamples=1000, seed=42),
        "macro_f1_ci": bootstrap_ci(
            list(range(len(y_true))),
            lambda idxs: _macro_f1_from_indices(y_true, y_pred, idxs),
            n_resamples=1000,
            seed=42,
        ),
        "ece_ci": bootstrap_ci(
            list(range(len(y_true))),
            lambda idxs: expected_calibration_error_from_confidence(
                confidences=[conf[i] for i in idxs],
                correctness=[correctness[i] for i in idxs],
                n_bins=15,
            ),
            n_resamples=1000,
            seed=42,
        ),
        "per_class_f1": per_class,
    }


def _macro_f1_from_indices(y_true: list[str], y_pred: list[str], idxs: list[int]) -> float:
    t = [y_true[i] for i in idxs]
    p = [y_pred[i] for i in idxs]
    labels = sorted(set(t) | set(p))
    vals = []
    for label in labels:
        tp = sum(1 for yy, pp in zip(t, p, strict=True) if yy == label and pp == label)
        fp = sum(1 for yy, pp in zip(t, p, strict=True) if yy != label and pp == label)
        fn = sum(1 for yy, pp in zip(t, p, strict=True) if yy == label and pp != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        vals.append((2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0)
    return sum(vals) / len(vals)


def _format_table(rows: list[dict]) -> str:
    headers = [
        "run_id",
        "precision",
        "template_id",
        "n_examples",
        "accuracy",
        "macro_f1",
        "ece",
        "ace",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        vals = []
        for key in headers:
            value = row.get(key, "")
            if isinstance(value, float):
                vals.append(f"{value:.6f}")
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines) + "\n"


def _plot_reliability(rows: list[dict], artifact_root: Path, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError:
        out_path.write_bytes(b"")
        return
    fig, axes = plt.subplots(1, max(1, len(rows)), figsize=(5 * max(1, len(rows)), 4), squeeze=False)
    for i, row in enumerate(rows):
        pred_rows = _read_predictions(artifact_root / row["run_id"] / "predictions.jsonl")
        conf = [float(r["confidence"]) for r in pred_rows]
        corr = [1 if r["true_label"] == r["predicted_label"] else 0 for r in pred_rows]
        bins = reliability_bins(conf, corr, n_bins=15)
        xs = [0.5 * (b["left"] + b["right"]) for b in bins]
        ys = [b["avg_accuracy"] for b in bins]
        ax = axes[0, i]
        ax.plot([0, 1], [0, 1], linestyle="--", linewidth=1, color="gray")
        ax.plot(xs, ys, marker="o", linewidth=1.5)
        ax.set_title(f"{row['run_id']}\n{row['precision']}")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel("Confidence")
        ax.set_ylabel("Accuracy")
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_recovery(rows: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError:
        out_path.write_bytes(b"")
        return
    by_prec: dict[str, list[float]] = {}
    for row in rows:
        by_prec.setdefault(row["precision"], []).append(float(row["ece"]))
    names = sorted(by_prec.keys())
    vals = [sum(v) / len(v) for v in (by_prec[n] for n in names)]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(names, vals, marker="o")
    ax.set_xlabel("Precision")
    ax.set_ylabel("ECE")
    ax.set_title("ECE trajectory by precision")
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close(fig)


def _hypothesis_rows(rows: list[dict], artifact_root: Path) -> str:
    by_key = {(r["precision"], r["template_id"]): r for r in rows}
    all_precisions = sorted({r["precision"] for r in rows})
    all_templates = sorted({r["template_id"] for r in rows})
    total_cells = len(all_precisions) * len(all_templates)
    completed_cells = len(rows)

    deltas: list[float] = []
    compared_pairs: list[str] = []
    for template in all_templates:
        fp16 = by_key.get(("fp16", template))
        int4 = by_key.get(("int4", template))
        if fp16 is None or int4 is None:
            continue
        d_ece = abs(float(int4["ece"]) - float(fp16["ece"]))
        d_f1 = abs(float(fp16["macro_f1"]) - float(int4["macro_f1"]))
        deltas.append(d_ece - d_f1)
        compared_pairs.append(template)
    primary = paired_bootstrap_ci(deltas, n_resamples=1000, seed=42) if deltas else None

    int4_templates = sorted({r["template_id"] for r in rows if r["precision"] == "int4"})
    int4_incomplete = len(int4_templates) < len(all_templates)

    lines = ["# Hypothesis Tests", ""]

    # Matrix completeness note
    lines.append(
        f"Matrix completeness note: computed from the finalized partial `n=2000` matrix "
        f"(`{completed_cells}/{total_cells}` cells)."
    )
    missing_parts: list[str] = []
    for prec in all_precisions:
        missing_templates = sorted(t for t in all_templates if (prec, t) not in by_key)
        if missing_templates:
            missing_parts.append(f"`{prec} / {', '.join(missing_templates)}`")
    if missing_parts:
        lines.append(f"Missing cells are {' and '.join(missing_parts)} due to runtime failures.")
    lines.append("")

    lines.append("## Primary: |Delta_ECE| > |Delta_F1| at INT4 vs FP16")
    lines.append("- Statistic: `(|Delta_ECE| - |Delta_F1|)` (absolute deltas, per preregistration)")
    if primary is None:
        lines.append("- Insufficient FP16/INT4 template pairs.")
    else:
        lines.append(
            f"- point={primary['point']:.6f}, ci=[{primary['ci_low']:.6f}, {primary['ci_high']:.6f}]"
        )
        pair_labels = [f"`int4 / {t}` vs `fp16 / {t}`" for t in compared_pairs]
        if len(pair_labels) == 1:
            pairs_str = pair_labels[0]
        elif len(pair_labels) == 2:
            pairs_str = f"{pair_labels[0]} and {pair_labels[1]}"
        else:
            pairs_str = ", ".join(pair_labels[:-1]) + ", and " + pair_labels[-1]
        if primary["ci_low"] > 0:
            outcome = (
                f"**supported** for the completed comparison ({pairs_str}) "
                "because the CI is positive and excludes 0."
            )
        elif primary["ci_high"] < 0:
            outcome = (
                f"**not supported** for the completed comparison ({pairs_str}) "
                "because the CI is negative."
            )
        else:
            outcome = (
                f"**inconclusive** for the completed comparison ({pairs_str}) "
                "because the CI crosses 0."
            )
        lines.append(f"- Decision (available evidence): {outcome}")
        if int4_incomplete:
            n_int4 = len(int4_templates)
            lines.append(
                f"- Caveat: only {n_int4} INT4 template{'s' if n_int4 != 1 else ''} completed "
                "at `n=2000`; treat this as conditional support under partial matrix completeness."
            )

    lines.append("")
    lines.append("## Secondary: temperature scaling recovery <= 110% FP16 ECE")
    has_calibrated = any(r.get("ece_calibrated") is not None for r in rows)
    if has_calibrated:
        lines.append("- Reported via recovery ratios where calibrated runs exist.")
        for row in rows:
            if row.get("ece_calibrated") is None:
                continue
            fp16 = by_key.get(("fp16", row["template_id"]))
            if not fp16:
                continue
            try:
                ratio = recovery_ratio(
                    ece_uncal=float(row["ece"]),
                    ece_cal=float(row["ece_calibrated"]),
                    ece_fp16=float(fp16["ece"]),
                )
                lines.append(f"- {row['run_id']}: recovery_ratio={ratio:.6f}")
            except Exception:
                continue
    else:
        lines.append(
            "- Decision: **not evaluated** on the `n=2000` matrix because post-hoc calibrated "
            "counterparts were not generated for the finalized 10-run evidence set."
        )

    lines.append("")
    lines.append("## Tertiary: Fleiss' kappa degradation and non-recovery")
    template_groups: dict[str, list[tuple[str, list[str]]]] = {}
    for row in rows:
        pred_rows = _read_predictions(artifact_root / row["run_id"] / "predictions.jsonl")
        template_groups.setdefault(row["precision"], []).append(
            (row["template_id"], [r["predicted_label"] for r in pred_rows])
        )
    for precision, group in sorted(template_groups.items()):
        if len(group) < 2:
            continue
        group = sorted(group, key=lambda x: x[0])
        kappa_ci = fleiss_kappa_bootstrap_ci([preds for _, preds in group], n_resamples=1000, seed=42)
        lines.append(
            f"- {precision}: kappa={kappa_ci['point']:.6f}, "
            f"ci=[{kappa_ci['ci_low']:.6f}, {kappa_ci['ci_high']:.6f}]"
        )
    if int4_incomplete:
        lines.append(
            "- Decision: **descriptive only**. INT4 lacks template-complete coverage on `n=2000`, "
            "so the preregistered INT4-vs-FP16 non-recovery claim cannot be formally tested."
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build final report artifacts from runs.")
    parser.add_argument("--artifact-root", default="artifacts/runs")
    parser.add_argument(
        "--run-id",
        action="append",
        default=None,
        help="Optional run id filter (repeat flag for multiple runs)",
    )
    parser.add_argument("--expected-count", type=int, default=None)
    parser.add_argument("--table-out", default="reports/final_metrics.md")
    parser.add_argument("--hypothesis-out", default="reports/hypothesis_tests.md")
    parser.add_argument("--reliability-fig-out", default="reports/figures/reliability_by_precision.png")
    parser.add_argument("--recovery-fig-out", default="reports/figures/recovery_plot.png")
    args = parser.parse_args()

    artifact_root = Path(args.artifact_root)
    payload = aggregate_metrics(
        str(artifact_root),
        run_ids=args.run_id,
        expected_count=args.expected_count,
    )
    rows = payload["runs"]
    enriched = []
    for row in rows:
        pred_rows = _read_predictions(artifact_root / row["run_id"] / "predictions.jsonl")
        metrics = _metrics_with_ci(pred_rows)
        row = dict(row)
        row["accuracy"] = metrics["accuracy"]
        row["macro_f1"] = metrics["macro_f1"]
        row["ece"] = metrics["ece"]
        row["ace"] = metrics["ace"]
        row["macro_f1_ci"] = metrics["macro_f1_ci"]
        row["ece_ci"] = metrics["ece_ci"]
        row["per_class_f1"] = metrics["per_class_f1"]
        enriched.append(row)

    table_path = Path(args.table_out)
    table_path.parent.mkdir(parents=True, exist_ok=True)
    table_path.write_text(_format_table(enriched), encoding="utf-8")

    hyp_path = Path(args.hypothesis_out)
    hyp_path.parent.mkdir(parents=True, exist_ok=True)
    hyp_path.write_text(_hypothesis_rows(enriched, artifact_root), encoding="utf-8")

    _plot_reliability(enriched, artifact_root, Path(args.reliability_fig_out))
    _plot_recovery(enriched, Path(args.recovery_fig_out))

    print(f"wrote table: {table_path}")
    print(f"wrote hypothesis tests: {hyp_path}")
    print(f"wrote figure: {args.reliability_fig_out}")
    print(f"wrote figure: {args.recovery_fig_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
