# Reproducibility Note

**Status:** Filled in for final submission (April 2026). The placeholders below for external
archive URL, checksum, and mirrored location reflect the fact that no public external archive
was created; the canonical evidence set is the committed `artifacts/verification_runs/`
directory in this repository.

## What is in this repository

- Code and configs for the reliability evaluation pipeline.
- Final narrative/report files and summarized metrics:
  - `reports/final_report.md`
  - `reports/final_metrics.md`
  - `reports/hypothesis_tests.md`
  - `reports/run_ids_manifest.md`
- Small verification subset of run artifacts:
  - `artifacts/verification_runs/`

## What is stored outside the repository

Full raw run artifacts (all 10 finalized n=2000 runs) were produced on a GPU host and are not
committed to the repository to keep repo size manageable. No public external archive was
created for this submission cycle.

- Full artifact bundle: **not publicly archived** — artifacts remain local to the original GPU host.
- Canonical in-repo evidence: `artifacts/verification_runs/` (5 representative runs, 200
  predictions each, with metadata, metrics, config, and per-run reliability figures).
- Archive date/version: April 2026 final submission.

For a reviewer who needs to inspect raw predictions: the `artifacts/verification_runs/`
directory contains `predictions_sample.jsonl` (200 rows per run) for the five most relevant
runs, which is sufficient to verify the collapse structure and ECE/F1 values reported in
`reports/final_metrics.md`.

## Verification subset policy

`artifacts/verification_runs/` contains selected run directories with:

- `metadata.json`
- `metrics.json`
- `resolved_config.yaml`
- `predictions_sample.jsonl` (first 200 rows)
- `figures/reliability.png`
- `manifest.json` (export summary at root of `verification_runs/`)

This subset is intended for quick inspection and claim traceability.

**Note on `metadata.json` figure paths:** The `"figure"` field in each `metadata.json` contains
a Windows absolute path from the original execution host (e.g.,
`C:\Users\Strea\repos\cs781-s26\...`). This is an artifact of local execution and is not
reproducible on another machine. The actual reliability figures are committed directly under
`artifacts/verification_runs/<run_id>/figures/reliability.png`.

## Committed verification runs

The five runs in `artifacts/verification_runs/` are:

| run_id | precision | template | macro_f1 | ECE |
|--------|-----------|----------|----------|-----|
| `final_pubmed_reliabi_20260427T152058_146948Z_a7088d` | fp16 | pubmed_t1 | 0.0382 | 0.6861 |
| `final_pubmed_reliabi_20260427T163632_548544Z_d14da3` | fp16 | pubmed_t2 | 0.0955 | 0.3360 |
| `final_pubmed_reliabi_20260427T215337_743931Z_62dc21` | fp16 | pubmed_t5 | 0.0592 | 0.3764 |
| `final_pubmed_reliabi_20260427T233449_389217Z_d16724` | int4 | pubmed_t1 | 0.0382 | 0.5876 |
| `final_pubmed_reliabi_20260428T142308_358498Z_334b78` | int8 | pubmed_t2 | 0.0953 | 0.3555 |

These represent the FP16 best template (pubmed_t2), the collapse case (pubmed_t1), the
non-alphabetic legend template (pubmed_t5), the only completed INT4 cell, and the INT8 best
template. All 10 finalized run IDs are listed in `reports/run_ids_manifest.md`.

## Command recipe: export selected runs into `artifacts/verification_runs/`

From `project/`:

```bash
python scripts/export_verification_runs.py \
  --run-id <RUN_ID_1> \
  --run-id <RUN_ID_2> \
  --predictions-limit 200 \
  --include-figure
```

## Report linkage checklist

- [x] `reports/run_ids_manifest.md` references each claim → run_id.
- [x] Verification subset committed at `artifacts/verification_runs/`.
- [x] Verification subset manifest at `artifacts/verification_runs/manifest.json`.
- [x] Known missing cells and failed runs documented in `reports/run_ids_manifest.md`.
- [ ] Full external archive URL: **not applicable** (no public archive created).
