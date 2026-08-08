# Evidence Registry (Frozen Snapshot)

Canonical inventory of manuscript-relevant evidence as of **2026-05-07** (verification subset export) / finalized n=2000 runs **2026-04-27–2026-04-28**.

This file freezes *what exists*, *where it lives*, and *which claims it supports*. It does **not** invent results.

Related: [`reports/run_ids_manifest.md`](../reports/run_ids_manifest.md), [`docs/manuscript_claim_boundaries.md`](manuscript_claim_boundaries.md), [`docs/reproducibility_note.md`](reproducibility_note.md), [`docs/environment.md`](environment.md).

Historical n=2000 configs used `hf_revision`/`revision: main`. Configs are now pinned to commit SHAs for **future** runs (see `docs/environment.md`); this does not rewrite frozen verification `resolved_config.yaml` files.

## Matrix status

| Precision | pubmed_t1 | pubmed_t2 | pubmed_t3 | pubmed_t4 | pubmed_t5 |
|-----------|-----------|-----------|-----------|-----------|-----------|
| FP16 | completed | completed | completed | completed | completed |
| INT8 | completed | completed | completed | completed | **blocked** |
| INT4 | completed | **blocked** | **blocked** | **blocked** | **blocked** |

- Completed cells: **10/15** at `sample_size=2000`, `calibration: none`, `inference_mode: real_inference`.
- Blocked: `int8/pubmed_t5` (`Int8Params.__new__() got an unexpected keyword argument '_is_hf_initialized'`); `int4/pubmed_t2`–`t5` (meta-tensor loader errors).

## Tracked in git (manuscript-usable)

| Artifact | Path | Role | Claim linkage |
|----------|------|------|---------------|
| Metrics table | `reports/final_metrics.md` | Per-run accuracy/macro-F1/ECE/ACE | Primary quantitative results |
| Hypothesis outcomes | `reports/hypothesis_tests.md` | Primary/secondary/tertiary decisions | Hypothesis section |
| Run ID map | `reports/run_ids_manifest.md` | Claim → run_id | Traceability |
| Report (PDF) | `reports/CS781_Final_Report_Anton_Rasmussen.pdf` | Canonical narrative | Submission |
| Report (TeX/MD) | `reports/final_report.tex`, `reports/final_report.md` | Source | Submission |
| Figures | `reports/figures/reliability_by_precision.png`, `recovery_plot.png`, `collapse_pattern.png` | Diagnostics | Results figures |
| Forensics | `reports/diagnostics/forensics_day1.md` | Collapse histograms | Collapse narrative |
| Verification subset | `artifacts/verification_runs/` + `manifest.json` | Metrics/config/sample preds/figures for all 10 runs | Audit without full JSONL |
| Data fixtures | `data/samples/pubmed_rct_dev200.jsonl`, `pubmed_rct_tiny.jsonl` | Dev gate / smoke | Gate runs |
| Provenance | `data/provenance/pubmed_rct_download.json`, `data/samples/pubmed_rct_dev200.provenance.json` | Dataset lineage | Methods |
| Preregistration | `reports/preregistration.md` | Locked decision rules | Protocol fidelity |

### Finalized n=2000 run IDs (verification subset)

| run_id | precision | template |
|--------|-----------|----------|
| `final_pubmed_reliabi_20260427T152058_146948Z_a7088d` | fp16 | pubmed_t1 |
| `final_pubmed_reliabi_20260427T163632_548544Z_d14da3` | fp16 | pubmed_t2 |
| `final_pubmed_reliabi_20260427T171304_946963Z_04759a` | fp16 | pubmed_t3 |
| `final_pubmed_reliabi_20260427T211454_753565Z_82983f` | fp16 | pubmed_t4 |
| `final_pubmed_reliabi_20260427T215337_743931Z_62dc21` | fp16 | pubmed_t5 |
| `final_pubmed_reliabi_20260427T233449_389217Z_d16724` | int4 | pubmed_t1 |
| `final_pubmed_reliabi_20260428T122312_645511Z_4cbeeb` | int8 | pubmed_t1 |
| `final_pubmed_reliabi_20260428T142308_358498Z_334b78` | int8 | pubmed_t2 |
| `final_pubmed_reliabi_20260428T155143_845589Z_bde23a` | int8 | pubmed_t3 |
| `final_pubmed_reliabi_20260428T173219_254227Z_0dc4ed` | int8 | pubmed_t4 |

Per-run tracked contents: `metadata.json`, `metrics.json`, `resolved_config.yaml`, `predictions_sample.jsonl` (200 rows), `figures/reliability.png`.

Canonical ID list for re-export: [`reports/verification_run_ids.txt`](../reports/verification_run_ids.txt).

## External / not tracked (full fidelity)

| Item | Location | Status |
|------|----------|--------|
| Full `predictions.jsonl` for n=2000 runs | CUDA host `artifacts/runs/` (git-ignored) | Available to author; **not** publicly archived |
| Full raw archive (zip/tar + SHA256) | — | **Missing** (see `docs/reproducibility_note.md`) |
| Dev200 / smoke `mvp_pubmed_reliabili_*` gate runs cited in `run_ids_manifest.md` | CUDA host / local ignored runs | Not in `verification_runs/` |

## Missing for stronger manuscript claims

| Gap | Why it matters | Required before claim |
|-----|----------------|----------------------|
| INT8/t5, INT4/t2–t5 cells | Incomplete primary/tertiary power | New experiments or permanently narrow claims |
| Calibrated n=2000 counterparts | Secondary (temperature recovery) unevaluated | Post-hoc calibration reruns |
| Flip-rate metric | Docstring-only in `prompt_stability.py` | Implement + compute, or drop claim |
| Efficiency (VRAM/latency/throughput) | `metrics/efficiency.py` is `NotImplementedError` | Implement + measure, or drop deployment-feasibility claim |
| MedNLI | Loader stub; DUA blocked | Unblock data or keep PubMed-only |
| Isotonic fit | `fit_isotonic` raises `NotImplementedError` | Implement or keep deferred |
| Exact HF commit SHAs at run time | Configs used `revision: main` / `hf_revision: main` | Pin SHA for *future* runs; historical numbers tied to `main` as of run dates |
| Environment lockfile | `pyproject.toml` uses version ranges | Lockfile / CUDA env snapshot |

## Historical / superseded (do not cite for final claims)

| Path | Status |
|------|--------|
| `reports/archive/milestone3/` (moved from `reports/m3_metrics.md`, `milestone_3_status.md`, obsolete figure) | Superseded by `final_metrics.md` / `final_report.*` |
| `reports/figures/m3_reliability.png` (zero-byte) | Obsolete; quarantined under archive |
| `experiments/build_m3_report.py` | Milestone helper only |

## Integrity checks

```bash
# From project/
python scripts/verify_claim_consistency.py
python scripts/validate_verification_subset.py
pytest tests/ -q
```
