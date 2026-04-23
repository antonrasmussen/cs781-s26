"""Run evaluation over dataset with given template and precision.

TODO: Batch inference; deterministic (temperature=0); save predictions.
"""

from __future__ import annotations

import warnings

from reliability_eval.inference.score_class_codes import score_example
from reliability_eval.models.tokenizer_utils import get_code_token_ids
from reliability_eval.prompting.label_codes import get_label_codes
from reliability_eval.prompting.render import render


def run_eval(
    model,
    tokenizer,
    dataset,
    *,
    template_id: str,
    task: str,
    config_dir: str | None = None,
    run_generation_sanity_check: bool = False,
):
    """Run inference over dataset and return rows + metric vectors."""
    label_codes = get_label_codes(task)
    code_token_ids = get_code_token_ids(tokenizer, task=task)
    if run_generation_sanity_check:
        _sanity_check_first_token_alignment(
            model=model,
            tokenizer=tokenizer,
            dataset=dataset,
            template_id=template_id,
            task=task,
            label_codes=label_codes,
            code_token_ids=code_token_ids,
            config_dir=config_dir,
        )

    predictions = []
    y_true = []
    y_pred = []
    confidences = []

    for ex in dataset:
        prompt = render(
            template_id=template_id,
            task=task,
            text=ex["text"],
            label_codes=label_codes,
            config_dir=config_dir,
        )
        result = score_example(
            model=model,
            tokenizer=tokenizer,
            prompt=prompt,
            code_token_ids=code_token_ids,
            task=task,
        )

        y_true.append(ex["label"])
        y_pred.append(result["predicted_label"])
        confidences.append(float(result["confidence"]))
        predictions.append(
            {
                "example_id": ex["example_id"],
                "text": ex["text"],
                "true_label": ex["label"],
                "template_id": template_id,
                "prompt": prompt,
                "predicted_label": result["predicted_label"],
                "predicted_code": result["predicted_code"],
                "confidence": result["confidence"],
                "probabilities": result["probabilities"],
            }
        )

    return {
        "predictions": predictions,
        "y_true": y_true,
        "y_pred": y_pred,
        "confidences": confidences,
    }


def _sanity_check_first_token_alignment(
    *,
    model,
    tokenizer,
    dataset,
    template_id: str,
    task: str,
    label_codes: dict,
    code_token_ids: list[int],
    config_dir: str | None,
) -> None:
    """Compare restricted-logit argmax with 1-token greedy generation."""
    try:
        import torch
    except ImportError:
        return
    subset = list(dataset[: min(5, len(dataset))])
    if not subset:
        return
    id_to_code = {token_id: code for code, token_id in zip(sorted(label_codes.values()), code_token_ids, strict=True)}
    mismatches = 0
    for ex in subset:
        prompt = render(
            template_id=template_id,
            task=task,
            text=ex["text"],
            label_codes=label_codes,
            config_dir=config_dir,
        )
        inputs = tokenizer(prompt, return_tensors="pt")
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.inference_mode():
            logits = model(**inputs).logits[0, -1, :]
            pred_token_id = int(code_token_ids[int(torch.argmax(logits[code_token_ids]).item())])
            generated = model.generate(
                **inputs,
                do_sample=False,
                max_new_tokens=1,
                pad_token_id=tokenizer.eos_token_id,
            )
            generated_token_id = int(generated[0, -1].item())
        if generated_token_id in id_to_code and generated_token_id != pred_token_id:
            mismatches += 1
    if mismatches:
        warnings.warn(
            f"Found {mismatches} first-token alignment mismatches in quick sanity check",
            UserWarning,
            stacklevel=2,
        )
