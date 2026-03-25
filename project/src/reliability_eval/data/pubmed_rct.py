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
    label = str(record.get("label", "")).strip().upper()
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


def load_pubmed_rct(
    path_or_hf_id: Optional[str] = None,
    split: str = "test",
    sample_size: Optional[int] = None,
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
    else:
        if path_or_hf_id:
            warnings.warn(
                f"path_or_hf_id={path_or_hf_id!r} is not an existing local path; "
                f"falling back to in-repo sample {_SAMPLE_PATH}",
                UserWarning,
                stacklevel=2,
            )
        path = _SAMPLE_PATH
    examples = _read_jsonl(path)
    if sample_size is not None:
        return examples[: max(0, int(sample_size))]
    return examples
