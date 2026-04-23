"""Tokenizer helpers: resolve label codes to token IDs.

Selects a consistent tokenization strategy for class codes by probing both plain
letters (``A``) and space-prefixed letters (`` A``).
"""

from __future__ import annotations

from reliability_eval.prompting.label_codes import get_label_codes


def _encode_single_token_id(tokenizer, token_text: str) -> int:
    token_ids = tokenizer.encode(token_text, add_special_tokens=False)
    if len(token_ids) != 1:
        raise ValueError(
            f"Expected single token for {token_text!r}, got ids={token_ids}"
        )
    return int(token_ids[0])


def get_code_token_ids(tokenizer, task: str) -> list[int]:
    """Return ordered class-code token IDs for ``task``.

    Order is lexical by code letter (e.g., A..E for PubMed).
    """
    label_to_code = get_label_codes(task)
    codes = sorted(set(label_to_code.values()))
    if not codes:
        raise ValueError(f"No label codes found for task={task!r}")

    variants = ("{}", " {}")
    best_ids: list[int] | None = None
    best_variant: str | None = None

    for variant in variants:
        try:
            ids = [_encode_single_token_id(tokenizer, variant.format(code)) for code in codes]
        except ValueError:
            continue
        if len(set(ids)) != len(ids):
            continue
        best_ids = ids
        best_variant = variant
        break

    if best_ids is None or best_variant is None:
        raise ValueError(
            f"Could not find a single-token encoding variant for task={task!r} codes={codes!r}"
        )
    return best_ids
