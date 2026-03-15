"""Load BioMistral-7B at specified precision.

TODO: Support FP16 and quantized (INT8/INT4) via bitsandbytes.
"""


def load_biomistral(precision: str, device_map: str = "auto"):
    """Load model. precision in ('fp16', 'int8', 'int4'). TODO: Implement."""
    raise NotImplementedError("TODO: implement load_model.load_biomistral")
