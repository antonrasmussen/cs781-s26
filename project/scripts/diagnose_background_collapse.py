#!/usr/bin/env python3
"""Reproduce BACKGROUND-collapse diagnostics (restricted logits at last prompt token)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _load_tiny_examples() -> list[dict]:
    p = _project_root() / "data" / "samples" / "pubmed_rct_tiny.jsonl"
    out = []
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def _legend_perm_background_last() -> str:
    """List BACKGROUND last (A still first in sorted-by-code order — use custom order)."""
    return (
        "B=OBJECTIVE C=METHODS D=RESULTS E=CONCLUSIONS A=BACKGROUND"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default="BioMistral/BioMistral-7B",
        help="HF model id (full forward pass; requires torch + enough RAM/VRAM).",
    )
    parser.add_argument("--device", default=None, help="e.g. cuda, cpu (default: auto pick)")
    args = parser.parse_args()

    project_root = _project_root()
    sys.path.insert(0, str(project_root / "src"))

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as e:
        print(f"ERROR: torch/transformers required: {e}", file=sys.stderr)
        return 1

    from reliability_eval.inference.score_class_codes import score_example
    from reliability_eval.models.tokenizer_utils import get_code_token_ids
    from reliability_eval.prompting.label_codes import get_label_codes
    from reliability_eval.prompting.render import render

    config_dir = str(project_root / "configs")

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    code_ids = get_code_token_ids(tokenizer, task="pubmed_rct")
    print("code_token_ids (ordered A..E):", code_ids)

    device = args.device
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        model = AutoModelForCausalLM.from_pretrained(
            args.model,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            low_cpu_mem_usage=True,
        )
        model.to(device)
        model.eval()
    except Exception as e:
        print(f"ERROR: model load failed: {e!r}", file=sys.stderr)
        return 1

    tiny = _load_tiny_examples()
    label_codes = get_label_codes("pubmed_rct")

    scenarios = [
        ("default_legend", None),
        ("background_last_inline_legend", _legend_perm_background_last()),
    ]

    for name, legend_override in scenarios:
        print(f"\n########## SCENARIO: {name} ##########")
        for row in tiny:
            text = str(row.get("text", "")).strip()
            prompt = render(
                template_id="pubmed_t1",
                task="pubmed_rct",
                text=text,
                label_codes=label_codes,
                config_dir=config_dir,
                legend_override=legend_override,
            )
            inputs = tokenizer(prompt, return_tensors="pt")
            input_ids = inputs["input_ids"]
            print("---", row.get("example_id"), "true_label=", row.get("label"))
            print("  input_ids shape:", tuple(input_ids.shape))
            tail = input_ids[0, -8:].tolist()
            print("  last 8 input_ids:", tail)
            print("  last 8 tokens:", tokenizer.convert_ids_to_tokens(tail))

            with torch.inference_mode():
                out = model(**{k: v.to(device) for k, v in inputs.items()})
                last_logits = out.logits[0, -1, :]
                sel = last_logits[code_ids].float().cpu()
                probs = torch.softmax(sel, dim=-1).tolist()
            print("  restricted logits (A..E):", [round(float(x), 4) for x in sel.tolist()])
            print("  restricted softmax:", {c: round(p, 6) for c, p in zip("ABCDE", probs)})

            scored = score_example(
                model=model,
                tokenizer=tokenizer,
                prompt=prompt,
                code_token_ids=code_ids,
                task="pubmed_rct",
            )
            print("  score_example:", scored["predicted_code"], scored["confidence"])

    print("\nDIAGNOSE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
