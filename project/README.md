# Reliability of Quantized Biomedical LLMs

Calibration and prompt stability under resource constraints for CS781 (Spring 2026).

## Current status (2026-04-24)

- Operative scope: **PubMed 20k RCT only**.
- MedNLI status: **BLOCKED** pending a lawful configured data path.
- Immediate gate: FP16 real inference on `dev200` with `pubmed_t5` must avoid BACKGROUND collapse.
- First-pass success criteria: `real_inference`, 200 predictions, non-collapsed class usage, `macro_f1 > 0.20`, calibration `none`.

## Research goal vs operational scope

The research goal is to evaluate reliability impacts of quantization on biomedical LLM classification, including calibration and prompt robustness analyses.

Current operational work is intentionally narrower: stabilize a trustworthy PubMed-first real-inference path before spending CUDA time on larger runs, quantized sweeps, or MedNLI.

## Quick links

- CUDA handoff runbook: `docs/cuda_pubmed_handoff.md`
- Data status and provenance: `docs/data_inventory.md`
- Active protocol: `docs/experiment_protocol.md`
- Architecture reference: `docs/architecture.md`
- Frozen proposal (design contract): `docs/proposal.md`

## Repo layout

- `src/reliability_eval/` — core package and canonical pipeline (`run_single`).
- `configs/` — datasets, model, precision, prompts, calibration, execution profiles, sweeps.
- `scripts/` — operational checks (HF access, audits, subset generation, collapse diagnosis).
- `experiments/` — helper entrypoints; for CUDA operations prefer the module CLI.
- `tests/` — unit/integration tests for config, loaders, prompting, metrics, and artifacts.
- `data/` — tracked local fixtures, `dev200`, and provenance JSON.
- `docs/` — operator-facing docs plus archived audit/milestone material.
- `artifacts/` — local run outputs (regenerate; not source of truth).
- `reports/` — generated status summaries and optional figures.
- `notebooks/` — exploratory support, not required for first CUDA gate.

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

Sanity tests:

```bash
pytest tests/ -v
```

First CUDA gate (PubMed `dev200`, FP16, real inference, no calibration):

```bash
python -m reliability_eval.cli run \
  --profile local_real \
  --dataset pubmed_rct_dev200 \
  --precision fp16 \
  --template pubmed_t5 \
  --calibration none \
  --sample-size 200
```

Inspect gate outputs and pass/fail criteria:

- Use `docs/cuda_pubmed_handoff.md` ("Inspect the collapse gate").

## Implemented vs deferred

Implemented and in active use:

- PubMed loader (HF and local JSONL), deterministic `dev200`, provenance logging.
- Real and mock inference paths, single-token class-code scoring, artifact writing.
- Macro/per-class F1, accuracy, ECE, reliability diagrams, Fleiss' kappa, temperature scaling.

Deferred until after the first CUDA gate passes:

- MedNLI data path and experiments.
- INT8/INT4 experiment runs for conclusions.
- ACE/bootstrap confidence intervals, isotonic calibration, full prompt-stability sweeps.
- CLI `report` implementation and summary-export polish.

## Current phase

Current phase: prompt and inference validation on `dev200` with real FP16 inference.  
Next phase: scale to broader PubMed evaluation only after the collapse gate passes.

## References

See `docs/proposal.md` section 9 for references and citations.
