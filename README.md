# CS781 – AI for Health Sciences

Course materials for Spring 2026.

> **Status: Historical course provenance.** The `project/` tree records the CS781
> submission and a **class-code / collapse-dominated** BioMistral evaluation. It is
> **not** the scientific source of truth for the published quantization study.
>
> - Preprint: [arXiv:2608.03854](https://arxiv.org/abs/2608.03854) — *Quantization Effects on Biomedical LLM Reliability* (Rasmussen & Qin)
> - Manuscript + experiment SoT: [hongqin/fss26_antonLLM](https://github.com/hongqin/fss26_antonLLM) (day-to-day fork: [antonrasmussen/fss26_antonLLM](https://github.com/antonrasmussen/fss26_antonLLM))
> - Status detail: [project/docs/STATUS.md](project/docs/STATUS.md)
>
> **Do not use this repository to reproduce the preprint.** The preprint uses
> multi-model answer-text scoring (sum vs mean token log-likelihood) and lives in
> `fss26_antonLLM`, not here.

## Structure

| Folder | Contents |
|--------|----------|
| `assignments/` | Submitted assignments; each in its own subfolder (e.g. `assignments/diabetes/`) with README, data, notebook, report |
| `certificates/` | Course and training completion certificates (e.g. DataCamp) |
| `notebooks/` | Jupyter notebooks (e.g., Deep Learning in Genomics primer) |
| `notes/` | Course notes and discussion write-ups |
| `papers/` | Research papers (PDFs); see [papers/README.md](papers/README.md) for a list with titles, authors, page counts, years, and one-sentence summaries |
| `project/` | **Frozen** CS781 research code and course project materials (class-code protocol provenance) |
| `slides/` | Lecture slides |

## Project (course freeze)

**"Beyond Accuracy Loss in Quantized Biomedical LLMs"** — CS781 final project evaluating calibration and prompt robustness for BioMistral-7B on PubMed RCT under FP16, INT8, and INT4 with **zero-shot A–E class-code scoring**. That protocol produced prompt-driven label collapse and was **superseded** by the redesigned evaluation in arXiv:2608.03854.

### Final submission

| Artifact | Link |
|---|---|
| Written report (PDF) | [project/reports/CS781\_Final\_Report\_Anton\_Rasmussen.pdf](project/reports/CS781_Final_Report_Anton_Rasmussen.pdf) |
| Report source (LaTeX) | [project/reports/final\_report.tex](project/reports/final_report.tex) |
| Metrics table | [project/reports/final\_metrics.md](project/reports/final_metrics.md) |
| Hypothesis outcomes | [project/reports/hypothesis\_tests.md](project/reports/hypothesis_tests.md) |
| Run ID manifest | [project/reports/run\_ids\_manifest.md](project/reports/run_ids_manifest.md) |
| Reproducibility note | [project/docs/reproducibility\_note.md](project/docs/reproducibility_note.md) |
| Verification artifacts | [project/artifacts/verification\_runs/](project/artifacts/verification_runs/) |

### More project detail

For full repo layout, setup instructions, and CLI commands see [project/README.md](project/README.md). The original proposal is in [project/docs/proposal.md](project/docs/proposal.md). Course claim boundaries and the frozen evidence inventory are in [project/docs/manuscript_claim_boundaries.md](project/docs/manuscript_claim_boundaries.md) and [project/docs/evidence_registry.md](project/docs/evidence_registry.md). Current scientific status vs the preprint: [project/docs/STATUS.md](project/docs/STATUS.md).
