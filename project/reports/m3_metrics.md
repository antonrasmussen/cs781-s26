# Matrix status snapshot (sample_size=2000)

- Completion: `10/15`
- Completed:
  - `fp16`: `pubmed_t1`, `pubmed_t2`, `pubmed_t3`, `pubmed_t4`, `pubmed_t5`
  - `int8`: `pubmed_t1`, `pubmed_t2`, `pubmed_t3`, `pubmed_t4`
  - `int4`: `pubmed_t1`
- Blocked/pending:
  - `int8 / pubmed_t5` failed with `Int8Params.__new__() got an unexpected keyword argument '_is_hf_initialized'`
  - `int4 / pubmed_t2`..`pubmed_t5` pending; recurrent quantized-loader error includes `Tensor.item() cannot be called on meta tensors`

For exact run IDs, see `reports/run_ids_manifest.md`.
