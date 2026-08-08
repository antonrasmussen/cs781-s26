# Milestone 3 Status (Execution Update)

Date: 2026-04-23

## What was implemented in this pass

- Temperature-scaling calibration is now wired into the real pipeline in `src/reliability_eval/experiments/run_single.py`.
  - When `calibration.calibration == "temperature_scaling"` and `inference_mode == "real_inference"`, the runner:
    1) loads a validation calibration slice,
    2) fits `T` via `fit_temperature`,
    3) applies post-hoc scaling on test probabilities,
    4) writes `ece_calibrated` and `temperature`.
  - Calibration probabilities are saved to `calibration_probs.jsonl`.
- Quantized-load guard added:
  - `src/reliability_eval/models/quantization.py` now has `assert_quantized_footprint(...)`.
  - `src/reliability_eval/models/load_model.py` now calls this check for `int8` to detect silent fallback to higher precision.
- Minimal aggregation/reporting path implemented:
  - `src/reliability_eval/experiments/aggregate.py` now aggregates real-inference runs from `artifacts/runs`.
  - `src/reliability_eval/reporting/tables.py` now renders a simple markdown metrics table.
  - New script `experiments/build_m3_report.py` generates:
    - `reports/m3_metrics.md`
    - `reports/figures/m3_reliability.png`
- Test coverage update:
  - Added regression test `test_temperature_one_preserves_ece` in `tests/test_calibration_apply.py`.
  - Targeted tests pass in this environment: `21 passed`.

## Current real-inference evidence in repo

Real-inference runs currently available for milestone reporting:

- `artifacts/runs/mvp_pubmed_reliabili_20260423T034108_378616Z_fecfb0/` (FP16, n=2)
- `artifacts/runs/mvp_pubmed_reliabili_20260423T034428_611367Z_603ebe/` (FP16, n=8)

Generated summary artifacts (from those run IDs):

- `reports/m3_metrics.md`
- `reports/figures/m3_reliability.png`

## Honest blocker status

- This execution environment has no CUDA or MPS backend (`torch.cuda.is_available() == False`, `mps_available == False`), so Milestone 3 target runs (`n=200` FP16 and `n=200` INT8) could not be executed here.
- Hugging Face network/cache access is restricted in this environment; `load_pubmed_rct` now gracefully falls back to the in-repo tiny sample when HF loading fails.

## Required final Milestone 3 runs (still pending on cloud GPU)

Run these on Colab Pro / Lambda / HPC CUDA Linux:

1. FP16 real inference, PubMed, `n=200`, calibration `none`.
2. INT8 real inference, PubMed, `n=200`, calibration `none`.
3. FP16 real inference, PubMed, `n=200`, calibration `temperature_scaling`.
4. INT8 real inference, PubMed, `n=200`, calibration `temperature_scaling`.

Then regenerate:

- `reports/m3_metrics.md`
- `reports/figures/m3_reliability.png`

## Deferrals retained (intentional)

- INT4 runs: deferred to final report phase.
- MedNLI integration: deferred.
- Isotonic fit (`fit_isotonic`): deferred.
- 5-template PubMed sweep and Fleiss' kappa claims: deferred.
- Bootstrap CIs, ACE, and flip-rate analysis: deferred.
