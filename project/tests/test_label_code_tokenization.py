"""Tests for label-code mapping and single-token tokenization.

TODO: When a real tokenizer is wired, replace ``xfail`` on
``test_tokenization_single_token`` with assertions that each class code maps to
exactly one token id.
"""
import pytest


@pytest.mark.xfail(reason="Pending real tokenizer; remove xfail once codes are checked.")
def test_tokenization_single_token():
    """Placeholder for single-token checks (A-E / A-C) against the live tokenizer."""
    pytest.fail("requires tokenizer fixture")


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
