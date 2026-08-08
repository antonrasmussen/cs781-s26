# Reproducibility note

Submission-facing summary of what is in this repository, what is not, and how to audit the verification artifact subset.

See also: [`evidence_registry.md`](evidence_registry.md), [`manuscript_claim_boundaries.md`](manuscript_claim_boundaries.md), [`environment.md`](environment.md).

## What is in this repository

- Code and configs for the reliability evaluation pipeline.
- Final narrative/report files and summarized metrics:
  - `reports/final_report.md`
  - `reports/final_metrics.md`
  - `reports/hypothesis_tests.md`
  - `reports/run_ids_manifest.md`
  - `reports/verification_run_ids.txt` (canonical list of the 10 finalized run IDs)
- Small verification subset of run artifacts:
  - `artifacts/verification_runs/`
- Evidence freeze index:
  - `docs/evidence_registry.md`

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
- `figures/reliability.png` (when exported with `--include-figure`)
- `manifest.json` (export summary)

This subset is intended for quick inspection and claim traceability. Full reproduction may require access to the complete run directories on the execution host (see **What is stored outside the repository** above).

## Command recipe: export selected runs into `artifacts/verification_runs/`

From `project/`:

```bash
python scripts/export_verification_runs.py \
  --run-id <RUN_ID_1> \
  --run-id <RUN_ID_2> \
  --predictions-limit 200
```

Recommended: re-export the full finalized 10-run set from the ID file:

```bash
python scripts/export_verification_runs.py \
  --run-id-file reports/verification_run_ids.txt \
  --predictions-limit 200 \
  --include-figure
```

## Suggested run IDs for verification subset

The full finalized set is listed in `reports/verification_run_ids.txt`. Representative examples:

- FP16 baseline strongest template: `final_pubmed_reliabi_20260427T163632_548544Z_d14da3`
- INT8 comparison template: `final_pubmed_reliabi_20260428T142308_358498Z_334b78`
- INT4 available cell: `final_pubmed_reliabi_20260427T233449_389217Z_d16724`
- Collapse diagnostic example: `final_pubmed_reliabi_20260427T152058_146948Z_a7088d`

## Rebuild report tables/figures (no new inference)

If full `artifacts/runs/<run_id>/predictions.jsonl` files are available locally:

```bash
PYTHONPATH=src python -m reliability_eval.cli report \
  --artifact-root artifacts/runs \
  --run-id-file reports/verification_run_ids.txt \
  --expected-count 10
```

Equivalent direct script:

```bash
PYTHONPATH=src python experiments/build_final_report.py \
  --artifact-root artifacts/runs \
  --run-id-file reports/verification_run_ids.txt \
  --expected-count 10
```

## Integrity checks (no GPU required)

```bash
python scripts/verify_claim_consistency.py
python scripts/validate_verification_subset.py
pytest tests/ -q
```

## Report linkage checklist

- `reports/run_ids_manifest.md` references each claim → run_id.
- External archive: not published; see **What is stored outside the repository** above.
- Verification subset manifest exists at `artifacts/verification_runs/manifest.json`.
- Any known missing cells / failed runs are explicitly documented.
- Historical Milestone 3 outputs live under `reports/archive/milestone3/` and are not claim sources.

The editable template wording for reuse is `docs/reproducibility_note_template.md`.
