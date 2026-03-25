# Sources of Truth Inventory

Classification of project artifacts for the consistency audit. Each item is tagged as: **narrative**, **code**, **config**, **data**, **generated artifact**, or **placeholder**.

---

## Narrative (authored documentation)

| Path | Description |
|------|-------------|
| `README.md` | Project overview, repo layout, quick start, implementation phases |
| `docs/proposal.md` | Full proposal: methodology, hypotheses, tasks, timeline, references |
| `docs/architecture.md` | Module map, data flow, design decisions |
| `docs/experiment_protocol.md` | Splits, decoding, metrics, prompt robustness summary |

---

## Code (implementation)

| Path | Description |
|------|-------------|
| `src/reliability_eval/**/*.py` | Python package: data, models, prompting, inference, metrics, calibration, experiments, reporting, flyte, io |
| `experiments/run_mvp.py` | MVP entrypoint (mock inference, PubMed only) |
| `experiments/run_local.py` | Local run entrypoint (placeholder) |
| `experiments/run_grid.py` | Grid sweep entrypoint (placeholder) |
| `docs/scripts/build_pdf.py` | Converts `docs/proposal.md` to HTML/PDF |

---

## Config (YAML and project metadata)

| Path | Description |
|------|-------------|
| `configs/base.yaml` | Seed, artifact root, evaluation settings |
| `configs/datasets/pubmed_rct.yaml` | PubMed dataset config |
| `configs/datasets/mednli.yaml` | MedNLI dataset config |
| `configs/models/biomistral_7b.yaml` | BioMistral model config |
| `configs/precisions/fp16.yaml`, `int8.yaml`, `int4.yaml` | Precision configs |
| `configs/prompts/pubmed_templates.yaml` | PubMed prompt templates (2 templates) |
| `configs/prompts/mednli_templates.yaml` | MedNLI prompt templates (stub) |
| `configs/calibration/*.yaml` | Calibration method configs |
| `configs/sweeps/mvp_pubmed.yaml` | MVP sweep config |
| `pyproject.toml` | Package metadata, dependencies |
| `requirements.txt` | Pip dependencies |
| `.gitignore` | Ignore rules |

---

## Data (datasets and samples)

| Path | Description |
|------|-------------|
| `data/samples/pubmed_rct_tiny.jsonl` | In-repo tiny sample fixture for MVP |

---

## Generated artifact (outputs from runs or builds)

| Path | Description |
|------|-------------|
| `docs/generated/proposal.html` | HTML export of proposal (from `build_pdf.py`; gitignored) |
| `docs/generated/proposal.pdf` | PDF export of proposal (from `build_pdf.py`; gitignored) |
| `artifacts/runs/*/` | Run outputs: `metadata.json`, `metrics.json`, `predictions.jsonl`, `resolved_config.yaml`, `figures/reliability.png` |
| `src/reliability_eval.egg-info/*` | Setuptools metadata (gitignored via `*.egg-info/`) |

---

## Placeholder (empty or stub)

| Path | Description |
|------|-------------|
| `reports/` | Empty (`.gitkeep` only); intended for report figures/tables |
| `notebooks/` | Empty (`.gitkeep` only); intended for Jupyter notebooks |
| `docs/scripts/markdown-pdf.css` | Optional CSS for PDF (build_pdf uses inline CSS) |

---

## Root-level clutter (resolved)

Reorganization complete. Proposal, build script, and generated outputs now live under `docs/`.
