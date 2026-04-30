# artifacts/verification_runs

This directory contains a committed verification subset of run artifacts for the five most
representative runs from the final n=2000 experiment matrix. It is the canonical in-repo
evidence base for the claims in `reports/final_report.md`.

## What is here

Each run subdirectory contains:

| File | Contents |
|------|----------|
| `metadata.json` | Run metadata: run_id, timestamps, inference_mode, dataset_source, code_version |
| `metrics.json` | Computed metrics: accuracy, macro_f1, per_class_f1, ECE, n_examples |
| `resolved_config.yaml` | Full resolved configuration at time of run |
| `predictions_sample.jsonl` | First 200 predictions (text, true_label, predicted_label, confidence) |
| `figures/reliability.png` | Per-run reliability diagram |

The top-level `manifest.json` records the export parameters and which files were copied.

## Committed runs

| run_id | precision | template | macro_f1 | ECE |
|--------|-----------|----------|----------|-----|
| `final_pubmed_reliabi_20260427T152058_146948Z_a7088d` | fp16 | pubmed_t1 | 0.0382 | 0.6861 |
| `final_pubmed_reliabi_20260427T163632_548544Z_d14da3` | fp16 | pubmed_t2 | 0.0955 | 0.3360 |
| `final_pubmed_reliabi_20260427T215337_743931Z_62dc21` | fp16 | pubmed_t5 | 0.0592 | 0.3764 |
| `final_pubmed_reliabi_20260427T233449_389217Z_d16724` | int4 | pubmed_t1 | 0.0382 | 0.5876 |
| `final_pubmed_reliabi_20260428T142308_358498Z_334b78` | int8 | pubmed_t2 | 0.0953 | 0.3555 |

All 10 finalized run IDs (including the remaining 5 not exported here) are in
`reports/run_ids_manifest.md`.

## Note on Windows paths in metadata.json

The `"figure"` field in each `metadata.json` contains a Windows absolute path from the
original GPU execution host, e.g.:

```json
"figure": "C:\\Users\\Strea\\repos\\cs781-s26\\project\\artifacts\\runs\\..."
```

This path is a local execution artifact and is **not reproducible** on another machine.
The actual per-run reliability diagrams are committed at
`artifacts/verification_runs/<run_id>/figures/reliability.png` and can be opened directly.

## Full artifact bundle

The complete raw run artifacts for all 10 finalized runs are not committed to the repository.
See `docs/reproducibility_note.md` for the full reproducibility policy and archive status.
