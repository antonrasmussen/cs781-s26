"""Path conventions for runs and artifacts."""

from __future__ import annotations

import secrets
from datetime import datetime, timezone


def artifact_root(base: str = "artifacts/runs") -> str:
    """Return artifact root directory."""
    return base


def make_run_id(prefix: str = "mvp_pubmed") -> str:
    """Create a timestamped run identifier (UTC, sub-second + random suffix)."""
    now = datetime.now(timezone.utc)
    stem = now.strftime("%Y%m%dT%H%M%S_%fZ")
    suffix = secrets.token_hex(3)
    return f"{prefix}_{stem}_{suffix}"
