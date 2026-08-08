"""VRAM, latency, throughput (supplementary).

Manuscript scope: **not implemented**. Do not claim deployment efficiency gains
without measured artifacts (see ``docs/manuscript_claim_boundaries.md``).
"""


def measure_efficiency(model, tokenizer, batch_sizes=(1, 16)):
    """Return dict with vram_mb, latency_ms, throughput.

    Raises:
        NotImplementedError: Always — out of current manuscript package scope.
    """
    raise NotImplementedError(
        "efficiency.measure_efficiency is out of manuscript scope; "
        "see docs/manuscript_claim_boundaries.md"
    )
