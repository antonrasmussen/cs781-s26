# CS781 – AI for Health Sciences

## Course Project Proposal

**Anton Rasmussen**
Spring 2026
Submission Date: February 17, 2026

---

# Project Title

**Beyond Accuracy Loss: Measuring and Recovering Calibration Degradation in a Quantized Biomedical Large Language Model**

---

# 1. Introduction and Motivation

Healthcare organizations increasingly seek to deploy large language models for clinical documentation support, triage, and biomedical literature analysis. A 7B-parameter model achieves strong zero-shot and few-shot performance on biomedical NLP tasks but requires approximately 14 GB of VRAM at FP16, exceeding the capacity of most commodity hardware. A 4-bit quantized variant of the same model fits within 3.5 GB, enabling deployment on consumer-grade GPUs or CPU-only infrastructure. Post-training quantization (PTQ) is therefore the most practical compression technique for resource-constrained clinical environments.

However, existing evaluations of quantized models focus almost exclusively on aggregate accuracy. In safety-critical settings, this is insufficient. Two properties matter at least as much as accuracy for clinical deployment:

1. **Calibration** — whether a model's predicted confidence aligns with its actual probability of being correct. A model that maintains 92% accuracy but assigns 99% confidence to its predictions (including the 8% it gets wrong) is actively dangerous in decision-support contexts.
2. **Prompt robustness** — whether a model produces stable predictions across semantically equivalent input phrasings. A model whose output flips when a clinician rephrases a question is unreliable regardless of its average accuracy.

Critically, the existing literature on quantization-induced calibration shift provides an observation but not a remedy. This project goes further: it measures calibration degradation under quantization, then evaluates whether standard post-hoc calibration methods (temperature scaling, isotonic regression) can *recover* the lost calibration — and at what cost. The distinction between "quantization breaks calibration" (known) and "post-hoc methods can fix it" (not established for quantized biomedical LLMs) is the core contribution.

In my professional work as a healthcare data engineer, I have observed that deployment decisions hinge on predictability and behavioral stability, not just aggregate scores. This project is designed to produce results that directly inform those decisions.

---

# 2. Problem Statement

**Primary hypothesis:** Post-training quantization of BioMistral-7B to INT4 precision degrades Expected Calibration Error (ECE) by a greater relative magnitude than it degrades macro F1 score, across both biomedical tasks.

**Operationalization:** Let Δ_ECE = (ECE_quantized − ECE_FP16) / ECE_FP16 and Δ_F1 = (F1_FP16 − F1_quantized) / F1_FP16. The hypothesis predicts |Δ_ECE| > |Δ_F1| at INT4, tested via paired bootstrap comparison.

**Secondary hypothesis:** Standard post-hoc calibration (temperature scaling) applied after quantization recovers ECE to within 110% of the full-precision baseline, without materially reducing classification accuracy (verified empirically).

**Tertiary hypothesis:** Quantization to INT4 increases prompt sensitivity — measured as decreased inter-template prediction agreement — relative to FP16, and this effect is *not* recovered by post-hoc calibration.

---

# 3. NLP Tasks

Two open-access biomedical classification benchmarks provide generalizability across task types and class structures.

## 3.1 PubMed 20k RCT (Sequential Sentence Classification)

PubMed 20k RCT (the 20,000-abstract subset of PubMed 200k RCT; Dernoncourt & Lee, 2017) contains approximately 200,000 labeled sentences from 20,000 structured medical abstracts. Each sentence is labeled with one of five rhetorical roles: Background, Objective, Methods, Results, or Conclusions.

**Why this task:**
* Open access, no credentialing required
* Well-established benchmark in biomedical NLP
* 5-class structure provides richer signal for calibration analysis than binary tasks
* Large volume supports stable bootstrap estimates

## 3.2 MedNLI (Medical Natural Language Inference)

MedNLI contains approximately 14,000 premise-hypothesis pairs derived from clinical text, labeled as entailment, contradiction, or neutral. It is the standard NLI benchmark for clinical language understanding.

**Why this task:**
* Tests compositional reasoning, not just pattern matching
* 3-class structure complements the 5-class PubMed task
* Clinical origin adds direct healthcare relevance

**Access note:** MedNLI is distributed via PhysioNet under a credentialed data use agreement (Romanov & Shivade, 2018). The author has verified PhysioNet access. In the event of credentialing delays, the project will proceed with PubMed 20k RCT as the sole evaluation task; its large volume and 5-class structure are sufficient for the core calibration analysis.

Using two tasks with different class structures and cognitive demands guards against conclusions that are artifacts of a single dataset.

---

# 4. Model

This project focuses on a single model to eliminate confounds between model architecture, pretraining corpus, and inference paradigm. All quantization effects are measured within the same model family, isolating precision as the independent variable.

| Model | Parameters | Architecture | Access |
|---|---|---|---|
| BioMistral-7B (Labrak et al., 2024) | 7B | Decoder (Mistral architecture) | Open (HuggingFace) |

**Why BioMistral-7B:**
* 7B parameters is the scale where quantization produces deployment-relevant savings (14 GB → 3.5 GB at INT4)
* Mistral architecture is widely deployed and well-supported by quantization tooling
* Biomedical continued pretraining provides domain relevance without requiring clinical data access
* Open weights with no usage restrictions
* Large enough that calibration behavior under compression is a genuine open question

**Reference baselines (not part of the quantization analysis):**
* **TF-IDF + Logistic Regression:** Non-neural reference to establish task difficulty
* These baselines contextualize BioMistral's absolute performance; they are not compared on calibration or quantization metrics

**Design rationale:** A multi-model comparison across parameter scales (e.g., 110M encoder vs. 7B decoder) was considered but rejected because architecture and inference paradigm differences would confound any scale-dependent finding. A single-model design isolates precision as the independent variable and allows the project to invest its time budget in methodological depth rather than breadth.

---

# 5. Methodology

## 5.1 Quantization Conditions

BioMistral-7B will be evaluated at three precision levels using a single quantization backend (bitsandbytes) to eliminate cross-backend confounds:

| Precision | Method | Notes |
|---|---|---|
| FP16 | Native (torch.float16) | Full-precision baseline |
| INT8 | bitsandbytes LLM.int8() (Dettmers et al., 2022) | Mixed-precision post-training quantization |
| INT4 | bitsandbytes NF4 (Dettmers et al., 2023) | 4-bit NormalFloat, double quantization enabled; weight quantization only (no LoRA adapters) |

**Why a single backend:** Different quantization backends (bitsandbytes, GPTQ, AWQ, llama.cpp) use different kernel implementations, dequantization strategies, and logit extraction interfaces. Using multiple backends would introduce a confound: observed differences could reflect backend implementation choices rather than precision effects. Restricting to bitsandbytes ensures that all logit extraction, probability computation, and calibration measurement flows through a single, consistent code path.

This yields 3 precision levels × 2 tasks × 5 prompt templates = 30 core experimental runs, plus calibration recovery experiments (30 additional runs with post-hoc calibration applied).

## 5.2 Probability Extraction (Critical Methodological Detail)

Calibration analysis requires well-defined probability distributions over class labels. For a decoder LM evaluated via prompting, this is non-trivial and represents a key methodological decision in this project.

**Approach: Single-token class code scoring.**

Each task's labels are mapped to single-token alphabetic codes that are guaranteed to tokenize as exactly one token:

| PubMed RCT | | MedNLI | |
|---|---|---|---|
| A → Background | | A → Entailment |
| B → Objective | | B → Contradiction |
| C → Methods | | C → Neutral |
| D → Results | | | |
| E → Conclusions | | | |

The prompt explicitly presents this mapping (e.g., "Classify the following sentence. A = Background, B = Objective, C = Methods, D = Results, E = Conclusions. Answer with a single letter.") and the model is scored on the logits of exactly the tokens {A, B, C, D, E} (or {A, B, C} for MedNLI).

For each input x:

1. Construct the prompt with x, the label-code mapping, and a completion cue
2. Run a single forward pass and extract the logit vector z at the first generated token position
3. Select the logits corresponding to the token IDs for the code tokens (e.g., "A", "B", "C", "D", "E")
4. Compute P(class_k | x) = softmax(z[token_id(code_k)]) over only the K code tokens

This produces a proper K-dimensional probability distribution suitable for ECE computation.

**Why single-token codes instead of natural-language label verbalizers?** Scoring the "first token of each label name" (e.g., first token of "Background", "Methods") introduces a fragile dependency on tokenizer behavior: multi-token labels, leading-space sensitivity, and shared first-token collisions can silently corrupt the probability distribution. Single-letter codes are each guaranteed to be a single token in any BPE tokenizer, avoiding this class of errors.

**Why not free-form generation?** Decoding full text and parsing the output introduces label noise, loses probability information, and makes calibration measurement ill-defined. Constrained token scoring avoids all three problems.

**Validation gate (Phase 1):** On 200 held-out examples, verify that (a) code-token probabilities sum to 1.0 after softmax over the restricted set, (b) the argmax of the code distribution matches the greedy-decoded output token, and (c) reliability diagrams are visually plausible at FP16. Experiments do not proceed until this gate passes.

## 5.3 Evaluation Framework

### 5.3.1 Classification Performance

* Macro F1 score (primary metric, accounts for class imbalance)
* Per-class F1 scores (to detect selective degradation on minority classes)
* Accuracy (secondary, for comparability with prior work)
* 95% bootstrap confidence intervals on all metrics (n=1000 resamples)

### 5.3.2 Calibration Analysis (Primary Contribution)

**Measurement:**
* Expected Calibration Error (ECE) with 15 equal-width bins
* Adaptive ECE (ACE) with 15 equal-mass bins as a robustness check (equal-width ECE can be unstable when confidence distributions are skewed)
* Reliability diagrams (predicted confidence vs. observed accuracy) for each precision level
* Calibration delta: relative change in ECE from FP16 to each quantized precision

**Recovery (the intervention):**

For each quantized model, post-hoc calibration will be applied to test whether quantization-induced miscalibration is recoverable:

* **Temperature scaling** (Guo et al., 2017): A single scalar T is optimized on a held-out calibration set (15% of validation data) to minimize negative log-likelihood. Applied at test time by dividing logits by T before softmax. Because temperature scaling preserves logit ordering, it should not materially change classification accuracy — but this will be verified empirically, since ties and numerical edge cases can produce marginal shifts.
* **Isotonic regression** (Zadrozny & Elkan, 2002): A non-parametric, per-class calibration method fit on the same held-out calibration set. More flexible than temperature scaling but can overfit on small calibration sets.

For each precision level and calibration method, the following will be reported:
* ECE (equal-width) and ACE (equal-mass) before and after post-hoc calibration. Reporting both guards against conclusions that depend on binning strategy; if the two metrics disagree directionally, this will be noted as a limitation.
* Recovery ratio: (ECE_uncalibrated − ECE_calibrated) / (ECE_uncalibrated − ECE_FP16). This is a derived summary statistic (not a community-standard metric) that measures what fraction of quantization-induced miscalibration was recovered. It is reported for interpretive convenience alongside the raw ECE values.
* Whether post-hoc calibration changed classification accuracy (expected to be negligible for temperature scaling; verified empirically)

### 5.3.3 Prompt Robustness Analysis (Secondary Contribution)

Prompt robustness measures whether the model produces stable predictions when the prompt's surface form varies but the task semantics are held constant. The key constraint is that all template variation must be strictly *meaning-preserving*: templates may rephrase instructions or reorder label-code mappings, but must not alter the implied task, add hints, or change the information available to the model.

**Design:**
* 5 prompt templates per task
* All templates share the same class-code mapping, input formatting, and answer-space constraint (single letter)
* Permitted variation: instruction synonym substitution (e.g., "Classify" vs. "Label"), sentence structure rearrangement, label-code presentation order
* Prohibited variation: adding reasoning cues, changing few-shot examples, altering the code-to-class mapping, or restructuring the task framing (these would measure instruction-following differences, not robustness)
* All templates validated on 50 held-out development examples per task to confirm that (a) all templates yield the same modal prediction on ≥90% of dev examples at FP16, and (b) no template produces systematically different class distributions. Templates failing this gate are revised or discarded.

**Metrics:**
* **Fleiss' kappa** (Fleiss, 1971) across the 5 templates (treated as independent "raters"), computed at each precision level. Kappa accounts for chance agreement and is more informative than raw agreement rate for multi-class tasks.
* **Sensitivity delta:** Change in Fleiss' kappa from FP16 to each quantized variant, with bootstrap confidence interval
* **Per-sample flip rate:** Fraction of test examples where the modal prediction (across templates) changes between FP16 and quantized

**Critical test:** After applying temperature scaling to the quantized model, re-run the prompt robustness analysis on the calibrated quantized model. If temperature scaling recovers calibration but does *not* recover inter-template agreement, this demonstrates that quantization introduces two distinct failure modes — one recoverable (miscalibration), one not (output instability) — which is a meaningful finding for deployment.

### 5.3.4 Efficiency Metrics (Supplementary)

Reported in a single summary table, not as a primary contribution:

* Model size on disk (MB)
* Peak GPU VRAM during inference (nvidia-smi, batch size 1 and 16)
* Inference latency (mean and p95, per-sample, batch size 1 and 16)
* Throughput (samples/second)

## 5.4 Statistical Rigor

* All classification and calibration metrics include 95% bootstrap confidence intervals (n=1000 resamples)
* McNemar's test for pairwise significance testing of accuracy between precision variants
* Paired bootstrap test for comparing ECE and F1 degradation magnitudes (testing the primary hypothesis directly)
* Results reported per-task throughout; no cross-task averaging
* All prompt template results reported individually to enable inspection of outlier templates

## 5.5 Controls and Validity Safeguards

* **No test-set prompt tuning:** Prompt templates are designed and validated exclusively on a held-out development subset (50 examples per task). No template selection or modification based on test-set performance.
* **Calibration set isolation:** The 15% calibration split used for temperature scaling / isotonic regression is drawn from the validation set and is never used for ECE evaluation. ECE is computed exclusively on the test set.
* **Deterministic decoding:** All inference uses temperature=0 (greedy decoding) to eliminate sampling variance. The only source of variation across templates is the prompt itself.
* **Contamination acknowledgment:** BioMistral-7B was pretrained on biomedical corpora that likely include PubMed abstracts overlapping with PubMed 20k RCT test examples. The pretraining corpus is not publicly released, making direct n-gram overlap analysis infeasible. This will be reported as a limitation. As a partial mitigation, FP16 zero-shot accuracy on PubMed RCT will be compared against published baselines; performance substantially above known benchmarks would suggest contamination.

---

# 6. Timeline and Milestones

Project Duration: February 17 – May 8, 2026

---

## Phase 1: Infrastructure, Data, and Probability Pipeline

**Feb 17 – Mar 2** (2 weeks)

* Download and preprocess PubMed 20k RCT; verify MedNLI access via PhysioNet (activate fallback if needed)
* Implement evaluation harness: F1 (macro + per-class), ECE (equal-width and adaptive), bootstrap CIs
* Implement single-token class code probability extraction for BioMistral-7B (see Section 5.2)
* **Validation gate (Section 5.2):** On 200 held-out examples, verify that code-token probabilities sum to 1.0, that the argmax matches greedy-decoded output, and that reliability diagrams are visually plausible at FP16. Do not proceed until this gate passes.
* Load BioMistral-7B at FP16; run sanity-check inference on both tasks
* Implement TF-IDF + Logistic Regression reference baseline

Deliverable: Working probability extraction pipeline, validated at FP16, with evaluation harness

---

## Phase 2: Full-Precision Baselines and Prompt Design

**Mar 3 – Mar 16** (2 weeks)

* Design and validate 5 prompt templates per task (meaning-preserving variation only; validated on 50 dev examples per task)
* Run full evaluation at FP16 on both tasks across all 5 templates
* Compute FP16 baselines: F1, ECE, reliability diagrams, Fleiss' kappa
* Measure FP16 efficiency metrics (VRAM, latency, throughput)
* Implement temperature scaling and isotonic regression; validate on FP16 (post-hoc calibration of a well-calibrated model should produce minimal change — this is a sanity check)

Deliverable: Complete FP16 baseline with calibration and robustness metrics

---

## Phase 3: Quantization Experiments

**Mar 17 – Apr 6** (3 weeks)

* Apply INT8 quantization via bitsandbytes; evaluate on both tasks across all 5 templates
* Apply INT4 (NF4) quantization via bitsandbytes; evaluate on both tasks across all 5 templates
* Record efficiency metrics at each precision level
* Compute calibration deltas and robustness deltas relative to FP16 baselines
* Apply temperature scaling and isotonic regression to INT8 and INT4 models; re-evaluate calibration
* Re-run prompt robustness analysis on calibrated quantized models
* **Checkpoint:** By Apr 1, INT8 results should be complete. If INT4 is causing technical problems, the project still has a complete INT8 story to tell.

Deliverable: Complete results matrix (3 precisions × 2 tasks × 5 templates × pre/post calibration)

---

## Phase 4: Analysis

**Apr 7 – Apr 18** (~2 weeks)

* Test primary hypothesis: paired bootstrap comparison of |Δ_ECE| vs |Δ_F1|
* Test secondary hypothesis: does temperature scaling recover ECE to within 110% of FP16 baseline?
* Test tertiary hypothesis: does Fleiss' kappa degrade under quantization, and does calibration recovery restore it?
* Construct reliability diagrams (FP16 vs INT8 vs INT4, before and after temperature scaling)
* Construct calibration recovery plots showing ECE trajectory across precision × calibration method
* Analyze per-class calibration to identify whether specific classes are disproportionately affected
* Compile efficiency summary table

Deliverable: Complete statistical analysis with tested hypotheses and publication-quality figures

---

## Phase 5: IEEE Report and Presentation

**Apr 19 – May 8** (3 weeks)

* Title and Abstract (150–250 words)
* Introduction with hypothesis statement and explicit scope
* Methods: reproducible experimental protocol, probability extraction methodology, calibration recovery procedure
* Results: with confidence intervals, reliability diagrams, recovery plots, robustness analysis
* Discussion: practical deployment recommendations, limitations, failed hypotheses (if any)
* References, Figures, Tables
* Finalize visualizations, clean and document code repository
* Record presentation video

Final submission due by May 8.

---

# 7. Expected Contributions

1. **Calibration degradation measurement:** Quantify whether post-training quantization disproportionately degrades calibration (ECE) relative to classification accuracy (F1) in a biomedical LLM, using a single-token class code scoring methodology that eliminates tokenizer-dependent verbalizer artifacts.
2. **Calibration recovery evaluation:** Determine whether standard post-hoc calibration methods (temperature scaling, isotonic regression) can recover quantization-induced miscalibration to near-full-precision levels — a question with direct deployment implications that has received limited systematic attention for quantized biomedical LLMs.
3. **Prompt robustness under quantization:** Quantify whether INT4 quantization amplifies prompt sensitivity (measured via Fleiss' kappa over 5 meaning-preserving templates), and whether this instability is independent of calibration — i.e., whether it persists even after post-hoc calibration.
4. **Methodological contribution:** Provide a validated protocol for extracting well-defined class probabilities from prompted decoder LMs under quantization via single-token class code scoring, enabling rigorous calibration analysis that is currently absent from most quantization benchmarks.

---

# 8. Alignment with Course Objectives

This project aligns directly with:

* AI applications in healthcare (biomedical NLP deployment under resource constraints)
* EHR and NLP (Weeks 11–12) — clinical language understanding and classification
* Explainable AI and evaluation — calibration as a measurable dimension of trustworthiness
* Applied AI in biomedical contexts — connecting model compression research to clinical deployment realities

The project contributes to the gap between model development and production deployment in resource-constrained healthcare environments, with emphasis on safety-relevant properties (calibration, robustness) rather than aggregate accuracy alone.

---

# 9. References

* Dettmers, T., Lewis, M., Belkada, Y., & Zettlemoyer, L. (2022). GPT3.int8(): 8-bit Matrix Multiplication for Transformers at Scale. *NeurIPS 2022*.
* Dettmers, T., Pagnoni, A., Holtzman, A., & Zettlemoyer, L. (2023). QLoRA: Efficient Finetuning of Quantized Language Models. *NeurIPS 2023*.
* Dernoncourt, F., & Lee, J.Y. (2017). PubMed 200k RCT: a Dataset for Sequential Sentence Classification in Medical Abstracts. *IJCNLP 2017*.
* Fleiss, J.L. (1971). Measuring nominal scale agreement among many raters. *Psychological Bulletin*, 76(5), 378–382.
* Guo, C., Pleiss, G., Sun, Y., & Weinberger, K.Q. (2017). On Calibration of Modern Neural Networks. *ICML 2017*.
* Labrak, Y., Bazoge, A., Morin, E., Gourraud, P.-A., Rouvier, M., & Dufour, R. (2024). BioMistral: A Collection of Open-Source Pretrained Large Language Models for Medical Domains. *ACL 2024 Findings*.
* Romanov, A., & Shivade, C. (2018). Lessons from Natural Language Inference in the Clinical Domain. *EMNLP 2018*.
* Zadrozny, B., & Elkan, C. (2002). Transforming Classifier Scores into Accurate Multiclass Probability Estimates. *KDD 2002*.
