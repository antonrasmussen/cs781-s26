"""Temperature scaling (Guo et al.): single T on calibration set.

TODO: Optimize T to minimize NLL on calib set; apply logits/T at test.
"""


def fit_temperature(probs_calib, labels_calib):
    """Return optimal T. TODO: Implement."""
    raise NotImplementedError("TODO: implement temperature_scaling.fit_temperature")
