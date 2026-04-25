# Data inventory — PubMed 20k RCT & MedNLI

**Last updated (UTC):** 2026-04-25 (after running `scripts/verify_hf_access.py`, `scripts/download_pubmed_rct.py`, `scripts/make_dev_subset.py`, `scripts/validate_label_codes.py`, `scripts/audit_dataset.py`).

## Current operative scope

- **Primary:** PubMed 20k RCT (`armanc/pubmed-rct20k`, revision `main`) — HF access verified; full splits downloaded; deterministic dev subset `data/samples/pubmed_rct_dev200.jsonl` (200 rows, 40 per class).
- **Deferred:** MedNLI — **BLOCKED** (no PhysioNet path, no HF credential mirror confirmed; `load_mednli` remains `NotImplementedError`). Experiments and reporting proceed **PubMed-only** until unblocked.

---

## HF Access (`scripts/verify_hf_access.py`)

**Status:** OK (exit 0).

Captured output (abridged):

```
HF_ACCESS_OK
field_names: ['abstract_id', 'label', 'text', 'sentence_id']
first_record_raw: {"abstract_id": "24845963", "label": "background", "text": "This study analyzed liver function ...", "sentence_id": 0}
first_record_normalized: {"example_id": "24845963_0", "text": "This study analyzed liver function ...", "label": "BACKGROUND"}
```

**Implications for the loader:** The HF schema uses lowercase string `label` (e.g. `background`) and `text` (not `sentence`). There is no `label_text` column. The adapter in `src/reliability_eval/data/pubmed_rct.py` maps `abstract_id` + `sentence_id` to stable `example_id` values `{abstract_id}_{sentence_id}`.

---

## PubMed 20k RCT — provenance

- **Provenance file:** [`data/provenance/pubmed_rct_download.json`](../data/provenance/pubmed_rct_download.json)
- **Split sizes:** train 176,642; validation 29,672; test 29,578 (sentence-level rows; totals align with ~200k sentences across ~20k abstracts).
- **Observed HF fields:** `abstract_id`, `label`, `text`, `sentence_id`

### Label distribution (from `scripts/audit_dataset.py`)

| Split | n | BACKGROUND | OBJECTIVE | METHODS | RESULTS | CONCLUSIONS | sentences with `@` |
|-------|---|------------|-----------|---------|---------|---------------|---------------------|
| train | 176642 | 10.42% | 7.83% | 33.56% | 32.81% | 15.38% | 90050 |
| val | 29672 | 9.86% | 8.01% | 33.53% | 33.17% | 15.44% | 15336 |
| test | 29578 | 10.40% | 7.89% | 33.42% | 32.84% | 15.45% | 15161 |

**Macro F1:** The protocol uses **macro** F1 (not weighted) explicitly because RESULTS/METHODS dominate; this matches the imbalance documented above.

### Calibration split (15% of validation)

From `make_calibration_split(..., seed=42, calibration_fraction=0.15)` on the full validation set — class proportions vs full val (all deltas within ±2 percentage points):

| Label | val % | cal % | |Δ| |
|-------|-------|-------|-----|
| BACKGROUND | 9.86 | 9.64 | 0.22 |
| CONCLUSIONS | 15.44 | 16.52 | 1.07 |
| METHODS | 33.53 | 33.60 | 0.07 |
| OBJECTIVE | 8.01 | 8.22 | 0.22 |
| RESULTS | 33.17 | 32.02 | 1.14 |

### Token length sample (test, n=100/class, BioMistral tokenizer)

| Label | mean tokens | max | p95 | >512 tokens |
|-------|---------------|-----|-----|----------------|
| BACKGROUND | 35.8 | 100 | 63 | 0 |
| CONCLUSIONS | 33.4 | 63 | 55 | 0 |
| METHODS | 31.1 | 101 | 59 | 0 |
| OBJECTIVE | 40.4 | 117 | 74 | 0 |
| RESULTS | 39.9 | 193 | 86 | 0 |

Prompt framing adds ~20–30 tokens beyond sentence length.

### Dev subset

- **Path:** `data/samples/pubmed_rct_dev200.jsonl` (200 lines).
- **Method:** Stratified 40×5 from **test** split, per-class shuffle seeds derived from SHA256(`42|{label}`).
- **Sidecar:** `data/samples/pubmed_rct_dev200.provenance.json`

---

## MedNLI — status: BLOCKED

- **Canonical source:** Romanov & Shivade EMNLP 2018; distribution via **PhysioNet** under a **Data Use Agreement (DUA)**.
- **Repo state:** `configs/datasets/mednli.yaml` has `path_or_hf_id: null`. `src/reliability_eval/data/mednli.py` raises `NotImplementedError`. Prompt stubs in `configs/prompts/mednli_templates.yaml` have no `body` fields.
- **To unblock:** (a) Complete PhysioNet credentialing, download the official release to a **local path outside the repo**, set `path_or_hf_id` in a private overlay or env-specific config; **or** (b) confirm a Hugging Face mirror that satisfies the DUA and document the legal path.
- **No speculative loader** will be added until a path is confirmed.

---

## Single-Token Code Validation

**Script:** `scripts/validate_label_codes.py` — **exit 0** (`VALIDATE_LABEL_CODES_OK`).

`get_code_token_ids` (BioMistral tokenizer) selects the **`"{}"` bare-letter variant** (not `" {}"`) because space-prefixed letters are **two tokens** for this tokenizer.

**PubMed ordered token IDs (A–E):** `[330, 365, 334, 384, 413]` — five **distinct** single-token IDs.

**MedNLI (A–C):** `[330, 365, 334]` — three distinct IDs (subset of the PubMed code table).

**Per-variant encodings (representative):**

| Code | `"X"` | `" X"` | `"\nX"` | `"Answer: X"` |
|------|-------|--------|---------|----------------|
| A | 1 token | 2 tokens | 3 tokens | 3 tokens |
| … | (same pattern for B–E) | | | |

**Design note:** Prompts should terminate so the model predicts a **bare** class letter consistent with `get_code_token_ids` (e.g. end with “Answer with a single letter” without forcing a space before the letter).

---

## BACKGROUND-collapse diagnosis

**Evidence:** Real inference artifact [`artifacts/runs/mvp_pubmed_reliabili_20260423T034428_611367Z_603ebe/predictions.jsonl`](../artifacts/runs/mvp_pubmed_reliabili_20260423T034428_611367Z_603ebe/predictions.jsonl) (`metadata.json`: `inference_mode: real_inference`, n=8). **Every** row has `predicted_code: "A"` / `predicted_label: "BACKGROUND"` with confidence **0.71–0.86**, despite gold labels spanning RESULTS, CONCLUSIONS, etc.

**Not explained by n=8 alone:** The restricted distribution assigns high mass to token ID **330** (letter `A`) across heterogeneous sentences — systematic **collapse onto the first class code in the canonical legend** (`A=BACKGROUND`).

**Likely causes (ranked):**

1. **First-code / priming bias:** The inline legend leads with `A=BACKGROUND`, and the decoder places highest mass on token **A** at the answer position regardless of sentence semantics.
2. **Strong LM prior on “A”** at sentence boundaries: bare `A` is a single token; combined with (1), restricted softmax amplifies this.
3. **`@` masking:** Unlikely to be the sole cause (collapse also appears on sentences with few `@` tokens), but `@` correlates with RESULTS/METHODS (see audit counts) and may interact with calibration once the model stops collapsing.

**Recommended prompt-level mitigations (implemented as `pubmed_t3`–`pubmed_t5`):** numbered categories (`pubmed_t3`), question-before-answer ordering (`pubmed_t4`), and **non-alphabetic legend order with BACKGROUND last** (`pubmed_t5`). **Further diagnosis:** run `python scripts/diagnose_background_collapse.py` on a **CUDA** host (7B weights); compare scenarios `default_legend` vs `background_last_inline_legend` on the 8-example tiny fixture and on `pubmed_rct_dev200.jsonl` before any n>200 run.

---

## Calibration Risk Factors

1. **Class collapse:** If predictions use 1–2 codes only, ECE and temperature scaling are meaningless. **Gate:** do not fit temperature scaling unless uncalibrated macro F1 **> 0.20** on at least the dev200 slice (random 5-class baseline ≈ 0.20).
2. **Calibration split contamination:** Calibration rows must come **only** from validation via `make_calibration_split`; test rows must never enter the fit. `run_single.py` now partitions the validation loader output before `run_eval` for the temperature-scaling branch.
3. **Single-token collision:** Mitigated by `scripts/validate_label_codes.py` + `get_code_token_ids`; re-run after any tokenizer or template change.
4. **`@` masking:** ~51% of test sentences contain `@` (audit). Document per-class rates before interpreting calibration shifts.
5. **Temperature direction:** T<1 sharpens, T>1 smooths; under collapse, fitted T may be driven by a degenerate distribution — treat as a diagnostic, not a recovery claim.
6. **GPU / RAM:** Full BioMistral real inference requires a CUDA (or comparable) environment; local macOS dev in this repo is CPU-only for data scripts.

---

## Ready for Experiments

**First experiment to run:** FP16 real inference on **PubMed test** (or `pubmed_rct_dev200.jsonl` via local JSONL path) with **`pubmed_t5`** (or another non-collapsing template after smoke checks), `calibration: none`, `sample_size: 200` — **only after** single-token validation passes (done) and template smoke shows **non-collapsed** predictions on dev200.

**Example CLI (from repo root `project/`):**

```bash
export PYTHONPATH=src
export RELIABILITY_ARTIFACT_ROOT=artifacts/runs
# Use resolve_mvp_config / run_single with a profile that sets:
#   inference_mode: real_inference
#   dataset.path_or_hf_id -> JSONL path to pubmed_rct_dev200.jsonl OR HF id with sample_size 200
#   template_id: pubmed_t5
python experiments/run_mvp.py --sample-size 8 --template-id pubmed_t5 --profile local_real
```

(Adjust flags to match your resolved `local_real` profile once it points at `dev200` or HF test + `sample_size=200`.)

**Environment:** Linux **CUDA** (e.g. A10 / L4 or better), **≥16 GB VRAM** for FP16 7B + batching overhead; **≥32 GB RAM** if running CPU-only diagnostics.

**Remaining blockers:** (1) Confirm **non-collapsed** predictions on dev200 with at least one new template before scaling. (2) MedNLI remains blocked (optional for core PubMed hypothesis). (3) Isotonic / ACE / bootstrap CIs still deferred per milestone scope.

---

## Notebooks

- [`notebooks/01_data_audit.ipynb`](../notebooks/01_data_audit.ipynb) — re-runs audit-style checks and points here for canonical numbers.
- [`notebooks/02_prompt_template_dev.ipynb`](../notebooks/02_prompt_template_dev.ipynb) — template design notes + mock renders for `pubmed_t1`–`pubmed_t5`.
