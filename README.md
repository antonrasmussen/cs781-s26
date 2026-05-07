# CS781 – AI for Health Sciences

Course materials for Spring 2026.

## Structure

| Folder | Contents |
|--------|----------|
| `assignments/` | Submitted assignments; each in its own subfolder (e.g. `assignments/diabetes/`) with README, data, notebook, report |
| `certificates/` | Course and training completion certificates (e.g. DataCamp) |
| `notebooks/` | Jupyter notebooks (e.g., Deep Learning in Genomics primer) |
| `notes/` | Course notes and discussion write-ups |
| `papers/` | Research papers (PDFs); see [papers/README.md](papers/README.md) for a list with titles, authors, page counts, years, and one-sentence summaries |
| `project/` | Active research code and course project materials |
| `slides/` | Lecture slides |

## Project

**Final course project (reviewers start here):** [project/reports/final_report.md](project/reports/final_report.md), summarized metrics in [project/reports/final_metrics.md](project/reports/final_metrics.md), and hypothesis outcomes in [project/reports/hypothesis_tests.md](project/reports/hypothesis_tests.md). Reproducibility and artifact disclosure: [project/docs/reproducibility_note.md](project/docs/reproducibility_note.md).

The course project proposal source is in [project/docs/proposal.md](project/docs/proposal.md). For repository layout and commands, see [project/README.md](project/README.md). For historical CUDA handoff operations during development, see [project/docs/cuda_pubmed_handoff.md](project/docs/cuda_pubmed_handoff.md).

To regenerate the proposal PDF:

```bash
cd project && python docs/scripts/build_pdf.py
```
