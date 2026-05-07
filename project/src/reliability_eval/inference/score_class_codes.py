"""Scoring utilities for class-code probabilities: real model inference via restricted softmax, and a deterministic mock path for testing."""

from __future__ import annotations

import hashlib
import random
from typing import Dict, Optional

from reliability_eval.prompting.label_codes import get_code_to_label


def score_example(
    model,
    tokenizer,
    prompt: str,
    code_token_ids: list,
    *,
    task: str = "pubmed_rct",
):
    """Score one prompt via restricted softmax over class-code token logits."""
    try:
        import torch
    except ImportError as e:  # pragma: no cover - environment dependent
        raise ImportError("torch is required for real model scoring") from e

    inputs = tokenizer(prompt, return_tensors="pt")
    device = next(model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.inference_mode():
        outputs = model(**inputs)
        last_token_logits = outputs.logits[0, -1, :]
        selected = last_token_logits[code_token_ids]
        probs = torch.softmax(selected, dim=-1)

    code_to_label = get_code_to_label(task)
    codes = sorted(code_to_label.keys())
    prob_values = probs.detach().float().cpu().tolist()
    probabilities = {
        code: float(p) for code, p in zip(codes, prob_values, strict=True)
    }
    predicted_code = max(probabilities, key=probabilities.get)
    return {
        "predicted_label": code_to_label[predicted_code],
        "predicted_code": predicted_code,
        "probabilities": probabilities,
        "confidence": float(probabilities[predicted_code]),
    }


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
