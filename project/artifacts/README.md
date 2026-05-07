# Artifacts Overview

This directory contains experiment outputs used by the final report.

## What is tracked in this repository

- `artifacts/verification_runs/`
  - A curated verification subset for quick auditability.
  - Includes selected run directories with:
    - `metadata.json`
    - `metrics.json`
    - `resolved_config.yaml`
    - `predictions_sample.jsonl` (sampled rows)
    - `figures/reliability.png`
  - Includes `artifacts/verification_runs/manifest.json` summarizing exported runs.

## What is not tracked in this repository

- `artifacts/runs/` full raw run outputs are git-ignored by default.
- The complete artifact set (all run directories, full predictions, intermediate files)
  is available locally on the CUDA-enabled machine used to execute the full runs.

## Why this split is used

- Keeps the git repository manageable and fast to clone.
- Preserves a reproducible, claim-linked verification subset in version control.
- Retains full-fidelity raw artifacts on the CUDA host for deep audit/reproduction.

## Related files

- `reports/run_ids_manifest.md` maps report claims to run IDs.
- `docs/reproducibility_note.md` is the canonical reproducibility and artifact disclosure for submission.
- `docs/reproducibility_note_template.md` provides editable template language (source for the note above).
- `scripts/export_verification_runs.py` exports selected runs into `artifacts/verification_runs/`.

## Known artifact quirks

The `resolved_config.yaml` files in `artifacts/verification_runs/` contain Windows-format absolute paths (e.g., `config_dir: C:\Users\Strea\repos\...`) reflecting the execution host. These paths are metadata only and do not affect reproducibility — the configs directory is `project/configs/` in this repository.
