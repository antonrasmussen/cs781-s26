"""Train/val/calibration/test split logic.

TODO: Implement deterministic splits; 15% calibration from val.
"""


def get_splits(dataset_id: str, seed: int = 42):
    """Return split names or indices. TODO: Implement."""
    return ["train", "val", "calibration", "test"]
