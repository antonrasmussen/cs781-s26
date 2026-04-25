"""Prompt rendering. Loads templates from configs/prompts/*.yaml (canonical source)."""

from __future__ import annotations

import re
from pathlib import Path

from reliability_eval.prompting.label_codes import get_label_codes
from reliability_eval.prompting.template_registry import get_template_body


def _format_template_body(body: str, *, legend: str, text: str) -> str:
    """Format template body; only substitute ``{legend}`` / ``{text}`` if present."""
    keys = set(re.findall(r"\{(\w+)\}", body))
    parts: dict[str, str] = {}
    if "legend" in keys:
        parts["legend"] = legend
    if "text" in keys:
        parts["text"] = text.strip()
    return body.format(**parts)


def _legend_from_label_codes(label_codes: dict) -> str:
    by_code = sorted(((code, label) for label, code in label_codes.items()), key=lambda x: x[0])
    return " ".join(f"{code}={label}" for code, label in by_code)


def render(
    template_id: str,
    task: str,
    text: str,
    label_codes: dict | None = None,
    config_dir: str | Path | None = None,
    legend_override: str | None = None,
) -> str:
    """Render one prompt for a task/template pair.

    Uses configs/prompts/<task>_templates.yaml when config_dir is provided.

    Args:
        legend_override: If set, use this legend string instead of building from
            ``label_codes`` (for prompt-order / priming experiments).
    """
    codes = label_codes or get_label_codes(task)
    legend = legend_override if legend_override is not None else _legend_from_label_codes(codes)
    body = get_template_body(task=task, template_id=template_id, config_dir=config_dir)
    return _format_template_body(body, legend=legend, text=text)
