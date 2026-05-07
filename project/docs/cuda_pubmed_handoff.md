# CUDA handoff: PubMed first experiment

**Historical context:** This is an operator runbook from **active development** (CUDA handoff and early gates). For the **final submission** narrative, numbers, and hypothesis outcomes, read [`reports/final_report.md`](../reports/final_report.md), [`reports/final_metrics.md`](../reports/final_metrics.md), and [`reports/hypothesis_tests.md`](../reports/hypothesis_tests.md).

Use this when moving to a CUDA machine. The goal is to get from the current data inventory to the first serious PubMed experiment without wasting time on already-solved data work.

## Current state

Already ready:

- PubMed 20k RCT HF access is verified: `scripts/verify_hf_access.py`.
- Full PubMed split provenance is recorded: `data/provenance/pubmed_rct_download.json`.
- Deterministic balanced test-derived subset exists: `data/samples/pubmed_rct_dev200.jsonl`.
- Subset provenance exists: `data/samples/pubmed_rct_dev200.provenance.json`.
- PubMed loader supports HF and local JSONL: `src/reliability_eval/data/pubmed_rct.py`.
- PubMed prompt templates `pubmed_t1` through `pubmed_t5` exist: `configs/prompts/pubmed_templates.yaml`.
- BioMistral single-token label-code validation has already passed per `docs/data_inventory.md`.
- Real inference path exists through `src/reliability_eval/experiments/run_single.py`.

Do not spend CUDA time re-solving data access unless a command actually fails.

## Actual blocker

The current blocker is not data. It is verifying that real FP16 inference with a revised prompt does not collapse to `BACKGROUND`.

Known bad prior run:

- Run artifact: `artifacts/runs/mvp_pubmed_reliabili_20260423T034428_611367Z_603ebe/`
- Template: `pubmed_t1`
- Inference mode: `real_inference`
- Dataset: `data/samples/pubmed_rct_tiny.jsonl` (n=8)
- Result: every prediction was `A` / `BACKGROUND`

The first gate is therefore a non-collapsed `pubmed_t5` real-inference run on `dev200`.

## CUDA setup

From repo root:

```bash
cd /path/to/cs781-s26/project
python -m venv .venv
source .venv/bin/activate
pip install -e ".[gpu,dev]"
export PYTHONPATH=src
export RELIABILITY_ARTIFACT_ROOT=artifacts/runs
```

Expected environment:

- Linux CUDA host.
- Enough VRAM for BioMistral-7B FP16, preferably at least 16 GB.
- If using ODU, use the same repo commands; ODU is plain remote compute, not a different pipeline.

## Run first: FP16 real inference on dev200

Use local `dev200` first. It is deterministic, balanced 40 per class, already normalized, and avoids HF/network/sample-order surprises while checking collapse.

```bash
PYTHONPATH=src python -m reliability_eval.cli run \
  --profile local_real \
  --dataset pubmed_rct_dev200 \
  --precision fp16 \
  --template pubmed_t5 \
  --calibration none \
  --sample-size 200
```

The CLI prints a `run_id`. Resolve it to a run directory as:

```bash
export RUN_ID=<printed-run-id>
export RUN_DIR="${RELIABILITY_ARTIFACT_ROOT:-artifacts/runs}/${RUN_ID}"
```

## Inspect the collapse gate

Run this immediately after the smoke run:

```bash
python scripts/inspect_run.py --run-dir "$RUN_DIR"
```

If a long run is interrupted, re-run with the same `run_id`; the pipeline now resumes
from the existing `predictions.jsonl` prefix when it matches the dataset prefix.

If needed, the equivalent inline Python check remains available in git history.

Pass condition:

- `metadata.json` says `inference_mode: real_inference`.
- `predictions.jsonl` has 200 rows.
- Predicted labels use several classes, not only `BACKGROUND`.
- Uncalibrated `macro_f1` is greater than `0.20`.
- Calibration is still `none`.

Note: the known-bad n=8 collapse artifact may not be present on fresh clones because run outputs are local and ignored by default. If needed, reproduce collapse diagnostics with `scripts/diagnose_background_collapse.py`.

If this fails because predictions are still collapsed, do not run calibration, INT8, INT4, or full-test evaluation.

## If pubmed_t5 still collapses

Compare only prompt behavior on the same `dev200` slice:

- `pubmed_t3`
- `pubmed_t4`
- `pubmed_t5`

Use the same script above and change only `template_id`.

Purpose: find whether any current prompt avoids collapse. Do not treat small metric differences as experiment results yet.

Relevant files:

- `configs/prompts/pubmed_templates.yaml`
- `notebooks/02_prompt_template_dev.ipynb`
- `scripts/diagnose_background_collapse.py`

## After the gate passes

The first serious experiment should be:

- Dataset: PubMed only.
- Data source: start with `data/samples/pubmed_rct_dev200.jsonl`.
- Model: `BioMistral/BioMistral-7B`.
- Precision: FP16.
- Template: the first non-collapsing template, likely `pubmed_t5`.
- Calibration: `none`.
- Sample size: 200.

Only after this run is sane should you scale to HF-hosted PubMed test or full test.

Use HF-hosted PubMed when the pipeline is stable and you want provenance-aligned full split loading from `configs/datasets/pubmed_rct.yaml`. Do not start with full test; it is too expensive if the prompt is still broken.

## Ignore for now

- MedNLI experiments.
- Temperature scaling.
- Isotonic calibration.
- INT8 and INT4 runs.
- ACE/bootstrap confidence intervals.
- Full prompt-stability sweeps.
- Full test split.

MedNLI is blocked until there is a lawful concrete data path. Current repo state:

- `configs/datasets/mednli.yaml` has `path_or_hf_id: null`.
- `src/reliability_eval/data/mednli.py` raises `NotImplementedError`.
- `configs/prompts/mednli_templates.yaml` has placeholder template IDs without bodies.

Document MedNLI as blocked; do not pretend access exists.

## Ready for first experiment means

You are ready to begin actual experiments when you have one artifact under `artifacts/runs/` where:

- `metadata.json` records `real_inference`.
- `resolved_config.yaml` points to PubMed, FP16, calibration none, and the chosen non-collapsing template.
- `dataset_source` is `data/samples/pubmed_rct_dev200.jsonl` or equivalent local path.
- `predictions.jsonl` has 200 PubMed rows.
- Prediction counts are not collapsed to one class.
- `metrics.json` has uncalibrated `macro_f1 > 0.20`.

Until then, the work is still prompt/inference validation, not experiment execution.
