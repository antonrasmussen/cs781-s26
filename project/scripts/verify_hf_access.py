#!/usr/bin/env python3
"""Verify Hugging Face access to armanc/pubmed-rct20k (10 test rows only)."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    try:
        from datasets import load_dataset
    except ImportError as e:
        print("ERROR: `datasets` is not installed.", file=sys.stderr)
        print("Install with: pip install 'datasets>=2.18' pyarrow", file=sys.stderr)
        print(e, file=sys.stderr)
        return 1

    hf_id = "armanc/pubmed-rct20k"
    revision = "main"
    try:
        ds = load_dataset(hf_id, split="test[:10]", revision=revision)
    except Exception as e:
        print(f"ERROR: load_dataset failed: {e!r}", file=sys.stderr)
        return 1

    n = len(ds)
    if n != 10:
        print(f"ERROR: expected 10 rows, got {n}", file=sys.stderr)
        return 1

    # Reject accidental tiny in-repo fixture (8 rows, synthetic "Background:" prefixes)
    first = dict(ds[0])
    keys = list(first.keys())
    print("HF_ACCESS_OK")
    print("field_names:", keys)
    print("first_record_raw:", json.dumps(first, default=str)[:2000])

    # Optional normalization preview (may import project src)
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root / "src"))
    try:
        from reliability_eval.data.pubmed_rct import _normalize_record

        norm = _normalize_record(
            {
                "example_id": first.get("example_id"),
                "abstract_id": first.get("abstract_id"),
                "sentence_id": first.get("sentence_id"),
                "text": first.get("text") or first.get("sentence") or "",
                "label": first.get("label_text", first.get("label")),
            },
            idx=1,
        )
        print("first_record_normalized:", json.dumps(norm))
    except Exception as e:
        print(f"normalize_preview_failed: {e!r}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
