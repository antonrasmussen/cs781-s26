# Milestone 3 Status (Real Inference Bridge)

Date: 2026-04-22

## What is now real (not mock)

- Real BioMistral loading is wired through `load_biomistral` for FP16 and quantized branches (`int8`/`int4`).
- Real class-code token id extraction is implemented and validated against the BioMistral tokenizer.
- Real first-token logit extraction with restricted softmax over class-code letters is implemented.
- Real batch evaluation is implemented and integrated into `run_single` under `inference_mode=real_inference`.
- PubMed loader now supports Hugging Face dataset loading (`armanc/pubmed-rct20k`) in addition to tiny local JSONL.
- A real FP16 run artifact exists with `inference_mode=real_inference`:
  - `artifacts/runs/mvp_pubmed_reliabili_20260423T034428_611367Z_603ebe/`
  - `metadata.json` shows `dataset_source=hf://armanc/pubmed-rct20k@main`
  - `n_examples=8`, with real `predictions.jsonl`, `metrics.json`, and `figures/reliability.png`

## Real-run evidence summary

- Run ID: `mvp_pubmed_reliabili_20260423T034428_611367Z_603ebe`
- Precision: FP16
- Dataset source: Hugging Face PubMed RCT (`armanc/pubmed-rct20k`, revision `main`)
- Template: `pubmed_t1`
- Sample size: 8 (reduced due hardware/runtime limits on local execution)
- Metrics:
  - accuracy: `0.125`
  - macro_f1: `0.07407407407407407`
  - ece: `0.66925048828125`

## Explicit deferrals and blockers

- MedNLI: deferred.
- Full split logic (`data/splits.py`): deferred.
- 5-template prompt sweep / Fleiss kappa on real runs: deferred.
- Aggregate report generation modules: deferred.
- Quantized real runs:
  - `int4` run failed in this local environment due quantized memory/device-map constraints.
  - `int8` run failed in this local environment due bitsandbytes/accelerate runtime incompatibility on this stack.
  - Recommendation: run `int8`/`int4` on CUDA Linux GPU runtime (Kaggle/Colab/Lambda/HPC).

## Notes on artifact interpretation

- Prior run folders in `artifacts/runs/` include mock outputs from milestone-2-era wiring (`inference_mode=mock_inference`).
- Milestone 3 claims should cite only runs where `metadata.json` has `inference_mode=real_inference`.
