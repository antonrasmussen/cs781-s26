"""Label-code mappings used for class-code scoring."""

from typing import Dict


_PUBMED_RCT_LABEL_CODES: Dict[str, str] = {
    "BACKGROUND": "A",
    "OBJECTIVE": "B",
    "METHODS": "C",
    "RESULTS": "D",
    "CONCLUSIONS": "E",
}

_MEDNLI_LABEL_CODES: Dict[str, str] = {
    "entailment": "A",
    "contradiction": "B",
    "neutral": "C",
}


def get_label_codes(task: str) -> dict:
    """Return canonical label -> code mapping for a task."""
    if task == "pubmed_rct":
        return dict(_PUBMED_RCT_LABEL_CODES)
    if task == "mednli":
        return dict(_MEDNLI_LABEL_CODES)
    raise ValueError(f"Unknown task: {task}")


def get_code_to_label(task: str) -> dict:
    """Return inverse mapping code -> label."""
    label_to_code = get_label_codes(task)
    return {code: label for label, code in label_to_code.items()}
