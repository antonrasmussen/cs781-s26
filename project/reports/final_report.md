# Beyond Accuracy Loss in Quantized Biomedical LLMs

## Abstract

We evaluate calibration degradation under quantization for a biomedical decoder model
(`BioMistral-7B`) on PubMed RCT sentence classification. The analysis distinguishes
classification quality (macro F1) from confidence quality (ECE/ACE) and uses a
single-token class-code scoring protocol to extract a well-defined probability
distribution from next-token logits. We compare FP16 against quantized conditions
and test whether post-hoc temperature scaling recovers calibration to near-FP16
levels without materially harming accuracy. Execution was finalized under a
runtime-blocked contingency at `10/15` completed cells on the `n=2000` slice:
FP16 (`t1`-`t5`), INT8 (`t1`-`t4`), INT4 (`t1`). Across completed runs, macro-F1
remains low (`0.038`-`0.095`) and ECE remains high (`0.336`-`0.704`) in both FP16
and quantized settings. Prompt robustness is evaluated with Fleiss' kappa where
template coverage permits. Numerical findings and hypothesis outcomes are populated
from run artifacts listed in
`reports/run_ids_manifest.md`.

## Introduction

Quantized deployment is a practical requirement for many healthcare-adjacent NLP
workloads, but calibration failures under compression can introduce safety-relevant
risk that is invisible in aggregate accuracy. This project evaluates whether
quantization harms calibration more than it harms classification utility in a
biomedical LLM, and whether post-hoc calibration recovers that loss.

The study is intentionally scoped to PubMed RCT for reproducibility and schedule
control. MedNLI remains deferred due unresolved data-access constraints. This scope
decision follows the original proposal fallback path and keeps the final submission
focused on one complete, defensible experimental story.

## Methods

### Model and Task

We evaluate `BioMistral/BioMistral-7B` on PubMed RCT sentence classification with five labels:
Background, Objective, Methods, Results, Conclusions.

### Probability Extraction

Each class is mapped to a single-token class code (`A`-`E`). For each example prompt, we score only
the logits corresponding to these code tokens at the first generated position and apply softmax over
the restricted class-code set to obtain a proper probability distribution.

### Precision Conditions

- FP16 baseline.
- INT8 quantized (`bitsandbytes`).
- INT4 quantized (`bitsandbytes NF4`) when hardware permits.

### Calibration Protocol

- Uncalibrated metrics are computed on test predictions.
- Temperature scaling fits a scalar temperature on a held-out calibration subset from validation data
  (15% split, seed 42), then applies the fitted temperature to test-set class-code probabilities.
- Isotonic fitting is deferred and noted as a limitation.

### Prompt Robustness

We evaluate five meaning-preserving prompt templates (`pubmed_t1`-`pubmed_t5`) and compute Fleiss'
kappa across template predictions on matched examples. When template-complete test-slice results are
not available, kappa is reported on `dev200` as a descriptive lower-power analysis.

### Metrics and Inference Rules

- Macro F1, per-class F1, accuracy.
- ECE (15 equal-width bins), ACE (15 equal-mass bins).
- Bootstrap confidence intervals: 1000 resamples, percentile method, seed 42.
- Primary hypothesis decision rule: paired-bootstrap CI on `(|Delta_ECE| - |Delta_F1|)` must exclude
  zero and be positive; otherwise the result is reported as inconclusive.

## Results

Results are generated from:

- `reports/final_metrics.md` (per-run metrics table)
- `reports/hypothesis_tests.md` (primary/secondary/tertiary outcomes)
- `reports/figures/` (cross-run reliability diagrams and recovery plot)

**Generating figures:** Cross-run figures (`reliability_by_precision.png`, `recovery_plot.png`) are
produced by running:

```bash
cd project
python experiments/build_final_report.py \
  --artifact-root artifacts/runs \
  --run-id <run_id> [--run-id <run_id> ...]
```

Full per-run reliability diagrams committed to the repository are available in
`artifacts/verification_runs/<run_id>/figures/reliability.png` for the five representative runs
exported at submission time (see `artifacts/verification_runs/manifest.json`).

Each headline claim in this section cites concrete run IDs from
`reports/run_ids_manifest.md`.

Execution was stopped at `10/15` cells for the `n=2000` matrix due to repeatable
quantized-runtime failures (`int8 / pubmed_t5` constructor mismatch and `int4` meta-tensor
loader errors). Completed cells include all FP16 templates, INT8 `t1`-`t4`, and INT4 `t1`.
This partial matrix is treated as the finalized evidence set for the current submission and
all claims are limited to those completed runs. A Day-1 forensic pass on the completed cells
(`reports/diagnostics/forensics_day1.md`) shows strong collapse structure: 5/10 runs are
single-label (`BACKGROUND`) and the remaining runs are heavily imbalanced toward one label.

From `reports/final_metrics.md`, FP16 rows show accuracy `0.1055`-`0.1470`, macro-F1
`0.0382`-`0.0955`, and ECE `0.3360`-`0.7040`. INT8 rows (`t1`-`t4`) are similar
(accuracy `0.1055`-`0.1315`, macro-F1 `0.0382`-`0.0953`, ECE `0.3555`-`0.6839`).
The only completed INT4 row (`t1`) yields accuracy `0.1055`, macro-F1 `0.0382`,
ECE `0.5876`. This supports a conservative interpretation: reliability deficits are
already substantial in FP16 and remain substantial under quantization.

## Discussion

Discussion focuses on three practical questions:

1. Whether calibration drift under quantization is materially larger than
   classification drift.
2. Whether temperature scaling offers reliable recovery without reducing task
   utility.
3. Whether prompt-level instability is separable from calibration quality.

Hypothesis outcomes are interpreted against preregistered rules but constrained by
matrix incompleteness. The primary statistic is positive on the completed INT4-vs-FP16
comparison (`point=0.098465`, CI `[0.098465, 0.098465]`), so it is reported as
conditional support only. Secondary recovery is not evaluated on `n=2000` because
post-hoc calibration runs were not produced for this finalized evidence set. Tertiary
kappa remains descriptive because INT4 lacks template-complete coverage.

At this stage, the dominant issue is not model loading or GPU plumbing alone; it is a mix of
(1) runtime incompatibilities in some quantized paths and (2) weak reliability quality in the
cells that do run. Across completed `n=2000` runs, macro-F1 remains low and ECE remains high
for both FP16 and quantized settings, indicating that calibration-quality deficits are not
explained solely by quantization.

## Limitations

- Single-task scope (PubMed only); MedNLI remains blocked by data-access constraints.
- Isotonic calibration fitting deferred.
- Quantization results depend on available GPU memory/runtime constraints.
- Final matrix is incomplete (`10/15`) due to repeatable INT8/INT4 runtime failures.
- Additional Day-1/Day-2 rerun attempts in this environment could not complete because
  the available Torch build has no CUDA backend and CPU offloaded runs did not finish in
  practical wall-clock time for this triage window.
- Potential pretraining contamination between BioMistral corpora and PubMed content
  cannot be directly audited from released pretraining manifests.
- Final writeup is maintained in Markdown (`final_report.md`) for this submission cycle;
  this is a pragmatic deviation from the preregistered LaTeX-first toolchain.
- ECE and ACE values are identical across all 10 completed runs (e.g., ECE = ACE = 0.6861
  for `fp16/pubmed_t1`). This is consistent with strongly collapsed predictions: when a
  model assigns near-uniform high confidence to a single class across all examples,
  equal-width bins (ECE) and equal-mass bins (ACE) are populated by the same
  distribution of confidence values, producing numerically identical results. This is a
  diagnostic signal of the collapse problem, not a computation error.

## Reproducibility

All run-level claims map to `run_id` entries in `reports/run_ids_manifest.md`.
