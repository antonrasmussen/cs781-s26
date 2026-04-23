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
