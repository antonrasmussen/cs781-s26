#!/usr/bin/env python3
"""Dataset audit (split counts, label distributions, @-mask, token lengths, cal split balance)."""

from __future__ import annotations

import random
import sys
from collections import Counter
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

    from reliability_eval.data.pubmed_rct import _normalize_record
    from reliability_eval.data.splits import make_calibration_split

    hf_id = "armanc/pubmed-rct20k"
    revision = "main"

    try:
        dsd = load_dataset(hf_id, revision=revision)
    except Exception as e:
        print(f"AUDIT_BLOCKED: {e!r}")
        return 1

    cfg_splits = {"train": "train", "val": "validation", "test": "test"}

    def load_norm(split_key: str) -> list[dict]:
        hf_name = cfg_splits[split_key]
        split = dsd[hf_name]
        out = []
        for idx, record in enumerate(split, start=1):
            text = record.get("text") or record.get("sentence") or ""
            lab = record.get("label_text", record.get("label"))
            try:
                out.append(
                    _normalize_record(
                        {
                            "example_id": str(record.get("example_id", f"pubmed_{idx}")),
                            "text": text,
                            "label": lab,
                        },
                        idx=idx,
                    )
                )
            except ValueError as e:
                print(f"WARN row {idx}: {e}", file=sys.stderr)
        return out

    print("# PubMed 20k RCT audit")
    for sk in ("train", "val", "test"):
        ex = load_norm(sk)
        c = Counter(e["label"] for e in ex)
        n_at = sum(1 for e in ex if "@" in e["text"])
        print(f"## split={sk} n={len(ex)} sentences_with_@={n_at}")
        for lab, k in sorted(c.items()):
            pct = 100.0 * k / len(ex) if ex else 0
            print(f"  {lab}: {k} ({pct:.2f}%)")

    val_examples = load_norm("val")
    part = make_calibration_split(val_examples, seed=42, calibration_fraction=0.15)
    cal = part["calibration"]
    c_val = Counter(e["label"] for e in val_examples)
    c_cal = Counter(e["label"] for e in cal)

    def dist(counter: Counter, n: int) -> dict[str, float]:
        return {lab: 100.0 * counter.get(lab, 0) / n for lab in sorted(c_val.keys())} if n else {}

    print("## calibration_split (15% of val) class % vs full val (target within +/-2 points)")
    for lab in sorted(c_val.keys()):
        pv = dist(c_val, len(val_examples))[lab]
        pc = dist(c_cal, len(cal))[lab] if cal else 0.0
        print(f"  {lab}: val={pv:.2f}% cal={pc:.2f}% delta={abs(pc - pv):.2f}")

    # Token length sample: 100 per class from test (requires transformers)
    try:
        from transformers import AutoTokenizer

        tok = AutoTokenizer.from_pretrained("BioMistral/BioMistral-7B")
    except Exception as e:
        print(f"## token_length_audit SKIPPED: {e!r}")
        return 0

    test_ex = load_norm("test")
    by_lab: dict[str, list[dict]] = {lab: [] for lab in c_val.keys()}
    for e in test_ex:
        by_lab[e["label"]].append(e)

    rng = random.Random(42)
    print("## token_length_sample (n=100/class on test, BioMistral tokenizer)")
    for lab, rows in sorted(by_lab.items()):
        sample = rows[:] if len(rows) <= 100 else rng.sample(rows, 100)
        lengths = [len(tok.encode(s["text"], add_special_tokens=False)) for s in sample]
        lengths.sort()
        p95 = lengths[int(0.95 * (len(lengths) - 1))] if lengths else 0
        over = sum(1 for L in lengths if L > 512)
        print(
            f"  {lab}: mean={sum(lengths)/len(lengths):.1f} max={max(lengths)} "
            f"p95={p95} n>{512}={over}"
        )

    print("AUDIT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
