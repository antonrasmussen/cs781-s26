#!/usr/bin/env python3
"""Download PubMed 20k RCT from Hugging Face and write provenance JSON."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _normalize_one(record: dict, idx: int) -> dict:
    sys.path.insert(0, str(_project_root() / "src"))
    from reliability_eval.data.pubmed_rct import _normalize_record

    text = record.get("text") or record.get("sentence") or ""
    lab = record.get("label_text", record.get("label"))
    return _normalize_record(
        {
            "example_id": record.get("example_id"),
            "abstract_id": record.get("abstract_id"),
            "sentence_id": record.get("sentence_id"),
            "text": text,
            "label": lab,
        },
        idx=idx,
    )


def main() -> int:
    provenance_path = _project_root() / "data" / "provenance" / "pubmed_rct_download.json"
    provenance_path.parent.mkdir(parents=True, exist_ok=True)

    base = {
        "dataset_id": "armanc/pubmed-rct20k",
        "hf_revision": "main",
        "download_date_utc": datetime.now(timezone.utc).isoformat(),
        "split_sizes": {},
        "field_names_observed": [],
        "status": "unknown",
        "error": None,
    }

    try:
        from datasets import load_dataset
    except ImportError as e:
        base["status"] = "blocked"
        base["error"] = f"ImportError: {e}"
        provenance_path.write_text(json.dumps(base, indent=2), encoding="utf-8")
        print(json.dumps(base, indent=2))
        return 1

    try:
        dsd = load_dataset("armanc/pubmed-rct20k", revision="main")
    except Exception as e:
        base["status"] = "blocked"
        base["error"] = repr(e)
        provenance_path.write_text(json.dumps(base, indent=2), encoding="utf-8")
        print(json.dumps(base, indent=2))
        return 1

    split_sizes = {}
    samples = {}
    all_keys: set[str] = set()

    for split_name in dsd.keys():
        split = dsd[split_name]
        n = split.num_rows if hasattr(split, "num_rows") else len(split)
        split_sizes[split_name] = int(n)
        raw0 = dict(split[0])
        all_keys.update(raw0.keys())
        samples[split_name] = [
            _normalize_one(dict(split[i]), idx=i + 1) for i in range(min(2, n))
        ]

    base["split_sizes"] = split_sizes
    base["field_names_observed"] = sorted(all_keys)
    base["status"] = "ok"
    base["samples_normalized_first_two_per_split"] = samples

    provenance_path.write_text(json.dumps(base, indent=2), encoding="utf-8")

    print("DOWNLOAD_OK")
    print("provenance:", provenance_path)
    for k, v in split_sizes.items():
        print(f"  split {k!r}: {v} rows")
    for k, rows in samples.items():
        print(f"--- {k} (normalized sample) ---")
        for row in rows:
            print(json.dumps(row))

    # Guard: do not mistake tiny fixture for full dataset
    if split_sizes.get("test", 0) <= 10:
        print("WARNING: test split unusually small; verify HF mirror.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
