"""Path conventions for runs and artifacts."""

from __future__ import annotations

from datetime import datetime


def artifact_root(base: str = "artifacts/runs") -> str:
    """Return artifact root directory."""
    return base


def make_run_id(prefix: str = "mvp_pubmed") -> str:
    """Create a timestamped run identifier."""
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{ts}"
