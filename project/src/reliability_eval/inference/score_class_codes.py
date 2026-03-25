"""Scoring for class-code probabilities.

This file contains a temporary mock inference path for MVP.
"""

from __future__ import annotations

import hashlib
import random
from typing import Dict, Optional

from reliability_eval.prompting.label_codes import get_code_to_label


def score_example(model, tokenizer, prompt: str, code_token_ids: list):
    """Real model scoring path (not implemented yet).

    TODO: Replace mock path with BioMistral logits extraction.
    """
    _ = (model, tokenizer, prompt, code_token_ids)
    raise NotImplementedError("TODO: implement real score_example with model logits")


def mock_score_example(
    prompt: str,
    task: str,
    example_id: str,
    true_label: Optional[str] = None,
) -> Dict:
    """Return deterministic mock prediction and probabilities for MVP wiring.

    Output shape intentionally mirrors future real inference artifacts.
    """
    code_to_label = get_code_to_label(task)
    codes = sorted(code_to_label.keys())

    seed_src = f"{example_id}|{prompt}".encode("utf-8")
    seed = int(hashlib.sha256(seed_src).hexdigest()[:16], 16)
    rng = random.Random(seed)

    raw = {code: rng.random() + 0.01 for code in codes}
    if true_label is not None:
        label_to_code = {v: k for k, v in code_to_label.items()}
        if true_label in label_to_code:
            raw[label_to_code[true_label]] += 0.35

    total = sum(raw.values())
    probabilities = {code: value / total for code, value in raw.items()}
    predicted_code = max(probabilities, key=probabilities.get)
    predicted_label = code_to_label[predicted_code]
    confidence = probabilities[predicted_code]

    return {
        "predicted_label": predicted_label,
        "predicted_code": predicted_code,
        "probabilities": probabilities,
        "confidence": confidence,
    }
