# Feature / Claim Consistency Matrix

Maps documentation statements to implementation status. Status key: **implemented** | **stubbed** | **mock-only** | **duplicated** | **outdated**.

---

## Calibration

| Claim (from docs/proposal) | Source | Status | Evidence |
|----------------------------|--------|--------|----------|
| ECE with 15 equal-width bins | `docs/proposal.md`, `experiment_protocol.md` | **implemented** | `metrics/calibration.py`: `expected_calibration_error`, `reliability_bins` |
| ACE with 15 equal-mass bins | `docs/proposal.md` | **stubbed** | Not present in `calibration.py` |
| Reliability diagrams | `docs/proposal.md`, `architecture.md` | **implemented** | `reporting/reliability_diagrams.py` (with placeholder PNG fallback if matplotlib missing) |
| Temperature scaling | `docs/proposal.md` | **stubbed** | `calibration/temperature_scaling.py`: `fit_temperature` raises `NotImplementedError` |
| Isotonic regression | `docs/proposal.md` | **stubbed** | `calibration/isotonic.py`: `fit_isotonic` raises `NotImplementedError` |
| Calibration recovery ratio | `docs/proposal.md` | **stubbed** | Not implemented |
| Bootstrap CIs (n=1000) on metrics | `docs/proposal.md`, `experiment_protocol.md` | **stubbed** | Not in `classification.py` or `calibration.py` |

---

## Prompt Robustness

| Claim | Source | Status | Evidence |
|-------|--------|--------|----------|
| 5 meaning-preserving templates per task | `docs/proposal.md`, `experiment_protocol.md` | **outdated** | PubMed has 2 templates in `render.py` and `pubmed_templates.yaml`; MedNLI has 0 body templates |
| Fleiss' kappa across templates | `docs/proposal.md` | **stubbed** | `metrics/prompt_stability.py`: `fleiss_kappa` raises `NotImplementedError` |
| Per-sample flip rate | `docs/proposal.md` | **stubbed** | Not implemented |
| Template validation on 50 dev examples | `docs/proposal.md` | **stubbed** | Not implemented |

---

## Tasks and Datasets

| Claim | Source | Status | Evidence |
|-------|--------|--------|----------|
| PubMed 20k RCT (5-class) | `docs/proposal.md`, `README.md` | **mock-only** | `data/pubmed_rct.py` loads; MVP uses tiny sample; real dataset path not wired |
| MedNLI (3-class) | `docs/proposal.md` | **stubbed** | `data/mednli.py`: `load_mednli` raises `NotImplementedError` |
| Train/val/calib/test splits | `experiment_protocol.md`, dataset configs | **stubbed** | `data/splits.py`: `get_splits` raises `NotImplementedError`; `pubmed_rct.py` ignores `split` |
| Calibration fraction 15% from val | Configs, protocol | **stubbed** | Config has it; code does not use it |

---

## Inference and Model

| Claim | Source | Status | Evidence |
|-------|--------|--------|----------|
| Single-token class-code scoring (A–E, A–C) | `docs/proposal.md`, `architecture.md` | **mock-only** | `inference/score_class_codes.py`: `mock_score_example` used; `score_example` raises `NotImplementedError` |
| BioMistral-7B loading | `docs/proposal.md` | **stubbed** | `models/load_model.py`: `load_biomistral` raises `NotImplementedError` |
| FP16, INT8, INT4 quantization | `docs/proposal.md` | **stubbed** | `models/quantization.py`: `apply_quantization` raises `NotImplementedError` |
| Deterministic decoding (temperature=0) | `experiment_protocol.md` | **stubbed** | No real inference yet |
| Batch inference | `architecture.md` | **stubbed** | `inference/batch_runner.py`: `run_eval` raises `NotImplementedError` |

---

## Classification Metrics

| Claim | Source | Status | Evidence |
|-------|--------|--------|----------|
| Macro F1 | `docs/proposal.md` | **implemented** | `metrics/classification.py`: `compute_metrics` |
| Per-class F1 | `docs/proposal.md` | **implemented** | Same |
| Accuracy | `docs/proposal.md` | **implemented** | Same |
| Bootstrap CIs on F1/accuracy | `docs/proposal.md` | **stubbed** | Not implemented |

---

## Artifacts and I/O

| Claim | Source | Status | Evidence |
|-------|--------|--------|----------|
| Run outputs: predictions, metrics, figures | `README.md`, `architecture.md` | **implemented** | `io/artifact_store.py`, `run_mvp.py` |
| `resolved_config.yaml` | Code | **implemented** | Written as JSON (valid YAML); naming is slightly misleading |
| Run manifest / metadata | Code | **implemented** | `run_manifest.py`, `metadata.json` |

---

## Prompt Template Sources (duplication risk)

| Item | YAML config | Registry (`prompting/template_registry.py`) | Status |
|------|-------------|---------------------------------------------|--------|
| PubMed t1 | `configs/prompts/pubmed_templates.yaml` | PubMed template entry (e.g., `pubmed_t1`) in the template registry | **implemented** — template bodies live in the registry; YAML is loaded when `config_dir` is set |
| PubMed t2 | Same | PubMed template entry (e.g., `pubmed_t2`) in the template registry | **implemented** — same mechanism as PubMed t1 (registry + YAML when `config_dir` is set) |
| MedNLI | `mednli_templates.yaml` has ids only, no body | No corresponding full template bodies wired through the template registry/renderer | **stubbed** — MedNLI not yet supported end-to-end in the renderer |

---

## Summary

- **Implemented**: ECE, reliability diagrams, macro/per-class F1, accuracy, MVP artifact writing, PubMed data loader (with tiny-sample fallback), mock inference path, prompt template registry.
- **Mock-only**: Current runnable path uses mock scoring and tiny sample; artifacts are MVP/demo outputs, not real experimental results.
- **Stubbed**: ACE, bootstrap CIs, temperature scaling, isotonic regression, Fleiss' kappa, MedNLI, real model loading, quantization, batch inference, splits.
- **Outdated**: Docs claim 5 templates per task; only 2 PubMed templates exist.
- **Duplicated**: None currently known for prompt templates; bodies are centralized in `prompting/template_registry.py`, with YAML configs loaded when `config_dir` is set.
