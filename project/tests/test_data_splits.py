"""Tests for deterministic calibration splits from validation."""

from __future__ import annotations

from reliability_eval.data.splits import make_calibration_split


def _make_examples(n: int) -> list[dict]:
    return [{"example_id": f"ex_{i}", "text": f"t{i}", "label": "BACKGROUND"} for i in range(n)]


def test_make_calibration_split_determinism():
    examples = _make_examples(100)
    a = make_calibration_split(examples, seed=42, calibration_fraction=0.15)
    b = make_calibration_split(examples, seed=42, calibration_fraction=0.15)
    assert a["calibration"] == b["calibration"]
    assert a["remaining_val"] == b["remaining_val"]


def test_make_calibration_split_different_seed():
    examples = _make_examples(100)
    a = make_calibration_split(examples, seed=42, calibration_fraction=0.15)
    b = make_calibration_split(examples, seed=99, calibration_fraction=0.15)
    assert a["calibration"] != b["calibration"] or a["remaining_val"] != b["remaining_val"]


def test_make_calibration_split_fraction_and_partition():
    examples = _make_examples(200)
    out = make_calibration_split(examples, seed=42, calibration_fraction=0.15)
    cal = out["calibration"]
    rem = out["remaining_val"]
    k = int(200 * 0.15)
    assert len(cal) == k
    assert len(rem) == 200 - k
    cal_ids = {ex["example_id"] for ex in cal}
    rem_ids = {ex["example_id"] for ex in rem}
    assert cal_ids.isdisjoint(rem_ids)
    assert cal_ids | rem_ids == {f"ex_{i}" for i in range(200)}


def test_make_calibration_split_preserves_within_split_order():
    """Indices in each split are sorted ascending → original row order preserved."""
    examples = [{"example_id": f"ex_{i}", "text": "x", "label": "BACKGROUND"} for i in range(30)]
    out = make_calibration_split(examples, seed=7, calibration_fraction=0.2)
    cal_ids = [ex["example_id"] for ex in out["calibration"]]
    rem_ids = [ex["example_id"] for ex in out["remaining_val"]]
    assert cal_ids == sorted(cal_ids, key=lambda s: int(s.split("_")[1]))
    assert rem_ids == sorted(rem_ids, key=lambda s: int(s.split("_")[1]))


def test_make_calibration_split_no_test_leakage_documented():
    """Partition is purely a function of its input list — caller must pass val only."""
    val_only = _make_examples(50)
    out = make_calibration_split(val_only, seed=42, calibration_fraction=0.15)
    assert len(out["calibration"]) + len(out["remaining_val"]) == 50


def test_make_calibration_split_empty():
    assert make_calibration_split([], seed=42) == {"calibration": [], "remaining_val": []}
