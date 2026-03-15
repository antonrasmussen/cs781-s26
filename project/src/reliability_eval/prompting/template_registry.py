"""Registry of prompt templates per task. Loads from configs/prompts/*.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any


# Task id -> config filename (configs/prompts/<name>.yaml)
_TASK_PROMPT_FILES: dict[str, str] = {
    "pubmed_rct": "pubmed_templates.yaml",
    "mednli": "mednli_templates.yaml",
}

# Fallback when YAML missing or template has no body
_PUBMED_FALLBACK: dict[str, str] = {
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


def _load_prompt_config(config_dir: str | Path, task: str) -> dict[str, Any]:
    """Load prompt config YAML for task. Returns empty dict on error."""
    try:
        import yaml  # type: ignore
    except ImportError:
        return {}
    filename = _TASK_PROMPT_FILES.get(task, f"{task}_templates.yaml")
    path = Path(config_dir) / "prompts" / filename
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_template_body(
    task: str,
    template_id: str,
    config_dir: str | Path | None = None,
) -> str:
    """Return template body string for task/template_id. Loads from YAML if config_dir given."""
    if config_dir:
        cfg = _load_prompt_config(config_dir, task)
        for t in cfg.get("templates", []):
            if t.get("id") == template_id and "body" in t:
                return t["body"].strip()
        # Fallback to hardcoded when YAML missing body (e.g. stub templates)
        if task == "pubmed_rct" and template_id in _PUBMED_FALLBACK:
            return _PUBMED_FALLBACK[template_id]
        raise ValueError(f"Template '{template_id}' not found in config for task '{task}'")

    # Fallback: hardcoded PubMed templates when no config_dir (backward compat)
    if task == "pubmed_rct" and template_id in _PUBMED_FALLBACK:
        return _PUBMED_FALLBACK[template_id]
    raise ValueError(f"Unknown template '{template_id}' for task '{task}' (no config_dir)")


def get_templates(task: str, config_dir: str | Path | None = None) -> list[dict]:
    """Return list of template specs for task. Loads from YAML if config_dir given."""
    if config_dir:
        cfg = _load_prompt_config(config_dir, task)
        return cfg.get("templates", [])
    # Fallback: return stub list for pubmed_rct
    if task == "pubmed_rct":
        return [{"id": "pubmed_t1"}, {"id": "pubmed_t2"}]
    return []
