"""Load BioMistral-7B at specified precision."""

from __future__ import annotations

from pathlib import Path

from reliability_eval.models.quantization import (
    assert_quantized_footprint,
    build_quantization_config,
)


def load_biomistral(
    precision: str,
    *,
    name_or_path: str = "BioMistral/BioMistral-7B",
    revision: str | None = None,
    device_map: str = "auto",
):
    """Load model+tokenizer pair.

    Returns:
        Tuple ``(model, tokenizer)``.
    """
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as e:  # pragma: no cover - environment dependent
        raise ImportError(
            "Missing GPU dependencies. Install with `pip install -e .[gpu]`."
        ) from e

    precision_key = str(precision).lower()
    tokenizer = AutoTokenizer.from_pretrained(name_or_path, revision=revision)
    offload_folder = Path(".hf-offload")
    offload_folder.mkdir(parents=True, exist_ok=True)

    if precision_key == "fp16":
        model = AutoModelForCausalLM.from_pretrained(
            name_or_path,
            revision=revision,
            torch_dtype=torch.float16,
            device_map=device_map,
            offload_folder=str(offload_folder),
            use_safetensors=False,
        )
        first_dtype = next(model.parameters()).dtype
        if first_dtype != torch.float16:
            raise RuntimeError(
                f"Expected fp16 model dtype, got {first_dtype} for precision={precision}"
            )
        model.eval()
        return model, tokenizer

    if precision_key in {"int8", "int4"}:
        bnb_config = build_quantization_config(precision_key)
        fp16_reference_bytes = None
        if precision_key == "int8":
            # Lightweight FP16 estimate for 7B-class models (~2 bytes/param).
            fp16_reference_bytes = int(7_000_000_000 * 2)
        model = AutoModelForCausalLM.from_pretrained(
            name_or_path,
            revision=revision,
            device_map=device_map,
            quantization_config=bnb_config,
            offload_folder=str(offload_folder),
            use_safetensors=False,
        )
        assert_quantized_footprint(
            model,
            precision=precision_key,
            fp16_reference_bytes=fp16_reference_bytes,
        )
        model.eval()
        return model, tokenizer

    raise ValueError(f"Unsupported precision: {precision!r}")
