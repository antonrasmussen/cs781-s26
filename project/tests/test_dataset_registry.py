"""Tests for dataset id -> loader registry."""

import pytest

from reliability_eval.data.dataset_registry import DATASET_REGISTRY, get_loader


def test_get_loader_pubmed_rct():
    assert get_loader("pubmed_rct") is DATASET_REGISTRY["pubmed_rct"]


def test_get_loader_unknown_raises():
    with pytest.raises(KeyError, match="Unknown dataset_id"):
        get_loader("not_a_dataset")
