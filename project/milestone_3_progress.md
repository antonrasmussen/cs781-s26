# CS781 - AI for Health Sciences

## Course Project Milestone 3: Research Progress Checkpoint

**Anton Rasmussen**  
Spring 2026  
Update Date: April 22, 2026

---

# 1. Project Title and Team

**Beyond Accuracy Loss: Measuring and Recovering Calibration Degradation in a Quantized Biomedical Large Language Model**

- **Author:** Anton Rasmussen (sole contributor)
- **Course:** CS781 - AI for Health Sciences, Spring 2026
- **Repository:** `cs781-s26` (project package `reliability_eval` under `project/src/`)
- **Milestone framing:** This report is a continuation of Milestone 2 with the same documentation and code-audit style.

---

# 2. Research Goal

The research question is unchanged from Milestone 2: whether post-training quantization of BioMistral-7B degrades calibration (ECE) more than macro F1, and whether post-hoc calibration can recover the degradation without comparable accuracy loss.

The scope intent is still PubMed 20k RCT first, MedNLI if feasible, with FP16/INT8/INT4 precision comparisons and class-code restricted softmax inference. Milestone 3 status is therefore evaluated against this same target, not against a narrowed or redefined objective.

---

# 3. Progress Update and Evidence

## 3.1 Completed Components (This Milestone)

The table below lists components that became newly implemented or newly validated since Milestone 2.

| Component | Evidence (file : function / artifact) | Research-goal link |
|-----------|----------------------------------------|--------------------|
| Real model loading path (FP16/INT8/INT4) | `src/reliability_eval/models/load_model.py` : `load_biomistral` | Enables actual model-backed probability extraction instead of mock-only scoring |
| Quantization sanity guard | `src/reliability_eval/models/quantization.py` : `assert_quantized_footprint` | Reduces risk of silent precision fallback that would invalidate quantization comparisons |
| Real restricted-softmax scorer | `src/reliability_eval/inference/score_class_codes.py` : `score_example` | Produces class-code probabilities required for ECE/F1 analysis |
| Real batch eval loop | `src/reliability_eval/inference/batch_runner.py` : `run_eval` | Connects dataset examples to model scoring and prediction artifacts |
| Code-token ID resolution for real tokenizer | `src/reliability_eval/models/tokenizer_utils.py` : `get_code_token_ids`; `tests/test_label_code_tokenization.py` | Resolves the Milestone 2 single-token mapping dependency for A-E/A-C class codes |
| Temperature-scaling fit/use in run pipeline | `src/reliability_eval/experiments/run_single.py` : temperature-scaling branch + `calibration_probs.jsonl` output | Moves calibration recovery from standalone utility to runnable experiment path |
| Minimal run aggregation/report generation | `src/reliability_eval/experiments/aggregate.py`, `src/reliability_eval/reporting/tables.py`, `experiments/build_m3_report.py`, `reports/m3_metrics.md` | Provides an auditable bridge from run artifacts to report-ready summary |
| Real-inference smoke artifacts | `artifacts/runs/mvp_pubmed_reliabili_20260423T034108_378616Z_fecfb0/`, `artifacts/runs/mvp_pubmed_reliabili_20260423T034428_611367Z_603ebe/` | Confirms end-to-end real forward pass + artifact writing path works at tiny sample sizes |
| Test suite expansion and status | `tests/test_calibration_apply.py` (`test_temperature_one_preserves_ece`), current run status: 39 passed | Improves confidence in calibration application behavior and overall pipeline correctness |

## 3.2 Overall Project Status

Milestone 3 materially advances the project from "mock-only end-to-end scaffold" (Milestone 2) to "real-inference code path implemented and smoke-executed." However, the work is still pre-experimental in the scientific sense because the available real runs are tiny FP16 probes (n=2 and n=8), with no INT8/INT4 runs and no n=200 validation gate completed.

| Research phase | Status | Detail |
|----------------|--------|--------|
| Infrastructure implementation | Substantially complete for MVP path | Real loader/scorer/eval path now exists and executes |
| Real experimental execution | Partially started (smoke only) | FP16 tiny real runs exist; no scale runs |
| Quantization comparison (FP16 vs INT8 vs INT4) | Not yet executed | INT8/INT4 code paths exist but no run evidence artifacts |
| Calibration recovery evaluation | Implemented in pipeline, not experimentally validated | Temperature scaling is wired; no real calibrated run artifact in reports table |
| Statistical hypothesis testing | Not started | No bootstrap CIs / paired tests yet |

## 3.3 Partially Complete

| Component | What Exists Now | What Is Missing |
|-----------|------------------|-----------------|
| PubMed real-data path | `load_pubmed_rct` can call HF dataset (`armanc/pubmed-rct20k`) and fallback to tiny sample when unavailable | Stable full-dataset execution at target sample sizes in GPU environment |
| Temperature-scaling workflow | Fit/apply is integrated in `run_single` for real inference and saves calibration probabilities | Real calibrated run outputs at planned n=200 + comparison table/figure integration |
| Real inference sanity checking | Optional greedy-vs-restricted-token alignment warning path in `batch_runner.py` | Systematic validation report across more prompts/examples |
| Milestone reporting utilities | `aggregate_metrics`, `metrics_table`, and `build_m3_report.py` generate M3 artifacts | Richer analysis outputs (comparative stats, confidence intervals, recovery ratios) |
| Tokenizer dependency closure | `test_tokenization_single_token` no longer xfail-based scaffold | Verification under quantized runs and alternate environments remains pending |

## 3.4 Not Started / Still Blocked

The following items remain unexecuted or blocked in the current repository state:

- **No GPU-backed scale runs:** `reports/milestone_3_status.md` explicitly documents lack of CUDA/MPS in this environment and inability to run the planned n=200 FP16/INT8 matrix.
- **No INT8 or INT4 experimental artifact evidence:** no run directories with reported INT8/INT4 metrics in `reports/m3_metrics.md`.
- **No MedNLI execution path completion:** `src/reliability_eval/data/mednli.py` still not implemented.
- **No isotonic fit implementation:** `src/reliability_eval/calibration/isotonic.py` : `fit_isotonic` still raises `NotImplementedError`.
- **No full prompt robustness study:** no 5-template PubMed sweep output, no Fleiss' kappa experimental section produced from real runs.
- **No advanced uncertainty analysis:** ACE, bootstrap CIs, and flip-rate analysis are still absent from current pipeline outputs.
- **CLI reporting command remains stubbed:** `src/reliability_eval/cli.py` : `_cmd_report` still prints "not yet implemented".

## 3.5 Real Experimental Status (Explicit Distinction)

This section separates (a) infrastructure implementation, (b) smoke validation, and (c) real experiment evidence.

### Implemented Infrastructure

- Real BioMistral loading and class-code scoring are implemented in source code.
- Temperature scaling can now be fit and applied within real inference runs.
- Artifact aggregation/report generation scripts exist and run.

### Validated Pipeline Behavior

- Real-inference smoke artifacts exist with `metadata.json -> inference_mode = "real_inference"`:
  - `mvp_pubmed_reliabili_20260423T034108_378616Z_fecfb0` (FP16, n=2)
  - `mvp_pubmed_reliabili_20260423T034428_611367Z_603ebe` (FP16, n=8)
- This demonstrates that the pipeline can execute actual forward passes and emit `predictions.jsonl`, `metrics.json`, `metadata.json`, and reliability figures.

### Real Experimental Results (What can and cannot be claimed)

- The n=8 run reports: accuracy `0.125`, macro F1 `0.074074`, ECE `0.669250`.
- These values are **not** treated as research findings because:
  1. sample size is far below the planned validation gate (200),
  2. only FP16 appears in evidence,
  3. no quantization comparison is present,
  4. no statistical uncertainty is computed.
- The observed BACKGROUND-dominant prediction pattern in the tiny run is treated as a diagnostic signal to investigate, not as a conclusion about model behavior on the full task.

---

# 4. What Changed Since Milestone 2

This section answers explicitly what was true at Milestone 2, what is newly true now, what remains unchanged, and whether the project advanced or stalled.

| Comparison question | Milestone 2 truth state | Milestone 3 truth state |
|---------------------|-------------------------|--------------------------|
| Was end-to-end pipeline available? | Yes, but mock scorer path only | Yes, with both mock and real scorer paths |
| Was BioMistral model loading implemented? | No (stub) | Yes (FP16/INT8/INT4 branches implemented) |
| Were class-code logits extracted from real model outputs? | No | Yes, in real `score_example` path |
| Did tokenizer single-token code mapping remain unresolved? | Yes (xfail placeholder) | No; tokenizer test now passes in environment |
| Were there any real-inference artifacts? | No | Yes (FP16 n=2 and n=8 smoke runs) |
| Were quantization experiments run? | No | Still no |
| Were calibration-recovery experiments run on real outputs? | No | Still no real calibrated results in artifacts summary |
| Was choke point purely missing implementation? | Yes | No; now shifted to compute access and scale execution |

**Net assessment:** the project has **materially advanced** in implementation maturity and liveness testing, but it has **not yet advanced to hypothesis-level experimentation**. The status is "bridged infrastructure, pending scaled execution."

---

# 5. Choke Point Analysis

## 5.1 Primary Bottleneck Shift

Milestone 2 identified one major blocker: implementing real model loading and scoring. In Milestone 3, that coding blocker is largely resolved. The primary bottleneck has shifted to **execution capacity and run scale**:

1. Obtain stable GPU environment for repeatable FP16/INT8 runs at n=200.
2. Verify INT8 (then INT4) runtime behavior under actual quantized loading.
3. Produce enough runs for comparative and calibrated analysis.

In short: the bottleneck is no longer writing inference infrastructure, but running enough valid experiments to test the hypotheses.

## 5.2 Risk Decomposition (Updated from Milestone 2)

- **Tokenizer behavior risk:** reduced (single-token mapping implemented and tested), but still worth rechecking under quantized runtime contexts.
- **Logit-position extraction risk:** reduced (implemented and smoke-executed), with optional generation sanity check now available.
- **Quantization configuration risk:** partially reduced (INT8 footprint guard added), but still unverified on real INT8/INT4 run artifacts.
- **Hardware dependency risk:** unchanged in principle and still active in practice; environment constraints currently prevent planned scale runs.

## 5.3 Current True Dependency Chain

The critical path is now:

`GPU access -> FP16 n=200 baseline -> INT8 n=200 comparison -> temperature-scaled repeats -> analysis outputs`

All downstream claim strength depends on crossing this chain with actual artifacts.

---

# 6. To-Do List for the Next Phase

The next phase should prioritize turning implemented infrastructure into defensible results.

1. **Run required PubMed experiments at target sample size (n=200):**
   - FP16 + no calibration
   - INT8 + no calibration
   - FP16 + temperature scaling
   - INT8 + temperature scaling
2. **Regenerate report artifacts** using `experiments/build_m3_report.py` after those runs.
3. **Validate quantization runtime assumptions** (especially INT8 footprint checks and run metadata consistency).
4. **Add uncertainty estimates** (bootstrap CIs) before making comparative claims.
5. **If time allows:** implement isotonic fit and include as secondary calibration method.

---

# 7. Fallback / Narrowed-Scope Plan

The fallback logic remains the realistic one stated in Milestone 2, updated to current status:

- **Primary credible scope:** PubMed-only, FP16/INT8, no-calibration vs temperature-scaling.
- **Deferred unless resources permit:** MedNLI integration, INT4 claims, full 5-template prompt stability study.
- **Stretch items:** isotonic fit, ACE, flip-rate analysis, broader template robustness matrix.

If constrained further, the most defensible final narrative is:
"implemented and partially validated real-inference reliability pipeline with initial FP16 smoke evidence, plus a focused PubMed FP16-vs-INT8 calibration study."

---

# 8. Experiment Pipeline Architecture

The existing architecture diagram (`pipeline_diagram.png`) is still structurally accurate. Compared with Milestone 2, the following nodes effectively moved from `[stub]` to `[done]` in code:

- `LoadModel`
- `Tokenizer code-token resolution`
- `Score class codes`
- `Batch run eval`
- `Temperature-scaling fit/apply path integration`
- `Minimal run aggregation/report table`

The diagram's downstream analysis/reporting breadth remains partly aspirational until scaled runs and statistical analysis are completed.

---

# 9. Questions for Peer Review

1. For this milestone stage, is it methodologically appropriate to frame n=2/n=8 real runs as "pipeline liveness evidence" only, with no performance interpretation?
2. Given current constraints, is prioritizing PubMed FP16/INT8 + temperature scaling (and explicitly deferring MedNLI/INT4) the best scientific trade-off for a credible final paper?
3. What minimum uncertainty reporting (e.g., bootstrap CI granularity) would you consider sufficient before accepting claims about relative ECE vs macro F1 degradation?

---

# References

- Dettmers, T., Lewis, M., Belkada, Y., & Zettlemoyer, L. (2022). LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale. *NeurIPS 2022*.
- Dettmers, T., Pagnoni, A., Holtzman, A., & Zettlemoyer, L. (2023). QLoRA: Efficient Finetuning of Quantized LLMs. *NeurIPS 2023*.
- Dernoncourt, F., & Lee, J.Y. (2017). PubMed 200k RCT: a Dataset for Sequential Sentence Classification in Medical Abstracts. *IJCNLP 2017*.
- Guo, C., Pleiss, G., Sun, Y., & Weinberger, K.Q. (2017). On Calibration of Modern Neural Networks. *ICML 2017*.
- Labrak, Y., Bazoge, A., Morin, E., Gourraud, P.-A., Rouvier, M., & Dufour, R. (2024). BioMistral: A Collection of Open-Source Pretrained Large Language Models for Medical Domains. *ACL 2024 Findings*.
- Romanov, A., & Shivade, C. (2018). Lessons from Natural Language Inference in the Clinical Domain. *EMNLP 2018*.
- Zadrozny, B., & Elkan, C. (2002). Transforming Classifier Scores into Accurate Multiclass Probability Estimates. *KDD 2002*.
