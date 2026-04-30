# CS781 – AI for Health Sciences: Final Project

**Reliability of Quantized Biomedical LLMs: Calibration and Prompt Stability under Resource Constraints**

Anton Rasmussen | CS781 AI for Health Sciences, Spring 2026

---

## Project Summary

This project evaluates whether post-training quantization of a biomedical language model
(`BioMistral-7B`) degrades *calibration* (Expected Calibration Error, ECE) more than it degrades
*classification quality* (macro F1), and whether post-hoc temperature scaling can recover the
lost calibration. Experiments use a single-token class-code scoring protocol on PubMed 20k RCT
sentence classification (5 classes, n=2000 test slice) across three precision conditions: FP16
baseline, INT8 (`bitsandbytes`), and INT4 (`bitsandbytes NF4`). The study is motivated by the
practical reality that resource-constrained healthcare AI deployments often require quantized
models, where calibration failures can introduce safety-relevant risk invisible in aggregate
accuracy metrics. All code, configurations, run artifacts, and the final report are in `project/`.

## Research Questions

**Primary hypothesis:** Quantization to INT4 degrades ECE by a greater relative magnitude than it
degrades macro F1 (`|Δ_ECE| > |Δ_F1|`), tested via paired bootstrap CI.

**Secondary hypothesis:** Temperature scaling applied post-quantization recovers ECE to ≤110% of
the FP16 baseline without materially reducing classification accuracy.

**Tertiary hypothesis:** Quantization increases prompt sensitivity (decreased inter-template
agreement, measured by Fleiss' kappa), and this effect is not recovered by post-hoc calibration.

## Key Results

The final experiment matrix completed 10 of 15 planned cells (FP16 × 5 templates, INT8 × 4
templates, INT4 × 1 template) at n=2000. Across all completed runs, macro-F1 ranges from
`0.038`–`0.095` and ECE from `0.336`–`0.704`, with 5/10 runs fully collapsed to
single-label (`BACKGROUND`) predictions. The primary hypothesis is conditionally supported on
the single completed INT4 cell (`point=0.098465`), but the sparse matrix prevents confirmation.
Secondary calibration recovery was not evaluated on the finalized evidence set. Full results and
honest limitations are in [`project/reports/final_report.md`](project/reports/final_report.md).

## Repository Structure

| Path | Contents |
|------|----------|
| `project/` | Final project: code, configs, data, results, and report |
| `project/src/reliability_eval/` | Core Python package (inference, metrics, calibration, reporting) |
| `project/reports/` | Final report (`final_report.md`), metrics, hypothesis tests, diagnostics |
| `project/artifacts/verification_runs/` | Committed run artifacts (5 representative runs, 200 predictions each) |
| `project/configs/` | YAML configs: datasets, model, precisions, prompts, calibration, sweeps |
| `project/data/` | Local data fixtures (`dev200`) and provenance JSON |
| `project/docs/` | Architecture, experiment protocol, data inventory, proposal, historical milestones |
| `project/scripts/` | Operational utilities (HF access, collapse diagnosis, subset generation) |
| `project/experiments/` | Run entrypoints and report generation scripts |
| `project/tests/` | Unit and integration tests (17 tests) |
| `assignments/` | Submitted course assignments (e.g., diabetes prediction) |
| `notes/` | Course notes and discussion write-ups |
| `papers/` | Reference papers (PDFs); see [papers/README.md](papers/README.md) |
| `presentations/` | Course paper presentations |
| `slides/` | Lecture slides |
| `certificates/` | Course completion certificates |
| `notebooks/` | Course Jupyter notebooks |

## Final Project Report

The primary deliverable is:

**[`project/reports/final_report.md`](project/reports/final_report.md)**

Supporting documents:

| File | Purpose |
|------|---------|
| `project/reports/final_metrics.md` | Per-run metrics table (accuracy, macro-F1, ECE, ACE) |
| `project/reports/hypothesis_tests.md` | Primary / secondary / tertiary hypothesis outcomes |
| `project/reports/run_ids_manifest.md` | Maps every numerical claim to a concrete `run_id` |
| `project/reports/preregistration.md` | Pre-registered hypotheses, decision rules, seeds |
| `project/reports/diagnostics/forensics_day1.md` | Day-1 forensic analysis of collapse structure |
| `project/artifacts/verification_runs/` | Committed per-run artifacts for claim traceability |

## Setup

All commands run from `project/`:

```bash
cd project
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"          # core + test dependencies
pip install -e ".[gpu,dev]"      # add GPU/inference extras for real runs
export PYTHONPATH=src
export RELIABILITY_ARTIFACT_ROOT=artifacts/runs
```

Run tests:

```bash
pytest tests/ -v
```

## Running the Core Pipeline

Single inference run (requires GPU with ≥16 GB VRAM for BioMistral-7B FP16):

```bash
python -m reliability_eval.cli run \
  --profile local_real \
  --dataset pubmed_rct_dev200 \
  --precision fp16 \
  --template pubmed_t2 \
  --calibration none \
  --sample-size 200
```

Regenerate final metrics tables and figures from committed verification artifacts:

```bash
python experiments/build_final_report.py \
  --artifact-root artifacts/verification_runs \
  --run-id final_pubmed_reliabi_20260427T152058_146948Z_a7088d \
  --run-id final_pubmed_reliabi_20260427T163632_548544Z_d14da3 \
  --run-id final_pubmed_reliabi_20260427T215337_743931Z_62dc21 \
  --run-id final_pubmed_reliabi_20260427T233449_389217Z_d16724 \
  --run-id final_pubmed_reliabi_20260428T142308_358498Z_334b78
```

Note: cross-precision figures (all 10 runs) require the full artifact bundle; see
`project/docs/reproducibility_note_template.md`.

## Known Limitations

- **10/15 matrix**: `int8/pubmed_t5` and `int4/pubmed_t2`–`t5` failed due to
  `bitsandbytes` runtime errors; only `int4/pubmed_t1` completed.
- **BACKGROUND collapse**: 5/10 runs predict a single label (`BACKGROUND`); macro-F1 is
  well below the preregistered `>0.20` pass threshold across all runs.
- **Secondary hypothesis not evaluated**: post-hoc calibration runs were not produced for
  the finalized n=2000 evidence set.
- **MedNLI deferred**: PhysioNet data-access constraints were not resolved; all experiments
  use PubMed RCT only.
- **Isotonic calibration deferred**: only temperature scaling was implemented.
- **No external artifact archive**: full raw run artifacts are local to the original GPU
  host and not committed to the repository.

## Course Materials

The rest of the repository contains Spring 2026 course materials:
`assignments/`, `notes/`, `papers/`, `presentations/`, `slides/`, `certificates/`, and
`notebooks/` are course deliverables and reference materials unrelated to the final project.
