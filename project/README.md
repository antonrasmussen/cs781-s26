# Reliability of Quantized Biomedical LLMs

Calibration and prompt stability under resource constraints for CS781 (Spring 2026).

## Final state (2026-04-30)

- Real-inference experiments completed: **10/15** cells at **n=2000**.
- Completed: **FP16** (`t1`–`t5`), **INT8** (`t1`–`t4`), **INT4** (`t1` only).
- Blocked: **INT8/t5** (runtime mismatch), **INT4/t2**–**t5** (loader errors).
- **Canonical submission**: [`reports/CS781_Final_Report_Anton_Rasmussen.pdf`](reports/CS781_Final_Report_Anton_Rasmussen.pdf) | source: [`reports/final_report.tex`](reports/final_report.tex).
- Metrics table: [`reports/final_metrics.md`](reports/final_metrics.md).
- Hypothesis outcomes: [`reports/hypothesis_tests.md`](reports/hypothesis_tests.md).
- Figures: [`reports/figures/`](reports/figures/).

## Final submission artifacts

Quick navigation for graders:

| Artifact | Path | Purpose |
|---|---|---|
| Written report (PDF) | [`reports/CS781_Final_Report_Anton_Rasmussen.pdf`](reports/CS781_Final_Report_Anton_Rasmussen.pdf) | Canonical submission |
| Report source | [`reports/final_report.tex`](reports/final_report.tex) | IEEEtran LaTeX source |
| Run ID manifest | [`reports/run_ids_manifest.md`](reports/run_ids_manifest.md) | Claim → run\_id traceability |
| Metrics table | [`reports/final_metrics.md`](reports/final_metrics.md) | All 10 completed n=2000 runs |
| Hypothesis tests | [`reports/hypothesis_tests.md`](reports/hypothesis_tests.md) | Primary/secondary/tertiary outcomes |
| Reproducibility note | [`docs/reproducibility_note.md`](docs/reproducibility_note.md) | Verification policy and export recipe |
| Verification subset | [`artifacts/verification_runs/`](artifacts/verification_runs/) | Curated run artifacts (metrics, configs, samples) |

Full raw run artifacts are git-ignored (large); see `docs/reproducibility_note.md` for the access policy.

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

Real-inference runs require a CUDA-enabled GPU with at least 16 GB VRAM (BioMistral-7B at FP16). CPU-only inference is not practical at n=2000 scale.

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

**Completed:** PubMed loader, `dev200` subset, real inference (FP16/INT8/INT4), single-token class-code scoring, ECE/ACE/macro-F1, reliability diagrams, Fleiss' kappa, temperature scaling (implemented and validated on `dev200`, not applied at n=2000 due to compute constraints), bootstrap CIs.

**Not completed:** MedNLI (data access blocked), INT8/t5 and INT4/t2–t5 (runtime failures), temperature scaling at n=2000 (secondary hypothesis not evaluated), isotonic calibration (deferred).

## References

See `docs/proposal.md` section 9 for references and citations.
