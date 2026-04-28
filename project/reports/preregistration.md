# Final Project Preregistration

Date: 2026-04-26

## Locked Decisions

- Toolchain: LaTeX-first (`reports/final_report.tex`) with smoke artifact `reports/_toolchain_smoke.pdf`.
- Task scope: PubMed-only. MedNLI remains blocked and out of scope.
- Calibration scope: temperature scaling only. Isotonic fitting deferred.
- Seeds: 42 for sampling, splits, and bootstrap.

## Dataset and Sampling

- Headline test slice: stratified sample of 2000 examples from `armanc/pubmed-rct20k` test split (400/class).
- Development gate slice: `data/samples/pubmed_rct_dev200.jsonl`.
- If compute pressure requires reduction, fallback to n=1000 with widened CI disclosure.

## Hypotheses and Decision Rules

### Primary

`|Delta_ECE| > |Delta_F1|` at INT4 vs FP16 using paired bootstrap over template-wise deltas.

- Statistic: `(|Delta_ECE| - |Delta_F1|)`.
- Decision: supported only if 95% CI excludes 0 and is positive.
- If CI includes 0: report as inconclusive.

### Secondary

Temperature scaling recovers ECE to <=110% of FP16 baseline without materially harming accuracy.

- Decision: `ECE_calibrated / ECE_FP16 <= 1.10` and `|accuracy_cal - accuracy_uncal| <= 0.005`.

### Tertiary

Fleiss' kappa over five templates degrades under quantization and is not recovered by calibration.

- Decision: if confidence intervals overlap heavily, report descriptively and mark as underpowered.

## Statistical Settings

- Bootstrap: percentile CI, 1000 resamples, seed 42.
- ECE: 15 equal-width bins.
- ACE: 15 equal-mass bins.

## Failure Handling

- If INT4 fails but INT8 succeeds: reframe headline to calibration recovery on INT8.
- If both INT4 and INT8 fail: report FP16-only reliability study with explicit limitation.
- Run crashes must resume from partial `predictions.jsonl` checkpoint.
