"""PubMed 20k RCT dataset adapter for MVP.

The MVP loader supports local JSONL files and an in-repo tiny sample fixture.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Dict, List, Optional

from reliability_eval.prompting.label_codes import get_label_codes


_SAMPLE_PATH = (
    Path(__file__).resolve().parents[3] / "data" / "samples" / "pubmed_rct_tiny.jsonl"
)


def _normalize_record(record: Dict, idx: int) -> Dict[str, str]:
    text = str(record.get("text", "")).strip()
    raw_label = str(record.get("label", "")).strip()
    label_aliases = {
        "BACKGROUND": "BACKGROUND",
        "BACKGROUND:": "BACKGROUND",
        "OBJECTIVE": "OBJECTIVE",
        "OBJECTIVES": "OBJECTIVE",
        "METHOD": "METHODS",
        "METHODS": "METHODS",
        "RESULT": "RESULTS",
        "RESULTS": "RESULTS",
        "CONCLUSION": "CONCLUSIONS",
        "CONCLUSIONS": "CONCLUSIONS",
    }
    label = label_aliases.get(raw_label.upper(), raw_label.upper())
    example_id = str(record.get("example_id", f"pubmed_{idx}"))
    if not text:
        raise ValueError(f"Empty text in record {idx}")
    valid_labels = set(get_label_codes("pubmed_rct").keys())
    if label not in valid_labels:
        raise ValueError(f"Invalid PubMed label '{label}' in record {idx}")
    return {"example_id": example_id, "text": text, "label": label}


def _read_jsonl(path: Path) -> List[Dict[str, str]]:
    examples: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            examples.append(_normalize_record(record, idx))
    return examples


def _read_hf_split(
    path_or_hf_id: str,
    split: str,
    revision: str | None = None,
) -> List[Dict[str, str]]:
    try:
        from datasets import load_dataset
    except ImportError as e:  # pragma: no cover - environment dependent
        raise ImportError(
            "datasets is required for Hugging Face dataset loading. "
            "Install with `pip install -e .[gpu]`."
        ) from e

    ds = load_dataset(path_or_hf_id, split=split, revision=revision)
    examples: List[Dict[str, str]] = []
    for idx, record in enumerate(ds, start=1):
        if "text" in record:
            text = record["text"]
        elif "sentence" in record:
            text = record["sentence"]
        else:
            text = ""
        label = record.get("label_text")
        if label is None:
            label = record.get("label")
        if isinstance(label, int):
            # Common class index order for PubMed RCT.
            idx_to_label = {
                0: "BACKGROUND",
                1: "OBJECTIVE",
                2: "METHODS",
                3: "RESULTS",
                4: "CONCLUSIONS",
            }
            label = idx_to_label.get(label, str(label))
        ex = _normalize_record(
            {"example_id": record.get("example_id", f"pubmed_{idx}"), "text": text, "label": label},
            idx,
        )
        examples.append(ex)
    return examples


def load_pubmed_rct(
    path_or_hf_id: Optional[str] = None,
    split: str = "test",
    sample_size: Optional[int] = None,
    hf_revision: str | None = None,
) -> List[Dict[str, str]]:
    """Load PubMed examples as normalized records.

    Args:
        path_or_hf_id: Local JSONL file path or None to use tiny in-repo sample.
        split: Kept for API compatibility; currently unused for local fixture mode.
        sample_size: Optional cap for tiny MVP runs.
    """
    _ = split  # TODO: Use split when full dataset integration is added.
    path: Path
    if path_or_hf_id and Path(path_or_hf_id).exists():
        path = Path(path_or_hf_id)
        examples = _read_jsonl(path)
    elif path_or_hf_id:
        examples = _read_hf_split(path_or_hf_id, split=split, revision=hf_revision)
    else:
        warnings.warn(
            "path_or_hf_id is unset; falling back to in-repo tiny sample "
            f"{_SAMPLE_PATH}",
            UserWarning,
            stacklevel=2,
        )
        examples = _read_jsonl(_SAMPLE_PATH)
    if sample_size is not None:
        return examples[: max(0, int(sample_size))]
    return examples
