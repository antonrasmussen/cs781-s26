"""Summary tables: precision x ECE/F1, recovery ratios. TODO: Implement."""


def metrics_table(run_metrics: list) -> str:
    """Return a simple Markdown table for run metrics rows."""
    headers = [
        "run_id",
        "precision",
        "template_id",
        "n_examples",
        "accuracy",
        "macro_f1",
        "ece",
        "ece_calibrated",
        "temperature",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in run_metrics:
        values = []
        for key in headers:
            value = row.get(key, "")
            if isinstance(value, float):
                values.append(f"{value:.6f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines) + "\n"
