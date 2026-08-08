"""Tests for claim-consistency and verification-subset validators."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parent.parent


def _run_script(script: Path, argv: list[str]) -> int:
    old = sys.argv
    try:
        sys.argv = argv
        try:
            runpy.run_path(str(script), run_name="__main__")
            return 0
        except SystemExit as exc:
            return int(exc.code) if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    finally:
        sys.argv = old


def test_verify_claim_consistency_passes_on_repo():
    root = _root()
    script = root / "scripts" / "verify_claim_consistency.py"
    code = _run_script(script, [str(script), "--project-root", str(root)])
    assert code == 0
    out = root / "reports" / "diagnostics" / "claim_consistency.md"
    assert out.exists()
    assert "PASS" in out.read_text(encoding="utf-8")


def test_validate_verification_subset_passes_on_repo():
    root = _root()
    script = root / "scripts" / "validate_verification_subset.py"
    code = _run_script(script, [str(script), "--project-root", str(root)])
    assert code == 0
    out = root / "reports" / "diagnostics" / "verification_subset_check.md"
    assert out.exists()
    assert "PASS" in out.read_text(encoding="utf-8")


def test_pinned_revisions_are_commit_shas():
    import yaml

    root = _root()
    ds = yaml.safe_load((root / "configs" / "datasets" / "pubmed_rct.yaml").read_text())
    model = yaml.safe_load((root / "configs" / "models" / "biomistral_7b.yaml").read_text())
    assert ds["hf_revision"] != "main"
    assert len(ds["hf_revision"]) >= 7
    assert model["revision"] != "main"
    assert len(model["revision"]) >= 7


def test_verification_run_ids_file_has_ten_entries():
    root = _root()
    path = root / "reports" / "verification_run_ids.txt"
    ids = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert len(ids) == 10


def test_cli_report_help_lists_builder_flags():
    from reliability_eval.cli import main
    import io
    from contextlib import redirect_stdout

    old = sys.argv
    buf = io.StringIO()
    try:
        sys.argv = ["reliability-eval", "report", "--help"]
        with redirect_stdout(buf):
            try:
                main()
            except SystemExit as exc:
                assert exc.code in (0, None)
    finally:
        sys.argv = old
    text = buf.getvalue()
    assert "--run-id-file" in text
    assert "--artifact-root" in text
