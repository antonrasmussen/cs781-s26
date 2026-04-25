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

The course project proposal source is in `project/docs/proposal.md`. For day-to-day experiment work, start with `project/README.md`. For CUDA handoff operations, start with `project/docs/cuda_pubmed_handoff.md`.

To regenerate the proposal PDF:

```bash
cd project && python docs/scripts/build_pdf.py
```
