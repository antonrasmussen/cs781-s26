# Verification run subset

This directory holds a **curated verification subset** for the finalized **10/15** real-inference cells at **n=2000** (FP16 `t1`–`t5`, INT8 `t1`–`t4`, INT4 `t1`). Each subdirectory is one `run_id` exported from the full artifact tree.

**Full raw runs** (complete `predictions.jsonl`, all intermediate files) live under `artifacts/runs/` and are **git-ignored** by default; see the parent [artifacts README](../README.md).

## Per-run directory contents

Each `final_pubmed_reliabi_*` folder typically includes:

- `metadata.json` — run provenance and settings summary
- `metrics.json` — headline metrics for that run
- `resolved_config.yaml` — composed config (see quirks below)
- `predictions_sample.jsonl` — first *N* rows of predictions (export limit set at export time)
- `figures/reliability.png` — per-run reliability diagram (when exported with `--include-figure`)

## Manifest

[`manifest.json`](manifest.json) records the export: `run_count`, `predictions_limit`, per-run `copied_files`, and `prediction_rows_copied`.

## Known quirks

`resolved_config.yaml` may contain **Windows-format absolute paths** (e.g. `config_dir: C:\Users\...`) from the CUDA execution host. That is **metadata only**; canonical configs in git are under [`project/configs/`](../../configs/).

## Links

- Claim → run ID mapping: [`reports/run_ids_manifest.md`](../../reports/run_ids_manifest.md)
- Re-export or extend subset: [`scripts/export_verification_runs.py`](../../scripts/export_verification_runs.py)
- Parent overview: [`artifacts/README.md`](../README.md)
