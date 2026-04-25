"""Quantization config and application (bitsandbytes).

TODO: INT8 LLM.int8(), INT4 NF4; single backend only.
"""

from __future__ import annotations


def build_quantization_config(mode: str):
    """Build BitsAndBytesConfig for int8/int4 loading."""
    try:
        import torch
        from transformers import BitsAndBytesConfig
    except ImportError as e:  # pragma: no cover - environment dependent
        raise ImportError(
            "Quantized loading requires transformers+bitsandbytes. "
            "Install with `pip install -e .[gpu]`."
        ) from e

    key = str(mode).lower()
    if key == "int8":
        return BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_enable_fp32_cpu_offload=True,
        )
    if key == "int4":
        return BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            llm_int8_enable_fp32_cpu_offload=True,
        )
    raise ValueError(f"Unsupported quantization mode: {mode!r}")


def apply_quantization(model, mode: str):
    """Backward-compatible helper.

    Returns ``model`` unchanged; quantization is applied at load time via
    ``build_quantization_config``.
    """
    _ = mode
    return model


def assert_quantized_footprint(model, *, precision: str, fp16_reference_bytes: int | None = None):
    """Sanity-check quantized model footprint to catch silent FP16 fallback."""
    try:
        footprint = int(model.get_memory_footprint())
    except Exception as e:  # pragma: no cover - model impl dependent
        raise RuntimeError("Could not read model memory footprint for quantization check") from e

    if footprint <= 0:
        raise RuntimeError("Invalid model memory footprint reported for quantized model")

    if precision == "int8" and fp16_reference_bytes is not None:
        # INT8 should be materially smaller than FP16 weights in practice.
        if footprint >= int(0.80 * fp16_reference_bytes):
            raise RuntimeError(
                "INT8 model footprint is too close to FP16 reference; "
                "possible silent fallback to higher precision"
            )
    return footprint
