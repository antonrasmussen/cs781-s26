"""Run metadata manifest helpers."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone


def create_manifest(run_id: str, config: dict) -> dict:
    """Build minimal run metadata manifest."""
    config_str = json.dumps(config, sort_keys=True)
    config_hash = hashlib.sha256(config_str.encode("utf-8")).hexdigest()[:12]
    return {
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "config_hash": config_hash,
    }
