# Rubric audit — CS781 final written report

**Audit date:** 2026-05-07  
**Evidence set:** `reports/final_report.md`, `reports/final_metrics.md`, `reports/hypothesis_tests.md`, `reports/diagnostics/forensics_day1.md`, `reports/run_ids_manifest.md`, `artifacts/verification_runs/`, `docs/reproducibility_note.md`

## Per-section verdicts (100 pts total)

| Section | Pts | Verdict | Est. score | Evidence / notes |
|--------|-----|---------|------------|------------------|
| Title & Abstract | 10 | **Pass** | 9–10 | Title is informative. Abstract ~169 words (within 150–250). States problem, approach, key results (10/15 matrix, macro-F1/ECE ranges, collapse), conclusions. Rounded ranges match `final_metrics.md` (see numeric verification below). |
| Introduction | 15 | **Risk** | 11–13 | Background, motivation, scope, and objectives are clear. **Gap:** no explicit bulleted “contributions” paragraph at end of intro (rubric asks for summary of contributions). **Fix (Phase 2):** add 3–5 contribution bullets aligned with delivered scope. Minor grammar: “due unresolved” → “due to unresolved”. |
| Methods | 15 | **Pass** | 13–15 | Model, task, class-code extraction, precisions, calibration protocol, prompts/kappa, metrics, bootstrap rule are documented. Aligns with `docs/proposal.md` / `reports/preregistration.md`. Configs live under `configs/` (reachable from repo). |
| Results | 15 | **Pass** | 13–15 | Quantitative ranges for FP16, INT8, INT4 match `final_metrics.md`. Hypothesis numbers match `hypothesis_tests.md`. 10/15 scoping consistent. Forensics 5/10 single-label matches `forensics_day1.md`. |
| Discussion | 10 | **Risk** | 7–9 | Strong interpretation (collapse vs quantization, deployment angle, open questions). Limitations are explicit. **Risk:** limited engagement with broader literature beyond cited calibration/quantization papers (Fleiss cited in methods only via name, no bib entry in current MD). **Fix:** expand refs + 1–2 sentences situating findings. |
| References | 5 | **Risk** | 3–4 | Five IEEE-style refs in MD — meets minimum “5–10” lower bound but thin. **Gaps:** Fleiss’ kappa, isotonic regression, MedNLI/PhysioNet (scope), NF4/QLoRA already partially covered — **Fix:** expand to 8+ entries in LaTeX (proposal §9 set). |
| Figures & Tables | 10 | **Gap** | 4–6 | Three PNGs exist and are listed as file paths; **no** in-text “Fig.~1” / “Table~I” integration in MD. Metrics table only in separate `final_metrics.md`. **Fix (Phase 2):** embed Table I + numbered figures + cross-references in IEEE PDF. |
| Supporting Materials | 10 | **Pass** | 8–10 | `project/README.md` setup, CLI, pytest documented. `artifacts/verification_runs/manifest.json` lists all 10 finalized `n=2000` run IDs matching `final_metrics.md`. `docs/reproducibility_note.md` + `artifacts/verification_runs/README.md` support reviewer path. Full raw runs intentionally out of repo (disclosed). |
| Overall quality & effort | 10 | **Risk** | 6–8 | MD prose is clear and professional. **Gap:** not yet in IEEE `IEEEtran` PDF form; smoke stub was `final_report.tex`. **Fix (Phase 2):** full LaTeX + PDF build. |

**Rough total (pre-fix):** ~72–86 / 100 depending on grader strictness on figures/refs/IEEE format.

## Numeric verification (final_report.md vs `final_metrics.md`)

| Claim | Report | Data (`final_metrics.md`) | OK |
|--------|--------|---------------------------|-----|
| FP16 accuracy range | 0.1055–0.1470 | 0.1055, 0.133, 0.1055, 0.1055, 0.147 | ✓ |
| FP16 macro-F1 | 0.0382–0.0955 | min 0.038173, max 0.095491 | ✓ (rounded) |
| FP16 ECE | 0.3360–0.7040 | min 0.336023, max 0.704047 | ✓ |
| INT8 accuracy | 0.1055–0.1315 | 0.1055, 0.1315, 0.106, 0.1055 | ✓ |
| INT8 macro-F1 | 0.0382–0.0953 | min 0.038173, max 0.095326 | ✓ |
| INT8 ECE | 0.3555–0.6839 | min 0.355458, max 0.683902 | ✓ |
| INT4 t1 accuracy / macro-F1 / ECE | 0.1055 / 0.0382 / 0.5876 | 0.1055 / 0.038173 / 0.587594 | ✓ |
| Abstract macro-F1 | 0.038–0.095 | global min/max over 10 rows | ✓ |
| Abstract ECE | 0.336–0.704 | global min 0.336023, max 0.704047 | ✓ |
| Primary hypothesis | point 0.098465, degenerate CI | matches `hypothesis_tests.md` | ✓ |
| Tertiary kappa | (in hypothesis file) | fp16/int8 values match `hypothesis_tests.md` | ✓ |

## Manifest / artifact traceability

- `artifacts/verification_runs/manifest.json`: **10** runs, same IDs as `final_metrics.md` rows.
- `run_ids_manifest.md`: maps primary comparison to those 10 IDs; dev200/smoke IDs called out separately (not all duplicated under `verification_runs/` — acceptable if disclosure is clear; `reproducibility_note.md` states full runs on CUDA host).

## Prioritized fix list (executed in Phase 2)

1. Replace `reports/final_report.tex` smoke stub with full IEEEtran paper: abstract, intro + **Contributions**, methods, results (**Table~\ref{...}**), discussion, limitations, reproducibility.
2. Add **Fig.~\ref{...}** for `reliability_by_precision.png`, `recovery_plot.png`, `collapse_pattern.png` (includegraphics paths relative to `reports/`).
3. Expand **thebibliography** to ≥8 IEEE-style `\bibitem`s (Fleiss, Zadrozny–Elkan, Romanov–Shivade, plus existing Guo, Dernoncourt–Lee, Labrak et al., Dettmers et al. ×2).
4. Build PDF (`pdflatex` ×2); deliver `reports/CS781_Final_Report_Anton_Rasmussen.pdf`.
5. Update `reports/final_report.md` limitation bullet to state canonical submission is PDF + `.tex` (optional one-line sync).

## Decision: Markdown vs LaTeX

- **Keep** `final_report.md` as a content sibling / easy-diff source; **canonical** submission artifact after Phase 2: **`reports/CS781_Final_Report_Anton_Rasmussen.pdf`** + **`reports/final_report.tex`**.

## Verification run log (automated)

- **pytest:** `pytest tests/ -q` from `project/` with `PYTHONPATH=src` completed **exit code 0** (2026-05-07; one test skipped as `s` in suite output).
- **CLI:** Full `run` recipe requires CUDA; README documents this. Smoke: `python -m reliability_eval.cli --help` recommended for graders without GPU.
