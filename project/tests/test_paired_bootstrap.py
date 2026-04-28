import pytest

from reliability_eval.metrics.paired_tests import paired_bootstrap_ci, recovery_ratio


def test_paired_bootstrap_ci_positive_shift():
    out = paired_bootstrap_ci([0.2, 0.1, 0.3, 0.2], n_resamples=200, seed=42)
    assert out["point"] > 0


def test_recovery_ratio_raises_on_zero_denominator():
    with pytest.raises(ValueError, match="undefined"):
        recovery_ratio(ece_uncal=0.2, ece_cal=0.1, ece_fp16=0.2)
