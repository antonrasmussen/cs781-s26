"""Tests for label-code mapping and single-token tokenization."""

import pytest


def test_tokenization_single_token():
    """Class-code letters map to one token each for BioMistral tokenizer."""
    transformers = pytest.importorskip("transformers")
    from reliability_eval.models.tokenizer_utils import get_code_token_ids

    try:
        tokenizer = transformers.AutoTokenizer.from_pretrained(
            "BioMistral/BioMistral-7B"
        )
    except Exception as e:  # pragma: no cover - environment dependent
        pytest.skip(f"Tokenizer unavailable in this environment: {e}")

    pubmed_ids = get_code_token_ids(tokenizer, task="pubmed_rct")
    mednli_ids = get_code_token_ids(tokenizer, task="mednli")

    assert len(pubmed_ids) == 5
    assert len(set(pubmed_ids)) == 5
    assert len(mednli_ids) == 3
    assert len(set(mednli_ids)) == 3


def test_label_codes_pubmed_rct():
    """Label codes for PubMed RCT are A-E."""
    from reliability_eval.prompting.label_codes import get_label_codes
    codes = get_label_codes("pubmed_rct")
    assert set(codes.values()) == {"A", "B", "C", "D", "E"}
    assert codes["BACKGROUND"] == "A"
    assert codes["CONCLUSIONS"] == "E"


def test_label_codes_mednli():
    """Label codes for MedNLI are A-C."""
    from reliability_eval.prompting.label_codes import get_label_codes
    codes = get_label_codes("mednli")
    assert set(codes.values()) == {"A", "B", "C"}
    assert codes["entailment"] == "A"


def test_unknown_task_raises():
    """Unknown task raises ValueError."""
    from reliability_eval.prompting.label_codes import get_label_codes
    with pytest.raises(ValueError, match="Unknown task"):
        get_label_codes("unknown")
