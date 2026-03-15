"""Prompt rendering. Loads templates from configs/prompts/*.yaml (canonical source)."""

from __future__ import annotations

from pathlib import Path

from reliability_eval.prompting.label_codes import get_label_codes
from reliability_eval.prompting.template_registry import get_template_body


def _legend_from_label_codes(label_codes: dict) -> str:
    by_code = sorted(((code, label) for label, code in label_codes.items()), key=lambda x: x[0])
    return " ".join(f"{code}={label}" for code, label in by_code)


def render(
    template_id: str,
    task: str,
    text: str,
    label_codes: dict | None = None,
    config_dir: str | Path | None = None,
) -> str:
    """Render one prompt for a task/template pair.

    Uses configs/prompts/<task>_templates.yaml when config_dir is provided.
    """
    codes = label_codes or get_label_codes(task)
    legend = _legend_from_label_codes(codes)
    body = get_template_body(task=task, template_id=template_id, config_dir=config_dir)
    return body.format(legend=legend, text=text.strip())
