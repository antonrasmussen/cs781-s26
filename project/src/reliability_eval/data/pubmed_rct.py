from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

logger = logging.getLogger(__name__)

# Path to the tiny in-repo sample dataset. This assumes the sample file is located
# alongside this module; adjust as needed if the project layout differs.
SAMPLE_PUBMED_RCT_PATH = Path(__file__).with_name("pubmed_rct_sample.jsonl")


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Load a JSONL file into a list of dictionaries."""
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def load_pubmed_rct(
    path_or_hf_id: Optional[str] = None,
    *,
    use_sample: bool = False,
) -> Iterable[Dict[str, Any]]:
    """
    Load the PubMed RCT dataset.

    Safety semantics:
    - If ``use_sample`` is True, the tiny in-repo sample is loaded explicitly.
    - If ``use_sample`` is False and ``path_or_hf_id`` is a path to an existing
      local file, that file is loaded.
    - If ``use_sample`` is False and ``path_or_hf_id`` is non-empty but does *not*
      resolve to an existing local file, a FileNotFoundError is raised.

    In particular, this function will *not* silently fall back to the tiny sample
    when a non-empty but invalid ``path_or_hf_id`` is provided. Callers must opt in
    to using the sample by passing ``use_sample=True``.

    Parameters
    ----------
    path_or_hf_id:
        Path to a local file containing the dataset. At present, this loader treats
        the value as a filesystem path; it does not automatically download
        HuggingFace datasets. If a non-empty value is provided that does not
        correspond to an existing file, a FileNotFoundError is raised.
    use_sample:
        When True, load the tiny in-repo sample dataset regardless of
        ``path_or_hf_id``. This parameter must be set explicitly; the function will
        never silently fall back to the sample for non-existent paths.

    Returns
    -------
    Iterable[Dict[str, Any]]
        An iterable of dataset examples.
    """
    # Explicit opt-in to the sample dataset.
    if use_sample:
        if not SAMPLE_PUBMED_RCT_PATH.exists():
            raise FileNotFoundError(
                f"Requested use_sample=True, but sample dataset file was not found at "
                f"{SAMPLE_PUBMED_RCT_PATH}"
            )
        logger.info("Loading PubMed RCT tiny sample from %s", SAMPLE_PUBMED_RCT_PATH)
        return _load_jsonl(SAMPLE_PUBMED_RCT_PATH)

    # If no path_or_hf_id is provided, we *do not* implicitly fall back to the
    # sample. Depending on project conventions, this could alternatively raise a
    # ValueError; here we raise to avoid ambiguity.
    if not path_or_hf_id:
        raise ValueError(
            "No 'path_or_hf_id' provided and 'use_sample' is False. "
            "To use the in-repo tiny sample, call load_pubmed_rct(use_sample=True)."
        )

    candidate_path = Path(path_or_hf_id)

    # Core safety fix: if the caller passed a non-empty path_or_hf_id that does not
    # correspond to an existing local file, we fail loudly instead of silently
    # falling back to the tiny sample.
    if not candidate_path.exists():
        raise FileNotFoundError(
            "The provided 'path_or_hf_id' does not point to an existing local file: "
            f"{path_or_hf_id!r}. "
            "This function does not automatically download HuggingFace datasets and "
            "does not silently fall back to the tiny in-repo sample. "
            "If you intended to use the sample, call "
            "load_pubmed_rct(use_sample=True) explicitly."
        )

    logger.info("Loading PubMed RCT dataset from local file %s", candidate_path)
    return _load_jsonl(candidate_path)
"""PubMed 20k RCT dataset adapter for MVP.

The MVP loader supports local JSONL files and an in-repo tiny sample fixture.
"""

from __future__ import annotations

import json
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
        path = _SAMPLE_PATH
    examples = _read_jsonl(path)
    if sample_size is not None:
        return examples[: max(0, int(sample_size))]
    return examples
