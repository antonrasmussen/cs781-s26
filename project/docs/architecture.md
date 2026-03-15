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
- **flyte**: Orchestration; thin wrapper over run_single. Optional; works without Flyte.
- **config**: Config resolution and execution profiles (local, flyte_sandbox, odu).

## Data flow

Config (YAML) → resolve → load data + model → run inference → compute metrics → write artifacts (predictions, metrics, figures).

## Execution modes

- **Local**: Plain Python; no Flyte. `run_mvp`, `run_local`, `run_grid`, CLI.
- **Flyte sandbox**: Local Flyte; thin tasks call `run_single`. No GKE/remote cluster.
- **ODU compute**: Same code; run scripts with `--profile odu` on ODU nodes. Plain remote compute, not Flyte control plane.

See `docs/execution_modes.md`.

## Decisions

- Local harness first; Flyte optional.
- Single-token class codes only (no natural-language verbalizers).
- One quantization backend (bitsandbytes).
