---
name: Triage CS781 Final Salvage
overview: Plan-only triage. The repo already has 10/15 real n=2000 runs, all collapse-failing. One last targeted debug attempt to break BACKGROUND collapse on dev200; one cheap int4/t2 retry; otherwise finalize a defensible report against the existing evidence.
status_note: "This triage plan was fully executed 2026-04-29/30. All todos are completed. Final state: 10/15 matrix finalized, report written, repository cleanup done."
todos:
  - id: day1-env
    content: "Day 1: Stand up GPU env per docs/cuda_pubmed_handoff.md (pip install [gpu,dev], PYTHONPATH=src, RELIABILITY_ARTIFACT_ROOT)."
    status: completed
  - id: day1-diag
    content: "Day 1 morning: Run scripts/diagnose_background_collapse.py and capture stdout to reports/diagnostics/collapse_day1.log. Verify code_token_ids decode A..E and are distinct."
    status: completed
  - id: day1-templates
    content: "Day 1: Use existing real dev200 runs for t3/t4/t5 comparison and raw prediction inspection; gate decision based on observed collapse behavior."
    status: completed
  - id: day1-gate
    content: "Day 1 EOD gate: macro_f1 > 0.20 on dev200 with multi-class predictions => proceed to a clean baseline. Else => commit to salvage path with the existing 10/15 evidence."
    status: completed
  - id: day2-baseline
    content: "Day 2: Attempt canonical FP16 dev200 baseline rerun (time-boxed under current runtime constraints)."
    status: completed
  - id: day2-int8
    content: "Day 2: Attempt INT8 condition (~30 min debug budget); cut if runtime mismatch reproduces."
    status: completed
  - id: day2-cal
    content: "Day 2: Attempt FP16 + temperature scaling using pubmed_rct (HF) for validation split."
    status: completed
  - id: day3-aggregate
    content: "Day 3: Re-run experiments/build_final_report.py on finalized real run IDs and verify final metrics/hypothesis/figure outputs."
    status: completed
  - id: day3-manifest
    content: "Day 3 morning: Cross-check reports/run_ids_manifest.md against ls artifacts/runs/. Trim or annotate any rows whose run_ids are not on disk; add any new Day 1/2 runs."
    status: completed
  - id: day3-report
    content: "Day 3 afternoon: Rewrite reports/final_report.md against actual numbers. Pick scenario (1, 2, 3, or 'fix-found') from section G. Make every numeric claim trace to a real metrics.json."
    status: completed
  - id: day4-format
    content: "Day 4: Keep markdown-first report path and document deviation from LaTeX-first preregistration in final report limitations."
    status: completed
  - id: day4-commit
    content: "Day 4 afternoon: Single clean commit covering reports/ and any new runs under artifacts/runs/."
    status: completed
isProject: false
---

# Triage Plan v2: Salvage cs781-s26 Final Project

Mode: PLAN-ONLY, TRIAGE. No edits, no execution.

## Repo State (corrected)

- `[artifacts/runs/](cs781-s26/project/artifacts/runs)` contains 64 run directories with `metadata.json`, `metrics.json`, `predictions.jsonl`, `resolved_config.yaml`. The 10 cells cited in `[reports/run_ids_manifest.md](cs781-s26/project/reports/run_ids_manifest.md)` all resolve to real artifacts on disk.
- All 10 finalized n=2000 runs (`final_pubmed_reliabi_*`) used `inference_mode: real_inference`, `dataset_source: hf://armanc/pubmed-rct20k@main`. They are real, not mocks.
- All 10 fail the preregistered `macro_f1 > 0.20` collapse gate. Best is FP16 `pubmed_t2` at `macro_f1 = 0.0955`. Worst (t1, t4) shows `per_class_f1 = {BACKGROUND: 0.19, all others: 0.0}` — pure single-class output.
- Sampled FP16 t1 rows: model predicts `A` with confidence 0.71–0.84 even on RESULTS sentences. Restricted softmax shape is dominated by A.
- 5 cells missing from the matrix: `int8/pubmed_t5`, `int4/pubmed_t2..t5`. Errors logged in manifest: `Int8Params.__new__()` kwargs mismatch and `Tensor.item() cannot be called on meta tensors`.
- Preregistration target is HF n=2000, not dev200. dev200 remains the right vehicle for fast Day 1 debug iteration only.

User decisions locked:
- 4 days available.
- GPU is available (prior host or equivalent).
- Day 1 fix candidate is decided after reading the diagnostic log, not pre-committed.
- Submission format: Markdown (`reports/final_report.md`); user handles final formatting.
- Fix-Found combination: pick whatever is defensible AND least compute-intense (i.e. one n=200 post-fix dev200 baseline plus the existing pre-fix n=2000 matrix as a documented bug-trail; no full n=2000 post-fix re-run).

## A. Strategic Read

- Best realistic outcome: Day 1 fix breaks collapse on dev200 (`macro_f1 > 0.20`), we add one clean FP16 dev200 baseline, frame existing 10/15 as a documented bug-trail, and ship a strong narrative.
- Minimum acceptable outcome: Day 1 fix fails, we keep the 10/15 evidence, finalize honest negative-result framing with cleaned manifest and aggregated tables.
- Dominant risk: Day 1 fix consumes a day, doesn't help, and we have less time for writing.

## B. GPU / Compute Plan

- Primary: same GPU host that produced the 10 existing runs (BioMistral-7B FP16/INT8 already loaded successfully there). No new env work needed.
- Fallback: Colab Pro / Lambda single A100/L4 (~16 GB sufficient for FP16). Day 2 int4 retry needs `bitsandbytes` rebuild against the loaded `transformers` version.
- If the prior GPU host is gone, this becomes Risk #1.

## C. Day-by-Day Plan

Written for ~4 days available. If less, drop the Day 1 fix attempt and go straight to forensics + Day 2.

- Day 1 — DIAGNOSE + ONE FIX ATTEMPT (must include all of these)
  - Forensics on existing 10 runs (no GPU needed): for each `final_pubmed_reliabi_*` dir, compute predicted-label histogram, mean confidence on A vs {B,C,D,E}, and per-class F1 from `metrics.json`. Tabulate by (precision, template). Conclusion target: which template/precision combos collapse fully (e.g. t1, t4) versus partially (e.g. t2 at macro_f1 ~0.095).
  - Run collapse diagnostic and capture stdout:
  `python scripts/diagnose_background_collapse.py --model BioMistral/BioMistral-7B 2>&1 | tee reports/diagnostics/collapse_day1.log`. Key checks: `code_token_ids` are distinct, decode round-trips to A..E, restricted softmax is not pre-determined to A by raw logits.
  - Inspect raw logits + top-k token probabilities. The diagnostic already prints restricted A..E logits and softmax. Compare against unrestricted top-k by adding a one-line print of `last_logits.topk(10)` mentally (the script already exposes `last_logits`).
  - Verify label-token mapping correctness (A/B/C…). `[tokenizer_utils.py](cs781-s26/project/src/reliability_eval/models/tokenizer_utils.py)` currently picks the first variant in `("{}", " {}")` whose 5 codes are all distinct. If `"A"` (no space) is chosen but the actual continuation token after the prompt is `" A"`, the model could be scoring wrong tokens. Confirm which variant was selected and check the last token of a rendered prompt — if it ends `"... letter."` then a leading-space variant likely matches the model's natural continuation.
  - Compare prompt templates across t3, t4, t5 on dev200 — but only via the existing artifacts where possible. The 10 finalized runs cover all 5 templates for FP16 already; recompute predicted-label histograms from `predictions.jsonl` instead of re-running.
  - Dump 10–20 raw predictions for manual inspection from FP16 t2 (best existing result) and FP16 t1 (worst): `head -n 20 artifacts/runs/<run_id>/predictions.jsonl`. Confirm whether t2's higher macro_f1 corresponds to genuine class diversity or just a slightly different collapse target.
  - Validate dev200 dataset creation: `wc -l data/samples/pubmed_rct_dev200.jsonl` should be 200; provenance file `pubmed_rct_dev200.provenance.json` should match.
  - Decision point (after diagnostic log + forensics): present findings to user; user picks the single candidate. Decision menu:
    - Candidate A — force `" {}"` variant in `get_code_token_ids`. Pick if the diagnostic shows the chosen variant is `"A"` and the prompt's last token is whitespace-adjacent.
    - Candidate B — change `score_class_codes.py` to score logits at the position right after the model's first generated whitespace. Pick if Candidate A's evidence is ambiguous and unrestricted top-k at `[-1]` shows the predicted token is a space or punctuation rather than a letter.
    - Candidate C — switch t5's legend to canonical A=BACKGROUND…E=CONCLUSIONS. Pick if forensics show the t5 collapse pattern matches positional confusion (e.g., predictions concentrate on the FIRST listed letter, which is `E` in t5).
  - Then ONE run: `PYTHONPATH=src python -m reliability_eval.cli run --profile local_real --dataset pubmed_rct_dev200 --precision fp16 --template <best> --calibration none --sample-size 200`.
  - Acceptance: `macro_f1 > 0.20` AND multi-class predictions AND saved at `artifacts/runs/<new_id>/`.
  - Hard guardrail: if the fix succeeds, DO NOT re-run the full n=2000 matrix post-fix. The single n=200 dev200 baseline is the post-fix exhibit. Pre-fix n=2000 stays as the documented bug-trail (least-compute Fix-Found scenario).
  - Fallback: if not met, lock the 10/15 as final evidence and proceed.
- Day 2 — ONE CHEAP INT4 RETRY + AGGREGATES
  - int4/`pubmed_t2` retry (30 min budget):
  `pip install -U bitsandbytes && pip install -U transformers` (or pin to versions known to work with `bitsandbytes>=0.43`); then `... --precision int4 --template pubmed_t2 --sample-size 2000`. If it fails: drop and continue.
  - Regenerate aggregates from the final run set:
  `python experiments/build_final_report.py --artifact-root artifacts/runs --run-id <each real run, including new ones if any>`.
  - Verify outputs match the actual on-disk evidence: `[reports/final_metrics.md](cs781-s26/project/reports/final_metrics.md)`, `[reports/hypothesis_tests.md](cs781-s26/project/reports/hypothesis_tests.md)`, `[reports/figures/reliability_by_precision.png](cs781-s26/project/reports/figures/reliability_by_precision.png)`, `[reports/figures/recovery_plot.png](cs781-s26/project/reports/figures/recovery_plot.png)`.
  - Optional: temperature scaling pass on the FP16 t2 baseline (best existing FP16 result). Note: per `[run_single.py](cs781-s26/project/src/reliability_eval/experiments/run_single.py)` `_load_calibration_probabilities` requires a `validation` split, which the HF PubMed RCT loader supports. Time budget: 20 min.
- Day 3 — REPORT REWRITE
  - Cross-check `[reports/run_ids_manifest.md](cs781-s26/project/reports/run_ids_manifest.md)` row-by-row against `ls artifacts/runs/`. Append any Day 1/2 new runs. The current manifest content matches reality; verify after any new runs land.
  - Rewrite `[reports/final_report.md](cs781-s26/project/reports/final_report.md)` Results/Discussion against actual numbers (`final_metrics.md`).
  - Choose narrative from section G:
    - If Day 1 fix worked: section G "Fix-Found" scenario.
    - Else if int4/t2 retry worked: section G Scenario 2.
    - Else: section G Scenario 1 (current de-facto state).
  - Acceptance: every numeric claim cites a real run_id whose `metrics.json` exists.
- Day 4 — FINALIZE
  - Polish [`reports/final_report.md`](cs781-s26/project/reports/final_report.md): tighten Results/Discussion, ensure every numerical claim cites a real run_id, verify Limitations covers (a) BACKGROUND collapse, (b) 10/15 matrix incompleteness, (c) Markdown vs LaTeX-first preregistration deviation.
  - Add a one-line note in the report acknowledging Markdown submission (rationale: time constraint; user handles final formatting pass before submission).
  - Single clean commit: `git add reports/ artifacts/runs && git commit -m "Finalize triaged final-project evidence"`.
  - User then runs final-formatting pass before submission.

## D. Scope Triage

KEEP

- Forensic re-analysis of the 10 existing runs (this IS the experiment now).
- One Day 1 fix attempt against dev200 (single shot).
- One Day 2 int4/t2 retry with pinned env (single shot).
- Aggregated metrics regenerated by `experiments/build_final_report.py`.
- Manifest cross-check.
- Reliability + recovery figures already in `reports/figures/`.

CUT (one-line justifications)

- MedNLI — `src/reliability_eval/data/mednli.py` raises `NotImplementedError`; out of scope.
- int8/`pubmed_t5` and int4/`pubmed_t3..t5` — not retried; documented as runtime-blocked.
- Isotonic — explicitly deferred per preregistration.
- Multi-template Fleiss kappa beyond what `build_final_report.py` already produces — already partially in `reports/hypothesis_tests.md`; do not extend.
- Flyte — irrelevant.
- Bootstrap CIs broader than `build_final_report.py` defaults — keep the script's defaults, don't extend.

STRETCH (only if Day 1 fix passes AND time remains)

- Generate one clean FP16 dev200 baseline run AND the corresponding HF n=2000 baseline; compare to the prior collapsed n=2000 result as a "before/after fix" exhibit.
- Multi-template Fleiss kappa on FP16 with the post-fix code path.
- INT8 retry of all 5 templates with pinned env.

## E. Deliverables (Dependency Order)

1. Forensics summary
  - Artifact: short markdown table or paragraph: per-run predicted-label histogram + mean A-vs-rest confidence.
  - Path: `reports/diagnostics/forensics_day1.md`.
  - Done: covers all 10 finalized runs.
2. Diagnostic log
  - Artifact: stdout of `scripts/diagnose_background_collapse.py`.
  - Path: `reports/diagnostics/collapse_day1.log`.
  - Done: contains `code_token_ids`, restricted A..E logits/softmax for both legend scenarios, and at least one top-k unrestricted token list.
3. Day 1 fix-attempt run (or recorded miss)
  - Path: `artifacts/runs/<day1_fix_run_id>/...` if attempted.
  - Done: either `macro_f1 > 0.20` (=> Fix-Found scenario) or noted as attempted-and-failed in `reports/diagnostics/forensics_day1.md`.
4. int4/`pubmed_t2` retry (or recorded miss)
  - Path: `artifacts/runs/<int4_t2_retry_run_id>/...` if attempted.
  - Done: completes with valid `metrics.json`, OR recorded as cut.
5. Aggregated metrics
  - Path: `[reports/final_metrics.md](cs781-s26/project/reports/final_metrics.md)`, `[reports/hypothesis_tests.md](cs781-s26/project/reports/hypothesis_tests.md)`.
  - Done: regenerated from the final run set.
6. Cross-run figures
  - Path: `[reports/figures/reliability_by_precision.png](cs781-s26/project/reports/figures/reliability_by_precision.png)`, `[reports/figures/recovery_plot.png](cs781-s26/project/reports/figures/recovery_plot.png)`.
  - Done: regenerated.
7. Honest report
  - Path: `[reports/final_report.md](cs781-s26/project/reports/final_report.md)` (and `.tex` if pursued).
  - Done: every numerical claim traces to a real `metrics.json`; chosen scenario from section G is explicit.
8. Updated manifest
  - Path: `[reports/run_ids_manifest.md](cs781-s26/project/reports/run_ids_manifest.md)`.
  - Done: only run_ids that exist on disk; new Day 1/2 runs included.
9. Final clean commit.

## F. Risk Register (Top 5)

1. GPU access failure
   - Likelihood: low. User confirmed GPU is available.
   - Impact: blocks Day 1 fix and Day 2 retry only; salvage path is unaffected.
   - Trigger: GPU host actually unavailable when Day 1 starts.
   - Mitigation: warm up env in the first 30 min of Day 1.
   - Kill-switch: skip both Day 1 fix and Day 2 retry; go straight to Day 3 with current evidence.
2. Day 1 fix attempt fails
  - Likelihood: medium-high. The collapse is consistent across templates and precisions, suggesting a systemic prompt/scoring issue.
  - Impact: no narrative upgrade.
  - Trigger: dev200 run after fix has `macro_f1 <= 0.20`.
  - Mitigation: pre-pick the highest-leverage candidate (likely Candidate A — leading-space token variant).
  - Kill-switch: do not attempt a second fix. Move to salvage.
3. int4/`pubmed_t2` retry fails
  - Likelihood: high (already errors documented in `[reports/run_ids_manifest.md](cs781-s26/project/reports/run_ids_manifest.md)`).
  - Impact: matrix stays at 10/15.
  - Trigger: same `bitsandbytes` / meta-tensor errors.
  - Mitigation: pin `bitsandbytes==0.43.x` against current `transformers`.
  - Kill-switch: drop the cell; document in limitations.
4. `build_final_report.py` regenerates inconsistent values
  - Likelihood: low. Aggregator reads `predictions.jsonl` directly; numbers should match `metrics.json`.
  - Impact: confusion in final report.
  - Trigger: aggregated numbers differ from `metrics.json`.
  - Mitigation: spot-check 2 runs after regeneration. Bootstrap CIs computed by aggregator are expected to differ slightly from `metrics.json` ECE due to bin re-computation; document this.
  - Kill-switch: prefer `metrics.json` values for headline claims; CIs from aggregator.
5. Submission format mismatch
   - Likelihood: low. User confirmed Markdown is the working format; user handles final formatting before submission.
   - Impact: minimal. Just needs to be acknowledged as a deviation from the LaTeX-first preregistration.
   - Trigger: report does not document the deviation.
   - Mitigation: include a one-line deviation note in `reports/final_report.md` Limitations.
   - Kill-switch: n/a.

## G. Honest Reporting Plan

- Fix-Found scenario (only if Day 1 fix succeeds; least-compute framing).
  Frame: "We identified and corrected a [tokenization / logit-position / prompt-legend] defect in our restricted-softmax single-token scoring path, which had caused near-complete BACKGROUND collapse in our n=2000 PubMed RCT matrix. We report the pre-fix n=2000 matrix in full as a cautionary record of how a single-token scoring defect can produce a coherent-looking but degenerate calibration study. Post-fix, FP16 BioMistral-7B on dev200 achieves [macro_f1=…, ECE=…] at n=200. We do not re-run the full quantization × template matrix post-fix due to compute constraints; the post-fix dev200 baseline is offered as proof that the defect was real and is now addressed, not as a replacement for the matrix-level claims."
- Scenario 1 — Final state, FP16 + INT8 + 1 INT4 cell, all collapse-failing.
Frame: "We executed 10/15 cells of the preregistered FP16/INT8/INT4 × five-template matrix at n=2000 on PubMed RCT (HF). Across all completed cells, classification quality is low (`macro_f1` 0.038–0.095) and calibration error is high (`ECE` 0.336–0.704), with `pubmed_t1` and `pubmed_t4` collapsing fully to BACKGROUND under restricted-softmax single-token scoring. The primary preregistered hypothesis (`|Δ_ECE| > |Δ_F1|` at INT4 vs FP16) is supported on the single completed INT4 template (`t1`) but the matrix is too sparse for confirmation; we report this as conditional support only. Secondary recovery is not evaluated. We frame this as a finding about prompt/scoring fragility in biomedical decoder LLMs at the single-token level rather than as a clean quantization study."
- Scenario 2 — Fix-Found AND int4/t2 retry succeeds.
Frame: "After correcting the scoring defect (see Fix-Found), we additionally completed `int4/pubmed_t2` at n=2000, bringing the matrix to 11/15. We report a coherent FP16 vs INT4 comparison on `pubmed_t2` and treat all other quantized cells under the pre-fix code path as descriptive."
- Scenario 3 — Day 1 fix fails, int4/t2 fails, GPU lost.
Frame: same as Scenario 1, with explicit acknowledgement that no new evidence was added during the final week.

## H. Explicitly Out of Scope (for report reuse)

- MedNLI (no lawful data path; loader unimplemented).
- Additional INT4 cells beyond the t1 already on disk and the optional t2 retry.
- Isotonic regression calibration.
- Bootstrap CIs beyond what `build_final_report.py` defaults produce.
- Prompt sweep beyond the t1–t5 already executed at n=2000.
- Flyte execution mode.
- TF-IDF or other classical baselines.

## I. Open Questions

All resolved 2026-04-29:
1. Days available: 4.
2. GPU: available. Risk #1 downgraded.
3. Day 1 fix candidate: chosen after diagnostic log + forensics, not pre-committed. User picks from Candidate A / B / C based on what the log shows.
4. Submission format: Markdown. User handles final formatting before submission. Risk #5 downgraded.
5. Fix-Found combination: defensible AND least-compute. Pre-fix n=2000 matrix stays as documented bug-trail; one post-fix n=200 dev200 baseline is the upgrade exhibit. No full n=2000 post-fix re-run.

Plan complete. Awaiting your go/no-go on Day 1.