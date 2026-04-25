#!/usr/bin/env python3
"""Validate BioMistral tokenizer single-token encodings for class codes A–E (and MedNLI A–C)."""

from __future__ import annotations

import sys
from pathlib import Path


def _encode_info(tokenizer, text: str) -> tuple[list[int], int]:
    ids = tokenizer.encode(text, add_special_tokens=False)
    return ids, len(ids)


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root / "src"))

    try:
        from transformers import AutoTokenizer
    except ImportError as e:
        print(f"ERROR: transformers not installed: {e}", file=sys.stderr)
        return 1

    try:
        tokenizer = AutoTokenizer.from_pretrained("BioMistral/BioMistral-7B")
    except Exception as e:
        print(f"ERROR: could not load tokenizer: {e!r}", file=sys.stderr)
        return 1

    from reliability_eval.models.tokenizer_utils import get_code_token_ids

    variants_template = ("{}", " {}", "\n{}", "Answer: {}")

    print("=== Per-code tokenization (PubMed A–E) ===")
    for code in ("A", "B", "C", "D", "E"):
        print(f"-- code {code} --")
        for tmpl in variants_template:
            t = tmpl.format(code)
            ids, n = _encode_info(tokenizer, t)
            print(f"  {t!r} -> ids={ids} (n={n})")

    try:
        pubmed_ids = get_code_token_ids(tokenizer, task="pubmed_rct")
    except ValueError as e:
        print(f"ERROR: get_code_token_ids(pubmed): {e}", file=sys.stderr)
        return 1

    print("get_code_token_ids(pubmed_rct):", pubmed_ids)
    if len(pubmed_ids) != 5 or len(set(pubmed_ids)) != 5:
        print("ERROR: expected 5 distinct token ids for PubMed", file=sys.stderr)
        return 1

    print("=== Per-code tokenization (MedNLI A–C) ===")
    for code in ("A", "B", "C"):
        for tmpl in variants_template:
            t = tmpl.format(code)
            ids, n = _encode_info(tokenizer, t)
            print(f"  {t!r} -> ids={ids} (n={n})")

    try:
        med_ids = get_code_token_ids(tokenizer, task="mednli")
    except ValueError as e:
        print(f"ERROR: get_code_token_ids(mednli): {e}", file=sys.stderr)
        return 1

    print("get_code_token_ids(mednli):", med_ids)
    if len(med_ids) != 3 or len(set(med_ids)) != 3:
        print("ERROR: expected 3 distinct token ids for MedNLI", file=sys.stderr)
        return 1

    print("VALIDATE_LABEL_CODES_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
