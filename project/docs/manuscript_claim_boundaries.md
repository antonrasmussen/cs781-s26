# Manuscript claim boundaries

Evidence-bounded statement of what the current repository **can** and **cannot** support for a conference manuscript. Source of truth for freeze: [`evidence_registry.md`](evidence_registry.md), [`reports/hypothesis_tests.md`](../reports/hypothesis_tests.md), [`reports/final_metrics.md`](../reports/final_metrics.md).

**Evidence set:** finalized partial matrix **10/15** cells at `n=2000`, uncalibrated, PubMed RCT only, BioMistral-7B.

## Supported (safe with current wording)

| Claim | Boundary language to use |
|-------|--------------------------|
| Reliability deficits appear in FP16 as well as quantized settings | Macro-F1 low (`0.038`–`0.095`) and ECE high (`0.336`–`0.704`) across completed cells |
| Prompt-template-driven label collapse dominates completed runs | 5/10 runs single-label BACKGROUND; forensics in `reports/diagnostics/forensics_day1.md` |
| Primary INT4 vs FP16 calibration-vs-F1 contrast is **conditionally / anecdotally** positive | Only `pubmed_t1` INT4 pair; degenerate CI `point=0.098465`; not a formal multi-template test |
| FP16/INT8 Fleiss’ κ is negative (poor template agreement) | Descriptive; κ reported where ≥2 templates exist |
| Pipeline produces claim-linked artifacts | Verification subset + run ID manifest + metrics table |

## Unevaluated (do not assert as results)

| Claim | Why blocked |
|-------|-------------|
| Temperature scaling recovers ECE after quantization (secondary) | No calibrated n=2000 counterparts in finalized set |
| Calibration recovery fails to restore prompt robustness | Requires calibrated multi-template runs |
| INT4 prompt stability worsens vs FP16 (formal tertiary) | INT4 lacks template-complete coverage |
| Full 3×5 precision×template matrix conclusions | 5 cells blocked by runtime failures |

## Unsupported / out of scope with current artifacts

| Claim | Gap |
|-------|-----|
| Quantization improves deployment feasibility (latency/VRAM/throughput) | `metrics/efficiency.py` not implemented |
| MedNLI generalization | Loader stub; PhysioNet DUA blocked |
| Isotonic calibration results | `fit_isotonic` not implemented |
| Per-sample flip-rate analysis | Mentioned in docstring only; not implemented |
| Exact bit-identical reproduction from fresh clone alone | Full raw runs external; historical configs used `main` tip |

## Required caveats in manuscript Methods/Limitations

1. PubMed-only; MedNLI deferred.
2. Matrix incomplete (`10/15`); blocked cells documented.
3. Secondary hypothesis **unevaluated**, not rejected.
4. Primary support is conditional on a single INT4 template pair.
5. Collapse-dominated regime: interpret quantization contrasts cautiously.
6. Efficiency claims omitted unless new measurements are added.

## Module scope markers (not manuscript-complete)

| Module | Status |
|--------|--------|
| `src/reliability_eval/data/mednli.py` | Intentionally unimplemented (DUA) |
| `src/reliability_eval/calibration/isotonic.py` `fit_isotonic` | Deferred / NotImplemented |
| `src/reliability_eval/metrics/efficiency.py` | Out of current manuscript scope |
| `src/reliability_eval/metrics/prompt_stability.py` flip rate | Not implemented; κ only |
| `configs/prompts/mednli_templates.yaml` | Placeholder IDs without bodies |
| `src/reliability_eval/reporting/export_summary.py` | Stub; use `experiments/build_final_report.py` / CLI `report` |

## Update rule

Do not expand “Supported” without new artifacts and a corresponding update to this file, `evidence_registry.md`, and `reports/run_ids_manifest.md`.
