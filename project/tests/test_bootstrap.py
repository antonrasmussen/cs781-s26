from reliability_eval.metrics.bootstrap import bootstrap_ci


def test_bootstrap_ci_is_deterministic_with_seed():
    values = [1.0, 2.0, 3.0, 4.0]
    a = bootstrap_ci(values, lambda xs: sum(xs) / len(xs), n_resamples=200, seed=42)
    b = bootstrap_ci(values, lambda xs: sum(xs) / len(xs), n_resamples=200, seed=42)
    assert a == b


def test_bootstrap_ci_contains_point_estimate():
    values = [1.0, 2.0, 3.0, 4.0]
    out = bootstrap_ci(values, lambda xs: sum(xs) / len(xs), n_resamples=200, seed=1)
    assert out["ci_low"] <= out["point"] <= out["ci_high"]
