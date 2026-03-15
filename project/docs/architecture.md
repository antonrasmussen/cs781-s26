# Architecture

Research question: **Reliability of quantized biomedical LLMs — calibration and prompt stability under resource constraints.**

## Module map

- **io**: Paths, artifact store, run manifests.
- **data**: Dataset adapters (PubMed RCT, MedNLI), splits (train/val/calib/test).
- **models**: Load BioMistral-7B; quantization (FP16, INT8, INT4 via bitsandbytes).
- **prompting**: Template registry, render, label codes (A–E / A–C).
- **inference**: Single-token class-code scoring; batch runner.
- **metrics**: Classification (F1, accuracy), calibration (ECE, ACE), prompt stability (Fleiss’ kappa), efficiency.
- **calibration**: Temperature scaling, isotonic regression, apply.
- **experiments**: run_single, run_grid, aggregate.
- **reporting**: Reliability diagrams, tables, export.
- **flyte**: Orchestration (Phase 5); thin wrapper over run_single / aggregate.

## Data flow

Config (YAML) → resolve → load data + model → run inference → compute metrics → write artifacts (predictions, metrics, figures).

## Decisions

- Local harness first; Flyte added after baseline works.
- Single-token class codes only (no natural-language verbalizers).
- One quantization backend (bitsandbytes).
