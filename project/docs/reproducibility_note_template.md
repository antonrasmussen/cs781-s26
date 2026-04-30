# Reproducibility Note (Template)

Use this template in your report appendix, README, or submission note.

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

Full raw run artifacts are not tracked in git by default (to keep repo size manageable).  
Canonical archive location:

- Full artifact bundle (zip/tar): `<ARCHIVE_URL_PLACEHOLDER>`
- Optional mirrored location: `<MIRROR_URL_PLACEHOLDER>`
- Archive checksum (SHA256): `<CHECKSUM_PLACEHOLDER>`
- Archive date/version: `<ARCHIVE_VERSION_PLACEHOLDER>`

## Verification subset policy

`artifacts/verification_runs/` contains selected run directories with:

- `metadata.json`
- `metrics.json`
- `resolved_config.yaml`
- `predictions_sample.jsonl` (sampled first N rows)
- `manifest.json` (export summary)

This subset is intended for quick inspection and claim traceability; full reproduction uses the external archive.

## Command recipe: export selected runs into `artifacts/verification_runs/`

From repo root:

```bash
python scripts/export_verification_runs.py \
  --run-id <RUN_ID_1> \
  --run-id <RUN_ID_2> \
  --predictions-limit 200
```

Optional run-id file mode (one run ID per line, `#` comments allowed):

```bash
python scripts/export_verification_runs.py \
  --run-id-file reports/verification_run_ids.txt \
  --predictions-limit 200
```

Optional include reliability figures:

```bash
python scripts/export_verification_runs.py \
  --run-id-file reports/verification_run_ids.txt \
  --predictions-limit 200 \
  --include-figure
```

## Suggested run IDs for verification subset

Choose 2-5 runs that cover your main claims (example set):

- FP16 baseline best template: `<FP16_RUN_ID_PLACEHOLDER>`
- INT8 comparison template: `<INT8_RUN_ID_PLACEHOLDER>`
- INT4 available cell (if used): `<INT4_RUN_ID_PLACEHOLDER>`
- Collapse diagnostic example: `<COLLAPSE_RUN_ID_PLACEHOLDER>`

## Report linkage checklist

- `reports/run_ids_manifest.md` references each claim -> run_id.
- This note includes a reachable full archive URL.
- Verification subset manifest exists at `artifacts/verification_runs/manifest.json`.
- Any known missing cells / failed runs are explicitly documented.
