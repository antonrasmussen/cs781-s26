# Audit: Comments, TODOs, and Prompt Templates

## Inline Comments and TODOs

### Summary
- **44 TODO/NotImplementedError** markers across `src/reliability_eval/`
- Comments generally align with docs: they describe planned work, not overstate current capability
- One potential drift: `pubmed_rct.py` docstring says "path_or_hf_id: Local JSONL file path or None to use tiny in-repo sample" but does not warn that an invalid path silently triggers fallback

### Key Comment Locations
| File | Comment / TODO | Aligns with docs? |
|------|----------------|-------------------|
| `run_mvp.py` | "TODO: Replace mock inference with real BioMistral scoring" | Yes |
| `score_class_codes.py` | "temporary mock inference path for MVP" | Yes |
| `pubmed_rct.py` | "TODO: Use split when full dataset integration is added" | Yes |
| `calibration.py` | No TODO; ECE implemented | Yes |
| `prompt_stability.py` | "Fleiss' kappa... TODO: Implement" | Yes |
| `template_registry.py` | "5 templates per task, validated on dev" | Docs say 5; only 2 exist for PubMed |

---

## Prompt Template Drift

### PubMed RCT
| Source | pubmed_t1 | pubmed_t2 |
|--------|-----------|-----------|
| `configs/prompts/pubmed_templates.yaml` | "Classify the following PubMed abstract sentence..." | "Assign the sentence to exactly one category..." |
| `src/reliability_eval/prompting/render.py` | Same body | Same body |

**Verdict**: Content matches. **Risk**: Two sources of truth; `render.py` does not load from YAML. Future edits could cause drift.

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
| `configs/datasets/pubmed_rct.yaml` | `"pubmed_rct"` (HF id) | `pubmed_rct.py` treats non-existent path as fallback to `data/samples/pubmed_rct_tiny.jsonl` |
| `configs/datasets/mednli.yaml` | `""` | MedNLI loader raises `NotImplementedError` |

**Verdict**: PubMed config suggests HuggingFace; MVP uses local tiny sample. Docs should clarify that current runs use the in-repo sample.

### Tests
- `test_prompt_rendering.py`: Asserts `pubmed_t1` output contains text, codes, "single letter" — matches docs
- `test_mvp_runner.py`: Asserts artifacts exist; does not assert `mode` or dataset provenance — metadata should be extended for clarity

---

## Recommendations
1. Add a single source of truth for prompt templates: either load from YAML in `render.py` or remove YAML and keep code as source.
2. Add a log/warning in `load_pubmed_rct` when falling back to tiny sample.
3. Extend `metadata.json` in MVP runs to include `mode: "mock_inference"` and `dataset_source: "pubmed_rct_tiny"`.
4. Add a test or docstring noting that `render.py` supports only `pubmed_rct` and `pubmed_t1`/`pubmed_t2`.
