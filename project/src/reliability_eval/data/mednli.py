"""MedNLI dataset adapter — intentionally unimplemented (stub).

``load_mednli`` raises :class:`NotImplementedError` until a PhysioNet path or
Hugging Face dataset id is confirmed and ingestion is implemented. There is no
fallback dataset behavior in this module.
"""


def load_mednli(path_or_hf_id: str | None = None, split: str = "test"):
    """Load MedNLI for a given split.

    Not implemented. Callers must catch :class:`NotImplementedError` or avoid
    this dataset until credentials and ``path_or_hf_id`` are configured.

    Args:
        path_or_hf_id: PhysioNet path or HF dataset id when available; ``None``
            if unset in config (YAML ``null``).
        split: Split name (e.g. ``train``, ``validation``, ``test``).

    Raises:
        NotImplementedError: Always, until loading is implemented.
    """
    raise NotImplementedError("TODO: implement mednli.load_mednli")
