"""Prompt rendering for MVP templates."""

from __future__ import annotations

from reliability_eval.prompting.label_codes import get_label_codes


_PUBMED_TEMPLATES = {
    "pubmed_t1": (
        "Classify the following PubMed abstract sentence into one rhetorical role.\n"
        "{legend}\n"
        "Sentence: {text}\n"
        "Answer with a single letter."
    ),
    "pubmed_t2": (
        "Assign the sentence to exactly one category.\n"
        "{legend}\n"
        "Input sentence: {text}\n"
        "Return only one letter."
    ),
}


def _legend_from_label_codes(label_codes: dict) -> str:
    by_code = sorted(((code, label) for label, code in label_codes.items()), key=lambda x: x[0])
    return " ".join(f"{code}={label}" for code, label in by_code)


def render(template_id: str, task: str, text: str, label_codes: dict | None = None) -> str:
    """Render one prompt for a task/template pair."""
    if task != "pubmed_rct":
        raise ValueError(f"MVP renderer only supports pubmed_rct, got '{task}'")
    if template_id not in _PUBMED_TEMPLATES:
        raise ValueError(f"Unknown template_id '{template_id}'")
    codes = label_codes or get_label_codes(task)
    legend = _legend_from_label_codes(codes)
    return _PUBMED_TEMPLATES[template_id].format(legend=legend, text=text.strip())
