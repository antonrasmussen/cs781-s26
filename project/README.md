# Reliability of Quantized Biomedical LLMs

**Calibration and prompt stability under resource constraints.**

Course project (CS781 – AI for Health Sciences, Spring 2026). This directory contains the proposal, scaffold, and (eventually) the evaluation harness and experiments.

## Goal

Evaluate how post-training quantization of **BioMistral-7B** affects:

1. **Calibration** — ECE, ACE, reliability diagrams; recovery via temperature scaling and isotonic regression.
2. **Prompt stability** — agreement across meaning-preserving prompt templates (e.g. Fleiss’ kappa).

Tasks: **PubMed 20k RCT** (5-class) and **MedNLI** (3-class, with PubMed-only fallback). Precisons: FP16, INT8, INT4 (bitsandbytes). Probability extraction uses **single-token class codes** (A–E / A–C), not natural-language verbalizers.

## Repo layout

- **`docs/`** — Documentation: proposal, architecture, experiment protocol, and audit deliverables.
  - **`docs/proposal.md`** — Full proposal (methodology, timeline, references).
  - **`docs/scripts/build_pdf.py`** — Build proposal PDF from Markdown.
- **`configs/`** — Base, dataset, model, precision, prompt, calibration, and sweep YAMLs.
- **`src/reliability_eval/`** — Python package: data, models, prompting, inference, metrics, calibration, experiments, reporting, flyte (thin wrappers).
- **`experiments/`** — Entrypoints: `run_local.py`, `run_mvp.py`, `run_grid.py`.
- **`artifacts/`** — Run outputs (predictions, metrics, figures). MVP runs use mock inference and the in-repo tiny sample; see `metadata.json` for `mode` and `dataset_source`.
- **`reports/`** — Generated figures and tables for the report.
- **`tests/`** — Pytest; start with label codes and config loading.

## Quick start

```bash
cd project
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -e .

# MVP run (mock inference, tiny sample)
python experiments/run_mvp.py --sample-size 8 --template-id pubmed_t1

# CLI
PYTHONPATH=src python -m reliability_eval.cli run --sample-size 8
PYTHONPATH=src python -m reliability_eval.cli sweep --dry-run

# Tests (from project root; requires pytest)
PYTHONPATH=src pytest tests/ -v
```

See `docs/execution_modes.md` for local, Flyte sandbox, and ODU compute modes.

## Implementation plan

1. **Phase 0** — Scaffold (this step): folders, stubs, configs, README.
2. **Phase 1** — Dataset ingestion and split logic.
3. **Phase 2** — Model loading and single-token class-code scoring.
4. **Phase 3** — Metrics and calibration.
5. **Phase 4** — Prompt robustness (templates, kappa).
6. **Phase 5** — Flyte orchestration (optional).
7. **Phase 6** — Reporting and paper figures.

## References

See `docs/proposal.md` §9 (References). Key: Dernoncourt & Lee (PubMed RCT), Romanov & Shivade (MedNLI), Labrak et al. (BioMistral), Guo et al. (calibration), Dettmers et al. (LLM.int8, QLoRA).
