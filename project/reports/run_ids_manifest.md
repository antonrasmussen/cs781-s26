# Run ID Manifest

This file maps each numerical claim in `reports/final_report.md` to concrete run artifacts.

## Current Matrix Status (sample_size=2000)

- Completed cells: 10/15
- Completed precisions/templates:
  - `fp16`: `pubmed_t1`..`pubmed_t5`
  - `int8`: `pubmed_t1`..`pubmed_t4`
  - `int4`: `pubmed_t1`
- Blocked/pending:
  - `int8 / pubmed_t5` failed repeatedly with `Int8Params.__new__() got an unexpected keyword argument '_is_hf_initialized'`
  - `int4 / pubmed_t2`..`pubmed_t5` remain pending; known quantized-loader instability includes `Tensor.item() cannot be called on meta tensors`

| Claim | Source run_id(s) | Notes |
| --- | --- | --- |
| FP16 dev200 collapse gate | `mvp_pubmed_reliabili_20260427T013747_627060Z_4dee78` | Canonical `pubmed_t5` gate run; non-collapsed but below macro-F1 threshold |
| FP16 prompt diagnostics | `mvp_pubmed_reliabili_20260427T014349_660880Z_31f1dd`, `mvp_pubmed_reliabili_20260427T015225_531206Z_81771d`, `mvp_pubmed_reliabili_20260427T015709_303244Z_015f0c`, `mvp_pubmed_reliabili_20260427T020314_217410Z_e356bd` | `t2` is strongest on dev200 but still sub-threshold |
| INT8 smoke viability | `mvp_pubmed_reliabili_20260427T020152_471563Z_3cda43` | Real-inference int8 smoke run completed on CUDA torch build |
| INT4 smoke viability | `mvp_pubmed_reliabili_20260427T020152_567211Z_7c8719` | Real-inference int4 smoke run completed on CUDA torch build |
| Primary hypothesis comparison | `reports/hypothesis_tests.md` (dev200 matrix), `final_pubmed_reliabi_20260427T152058_146948Z_a7088d`, `final_pubmed_reliabi_20260427T163632_548544Z_d14da3`, `final_pubmed_reliabi_20260427T171304_946963Z_04759a`, `final_pubmed_reliabi_20260427T211454_753565Z_82983f`, `final_pubmed_reliabi_20260427T215337_743931Z_62dc21`, `final_pubmed_reliabi_20260428T122312_645511Z_4cbeeb`, `final_pubmed_reliabi_20260428T142308_358498Z_334b78`, `final_pubmed_reliabi_20260428T155143_845589Z_bde23a`, `final_pubmed_reliabi_20260428T173219_254227Z_0dc4ed`, `final_pubmed_reliabi_20260427T233449_389217Z_d16724` | 2000-sample matrix stopped at 10/15 due to quantized-runtime failures on remaining cells |
| Secondary recovery claim | _pending calibration runs_ | `scripts/apply_calibration.py` implemented; calibration pass not started on 2000-sample runs |
| Tertiary kappa observation | `reports/hypothesis_tests.md` | Dev200 kappa for fp16/int8/int4 present; higher-sample confirmation partially complete (10/15) |
