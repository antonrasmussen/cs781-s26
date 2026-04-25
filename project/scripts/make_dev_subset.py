#!/usr/bin/env python3
"""Build deterministic stratified 200-example dev subset from PubMed RCT test split."""

from __future__ import annotations

import hashlib
import json
import random
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main() -> int:
    project_root = _project_root()
    sys.path.insert(0, str(project_root / "src"))

    try:
        from datasets import load_dataset
    except ImportError as e:
        print(f"ERROR: datasets not installed: {e}", file=sys.stderr)
        return 1

    hf_id = "armanc/pubmed-rct20k"
    revision = "main"
    try:
        split = load_dataset(hf_id, split="test", revision=revision)
    except Exception as e:
        print(f"ERROR: failed to load test split: {e!r}", file=sys.stderr)
        return 1

    from reliability_eval.data.pubmed_rct import _normalize_record

    by_label: dict[str, list[dict]] = defaultdict(list)
    for idx, record in enumerate(split, start=1):
        text = record.get("text") or record.get("sentence") or ""
        lab = record.get("label_text", record.get("label"))
        try:
            ex = _normalize_record(
                {
                    "example_id": record.get("example_id"),
                    "abstract_id": record.get("abstract_id"),
                    "sentence_id": record.get("sentence_id"),
                    "text": text,
                    "label": lab,
                },
                idx=idx,
            )
        except ValueError as e:
            print(f"WARN: skip row {idx}: {e}", file=sys.stderr)
            continue
        by_label[ex["label"]].append(ex)

    labels = sorted(by_label.keys())
    required = {
        "BACKGROUND",
        "OBJECTIVE",
        "METHODS",
        "RESULTS",
        "CONCLUSIONS",
    }
    if set(labels) != required:
        print(f"ERROR: expected labels {required}, got {set(labels)}", file=sys.stderr)
        return 1

    target_per_class = 40
    seed = 42
    selected: list[dict] = []
    per_class_counts: dict[str, int] = {}

    for lab in sorted(required):
        bucket = by_label[lab][:]
        subseed = seed + int(
            hashlib.sha256(f"{seed}|{lab}".encode("utf-8")).hexdigest()[:8], 16
        )
        random.Random(subseed).shuffle(bucket)
        take = min(target_per_class, len(bucket))
        if take < target_per_class:
            print(
                f"ERROR: class {lab!r} has only {len(bucket)} usable rows; need {target_per_class}.",
                file=sys.stderr,
            )
            return 1
        chosen = bucket[:target_per_class]
        per_class_counts[lab] = len(chosen)
        selected.extend(chosen)

    assert len(selected) == 200

    out_path = project_root / "data" / "samples" / "pubmed_rct_dev200.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for ex in selected:
            f.write(
                json.dumps(
                    {"example_id": ex["example_id"], "text": ex["text"], "label": ex["label"]},
                    ensure_ascii=False,
                )
                + "\n"
            )

    prov_path = project_root / "data" / "samples" / "pubmed_rct_dev200.provenance.json"
    prov = {
        "source": f"hf://{hf_id}@{revision}",
        "split": "test",
        "seed": seed,
        "method": "stratified_40_per_class_after_shuffle_per_class",
        "n_rows": 200,
        "per_class_counts": per_class_counts,
        "created_date_utc": datetime.now(timezone.utc).isoformat(),
        "output_path": str(out_path.relative_to(project_root)),
    }
    prov_path.write_text(json.dumps(prov, indent=2), encoding="utf-8")

    print("DEV200_OK", out_path)
    print(json.dumps(prov, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
