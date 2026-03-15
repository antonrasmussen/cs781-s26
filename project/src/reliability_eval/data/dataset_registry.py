"""Registry of dataset names to loader functions.

TODO: Register pubmed_rct, mednli; resolve from config.
"""


def get_loader(dataset_id: str):
    """Return loader callable for dataset_id. TODO: Implement registry."""
    raise NotImplementedError("TODO: implement dataset_registry.get_loader")
