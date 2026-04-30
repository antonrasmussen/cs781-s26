# Reliability of Quantized Biomedical LLMs

Calibration and prompt stability under resource constraints for CS781 (Spring 2026).

## Final project state (April 2026)

- Operative scope: **PubMed 20k RCT only** (MedNLI blocked — see below).
- Experiment matrix: **10/15 cells completed** at n=2000 (FP16 × 5 templates, INT8 × 4 templates, INT4 × 1 template).
- Remaining cells (`int8/pubmed_t5`, `int4/pubmed_t2`–`t5`) failed due to repeatable `bitsandbytes` runtime errors.
- All 10 completed runs show strong BACKGROUND collapse; macro-F1 `0.038`–`0.095`, ECE `0.336`–`0.704`.
- Primary hypothesis: conditionally supported on the single INT4 cell; matrix too sparse for confirmation.
- Final report: `reports/final_report.md`.

## Research goal

Evaluate whether quantization of BioMistral-7B degrades calibration (ECE) more than classification quality (macro F1), and whether post-hoc temperature scaling recovers the calibration loss — across FP16, INT8, and INT4 precision conditions on PubMed RCT sentence classification.

## Quick links

- Final report: `reports/final_report.md`
- Final metrics table: `reports/final_metrics.md`
- Hypothesis outcomes: `reports/hypothesis_tests.md`
- Run-ID manifest: `reports/run_ids_manifest.md`
- Data status and provenance: `docs/data_inventory.md`
- Experiment protocol: `docs/experiment_protocol.md`
- Architecture reference: `docs/architecture.md`
- Original proposal (design contract): `docs/proposal.md`
- Historical CUDA handoff runbook: `docs/cuda_pubmed_handoff.md`

## Repo layout

- `src/reliability_eval/` — core package and canonical pipeline (`run_single`).
- `configs/` — datasets, model, precision, prompts, calibration, execution profiles, sweeps.
- `scripts/` — operational checks (HF access, audits, subset generation, collapse diagnosis).
- `experiments/` — helper entrypoints; for CUDA operations prefer the module CLI.
- `tests/` — unit/integration tests for config, loaders, prompting, metrics, and artifacts.
- `data/` — tracked local fixtures, `dev200`, and provenance JSON.
- `docs/` — operator-facing docs plus archived audit/milestone material.
- `artifacts/` — `verification_runs/` contains the committed subset (5 runs); full run outputs are local to the original GPU host.
- `reports/` — final report, metrics tables, hypothesis tests, diagnostics, and preregistration.
- `notebooks/` — exploratory support notebooks (`01_data_audit`, `02_prompt_template_dev`).

## Setup

From `project/`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
export PYTHONPATH=src
export RELIABILITY_ARTIFACT_ROOT=artifacts/runs
```

For CUDA hosts, install GPU extras:

```bash
pip install -e ".[gpu,dev]"
```

## Canonical commands

Run tests:

```bash
pytest tests/ -v
```

Single inference run (requires CUDA host with ≥16 GB VRAM for BioMistral-7B FP16):

```bash
python -m reliability_eval.cli run \
  --profile local_real \
  --dataset pubmed_rct_dev200 \
  --precision fp16 \
  --template pubmed_t2 \
  --calibration none \
  --sample-size 200
```

Regenerate final metrics, hypothesis tests, and figures from run artifacts:

```bash
python experiments/build_final_report.py \
  --artifact-root artifacts/runs \
  --run-id <run_id> [--run-id <run_id> ...]
```

See `reports/run_ids_manifest.md` for the canonical run IDs used in the final submission.

## Implemented (final state)

All of the following are implemented and used in the completed experiment runs:

- PubMed loader (HF and local JSONL), deterministic `dev200`, provenance logging.
- Real and mock inference paths, single-token class-code scoring, artifact writing.
- Macro/per-class F1, accuracy, ECE, ACE, reliability diagrams, Fleiss' kappa, temperature scaling.
- Bootstrap confidence intervals, paired bootstrap CI for hypothesis testing.
- Aggregation and report generation: `experiments/build_final_report.py`.

## Deferred / not completed

The following items were explicitly deferred and are out of scope for the final submission:

- **MedNLI**: PhysioNet data-access constraints were not resolved; `src/reliability_eval/data/mednli.py` raises `NotImplementedError`.
- **Isotonic calibration**: `fit_isotonic` raises `NotImplementedError`; only temperature scaling was run.
- **Secondary hypothesis**: post-hoc calibration runs were not produced for the finalized n=2000 evidence set.
- **INT8/pubmed_t5 and INT4/t2–t5**: blocked by repeatable `bitsandbytes` runtime errors.
- **CLI `report` command**: `_cmd_report` in `src/reliability_eval/cli.py` prints "not yet implemented".

## Final submission state

The n=2000 experiment matrix is finalized at 10/15 completed cells. All numerical claims in
`reports/final_report.md` trace to real run artifacts via `reports/run_ids_manifest.md`.
Representative run artifacts are committed to `artifacts/verification_runs/` for inspection.

