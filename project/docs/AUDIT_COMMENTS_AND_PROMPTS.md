# Audit: Comments, TODOs, and Prompt Templates

## Inline Comments and TODOs

### Summary
- **TODO / `NotImplementedError` tally (as of 2026-03-24):** see `docs/generated/audit_marker_count.txt`, produced by `python docs/scripts/gen_audit_todo_count.py` (use `--write` to refresh that file). Counts drift as the codebase changes; do not rely on a hard-coded number in prose alone.
- Comments generally align with docs: they describe planned work, not overstate current capability
- `pubmed_rct.load_pubmed_rct` emits a `UserWarning` when a truthy `path_or_hf_id` is not an existing local path before falling back to the in-repo tiny sample.

### Key Comment Locations
| File | Comment / TODO | Aligns with docs? |
|------|----------------|-------------------|
| `run_mvp.py` | "TODO: Replace mock inference with real BioMistral scoring" | Yes |
| `score_class_codes.py` | "temporary mock inference path for MVP" | Yes |
| `pubmed_rct.py` | "TODO: Use split when full dataset integration is added" | Yes |
| `calibration.py` | No TODO; ECE implemented | Yes |
| `prompt_stability.py` | Fleiss' kappa implemented; per-template flip rate still TODO | Yes |
| `template_registry.py` | "5 templates per task, validated on dev" | Docs say 5; only 2 exist for PubMed |

---

## Prompt Template Drift

### PubMed RCT
| Source | pubmed_t1 | pubmed_t2 |
|--------|-----------|-----------|
| `configs/prompts/pubmed_templates.yaml` | "Classify the following PubMed abstract sentence..." | "Assign the sentence to exactly one category..." |
| `src/reliability_eval/prompting/render.py` | Same body | Same body |

**Verdict**: Content matches. **Risk**: low — `render.py` resolves bodies via `template_registry` loading `configs/prompts/*.yaml`; keep YAML as the canonical template source.

### MedNLI
| Source | Status |
|--------|--------|
| `configs/prompts/mednli_templates.yaml` | Has `mednli_t1`, `mednli_t2` ids only; no `body` |
| `render.py` | Raises `ValueError` for `task != "pubmed_rct"` |

**Verdict**: MedNLI not supported in renderer; config is placeholder. Aligns with stubbed MedNLI loader.

---

## Dataset and Config References

### Dataset Paths
| Config | `path_or_hf_id` | Loader behavior |
|--------|------------------|-----------------|
| `configs/datasets/pubmed_rct.yaml` | `null` (YAML) until a real path/HF id is set | `pubmed_rct.py` warns and falls back to `data/samples/pubmed_rct_tiny.jsonl` when the path is missing |
| `configs/datasets/mednli.yaml` | `null` (YAML) | `mednli.load_mednli` is a stub and raises `NotImplementedError` |

**Verdict**: PubMed config suggests HuggingFace; MVP uses local tiny sample. Docs should clarify that current runs use the in-repo sample.

### Tests
- `test_prompt_rendering.py`: Asserts `pubmed_t1` output contains text, codes, "single letter" — matches docs
- `test_mvp_runner.py`: Asserts artifacts exist; does not assert `mode` or dataset provenance — metadata should be extended for clarity

---

## Recommendations
1. Keep prompt templates in YAML under `configs/prompts/` (loaded via `template_registry`); avoid duplicating bodies in Python.
2. ~~Add a log/warning in `load_pubmed_rct` when falling back to tiny sample.~~ Done (`warnings.warn`).
3. ~~Extend `metadata.json` in MVP runs~~ — MVP manifest includes `inference_mode`, `dataset_source`, etc.; keep contract tests in sync.
4. Add a test or docstring noting that `render.py` / template loading supports `pubmed_rct` and `pubmed_t1`/`pubmed_t2` first; MedNLI templates remain placeholder.
