"""Reliability diagram plotting for MVP."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Sequence

from reliability_eval.metrics.calibration import reliability_bins


def _write_placeholder_png(path: Path) -> None:
    # 1x1 transparent PNG fallback when matplotlib is unavailable.
    png = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8"
        "/x8AAusB9Y9n7QAAAABJRU5ErkJggg=="
    )
    path.write_bytes(base64.b64decode(png))


def plot_reliability(
    confidences: Sequence[float],
    correctness: Sequence[int],
    n_bins: int = 15,
    path: str | None = None,
):
    """Plot and optionally save a basic reliability diagram."""
    bins = reliability_bins(confidences, correctness, n_bins=n_bins)
    xs = [0.5 * (b["left"] + b["right"]) for b in bins]
    ys = [b["avg_accuracy"] for b in bins]

    if path is None:
        return {"x": xs, "y": ys, "bins": bins}

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError:
        _write_placeholder_png(out)
        return {"x": xs, "y": ys, "bins": bins}

    plt.figure(figsize=(5, 5))
    plt.plot([0, 1], [0, 1], linestyle="--", linewidth=1, color="gray", label="Perfect")
    plt.plot(xs, ys, marker="o", linewidth=1.5, label="Model")
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.xlabel("Confidence")
    plt.ylabel("Accuracy")
    plt.title("Reliability Diagram")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(out, dpi=120)
    plt.close()
    return {"x": xs, "y": ys, "bins": bins}
