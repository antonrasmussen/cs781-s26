# Reproducibility note

Submission-facing summary of what is in this repository, what is not, and how to audit the verification artifact subset.

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

- Full artifact bundle (zip/tar): Not externally archived. Full run artifacts reside on the CUDA host used for execution. Contact the author for access.
- Optional mirrored location: N/A
- Archive checksum (SHA256): N/A — archive not available
- Archive date/version: Final runs completed 2026-04-28; verification subset exported 2026-04-30

## Verification subset policy

`artifacts/verification_runs/` contains selected run directories with:

- `metadata.json`
- `metrics.json`
- `resolved_config.yaml`
- `predictions_sample.jsonl` (sampled first N rows)
- `manifest.json` (export summary)

This subset is intended for quick inspection and claim traceability. Full reproduction may require access to the complete run directories on the execution host (see **What is stored outside the repository** above).

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

- FP16 baseline best template: `final_pubmed_reliabi_20260427T163632_548544Z_d14da3`
- INT8 comparison template: `final_pubmed_reliabi_20260428T142308_358498Z_334b78`
- INT4 available cell (if used): `final_pubmed_reliabi_20260427T233449_389217Z_d16724`
- Collapse diagnostic example: `final_pubmed_reliabi_20260427T152058_146948Z_a7088d`

## Report linkage checklist

- `reports/run_ids_manifest.md` references each claim -> run_id.
- External archive: not published; see **What is stored outside the repository** above.
- Verification subset manifest exists at `artifacts/verification_runs/manifest.json`.
- Any known missing cells / failed runs are explicitly documented.

The editable source for this note is `docs/reproducibility_note_template.md` (template wording for reuse).
