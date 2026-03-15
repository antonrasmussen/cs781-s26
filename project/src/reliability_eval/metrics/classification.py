"""Minimal classification metrics for MVP."""

from typing import Dict, List


def _f1_for_label(y_true: List[str], y_pred: List[str], label: str) -> float:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)
    if tp == 0 and (fp > 0 or fn > 0):
        return 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    if (precision + recall) == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def compute_metrics(y_true, y_pred, y_proba=None) -> Dict:
    """Return accuracy and macro F1 (plus per-class F1 for debugging)."""
    _ = y_proba  # TODO: use y_proba for additional metrics later.
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred length mismatch")
    if not y_true:
        raise ValueError("Empty inputs")

    labels = sorted(set(y_true) | set(y_pred))
    per_class_f1 = {label: _f1_for_label(y_true, y_pred, label) for label in labels}
    macro_f1 = sum(per_class_f1.values()) / len(per_class_f1)
    accuracy = sum(1 for t, p in zip(y_true, y_pred) if t == p) / len(y_true)

    return {
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "per_class_f1": per_class_f1,
        "n_examples": len(y_true),
    }
