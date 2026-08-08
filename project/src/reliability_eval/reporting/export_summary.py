"""Export run summary and figures for report.

Manuscript scope: use ``experiments/build_final_report.py`` or
``python -m reliability_eval.cli report`` instead. This helper remains a stub.
"""


def export_summary(run_dir: str, output_dir: str) -> None:
    """Copy/write summary artifacts to output_dir.

    Raises:
        NotImplementedError: Always — prefer build_final_report / CLI report.
    """
    raise NotImplementedError(
        "reporting.export_summary is a stub; use experiments/build_final_report.py "
        "or `reliability-eval report` (see docs/manuscript_claim_boundaries.md)"
    )
