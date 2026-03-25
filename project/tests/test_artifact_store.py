"""Tests for artifact path helpers."""

import pytest

from reliability_eval.io.artifact_store import ensure_run_dir


def test_ensure_run_dir_creates_figures(tmp_path):
    run_dir = ensure_run_dir(str(tmp_path), "run_safe_1")
    assert run_dir.is_dir()
    assert (run_dir / "figures").is_dir()


def test_ensure_run_dir_rejects_path_traversal(tmp_path):
    with pytest.raises(ValueError, match="path separators"):
        ensure_run_dir(str(tmp_path), "a/b")


def test_ensure_run_dir_rejects_parent_segments(tmp_path):
    with pytest.raises(ValueError, match=r"\.\."):
        ensure_run_dir(str(tmp_path), "..")
