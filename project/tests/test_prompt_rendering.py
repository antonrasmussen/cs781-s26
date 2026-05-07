"""Tests for PubMed prompt rendering."""

from reliability_eval.prompting.label_codes import get_label_codes
from reliability_eval.prompting.render import render


def test_render_pubmed_t5_puts_background_last_in_legend():
    from pathlib import Path

    project = Path(__file__).resolve().parent.parent
    codes = get_label_codes("pubmed_rct")
    prompt = render(
        template_id="pubmed_t5",
        task="pubmed_rct",
        text="Example sentence for template smoke.",
        label_codes=codes,
        config_dir=str(project / "configs"),
    )
    assert "A=BACKGROUND" in prompt
    assert "E=CONCLUSIONS" in prompt


def test_render_pubmed_template_contains_text_and_codes():
    codes = get_label_codes("pubmed_rct")
    prompt = render(
        template_id="pubmed_t1",
        task="pubmed_rct",
        text="Methods: We randomized 120 participants.",
        label_codes=codes,
    )
    assert "Methods: We randomized 120 participants." in prompt
    assert "A=BACKGROUND" in prompt
    assert "E=CONCLUSIONS" in prompt
    assert "single letter" in prompt.lower()
