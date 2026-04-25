"""Registry of prompt templates loaded from configs/prompts/*.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any


# Task id -> config filename (configs/prompts/<name>.yaml)
_TASK_PROMPT_FILES: dict[str, str] = {
    "pubmed_rct": "pubmed_templates.yaml",
    "mednli": "mednli_templates.yaml",
}

def _default_config_dir() -> Path:
    """Return repo configs path for direct/script usage."""
    return Path(__file__).resolve().parents[3] / "configs"


def _load_prompt_config(config_dir: str | Path, task: str) -> dict[str, Any]:
    """Load prompt config YAML for task. Returns empty dict on error."""
    try:
        import yaml  # type: ignore
    except ImportError:
        return {}
    filename = _TASK_PROMPT_FILES.get(task, f"{task}_templates.yaml")
    path = Path(config_dir) / "prompts" / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Prompt config for task {task!r} not found: {path}"
        )
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_template_body(
    task: str,
    template_id: str,
    config_dir: str | Path | None = None,
) -> str:
    """Return template body string for task/template_id. Loads from YAML if config_dir given."""
    cfg = _load_prompt_config(config_dir or _default_config_dir(), task)
    for t in cfg.get("templates", []):
        if t.get("id") == template_id and "body" in t:
            return str(t["body"]).strip()
    raise ValueError(f"Template '{template_id}' not found in config for task '{task}'")


def get_templates(task: str, config_dir: str | Path | None = None) -> list[dict]:
    """Return list of template specs for task. Loads from YAML if config_dir given."""
    cfg = _load_prompt_config(config_dir or _default_config_dir(), task)
    return cfg.get("templates", [])
