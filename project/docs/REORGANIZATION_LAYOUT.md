# Conservative Reorganization Layout

Target structure for documentation and generated artifacts. Code layout (`src/`, `tests/`, `configs/`, `experiments/`) remains unchanged.

---

## Current vs. Target

### Root (before)
```text
project/
├── README.md
├── project_topics.md          # proposal source
├── project_topics.html        # generated (gitignored)
├── project_topics.pdf         # generated (gitignored)
├── build_pdf.py               # doc build script
├── markdown-pdf.css           # unused (build_pdf uses inline CSS)
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── configs/
├── data/
├── docs/
├── experiments/
├── artifacts/
├── reports/
├── notebooks/
├── src/
└── tests/
```

### Root (after)
```text
project/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── configs/
├── data/
├── docs/                      # all documentation
├── experiments/
├── artifacts/
├── reports/
├── notebooks/
├── src/
└── tests/
```

---

## Documentation Structure (`docs/`)

| Path | Contents |
|------|----------|
| `docs/README.md` | Index of documentation (optional; README can link directly) |
| `docs/proposal.md` | Renamed from `project_topics.md` — full proposal |
| `docs/architecture.md` | (unchanged) |
| `docs/experiment_protocol.md` | (unchanged) |
| `docs/INVENTORY.md` | (audit deliverable) |
| `docs/CONSISTENCY_MATRIX.md` | (audit deliverable) |
| `docs/ISSUES.md` | (audit deliverable) |
| `docs/AUDIT_COMMENTS_AND_PROMPTS.md` | (audit deliverable) |
| `docs/generated/` | Generated exports (HTML, PDF) — add to .gitignore |
| `docs/scripts/build_pdf.py` | Moved from root; builds proposal PDF |
| `docs/scripts/markdown-pdf.css` | Moved if kept; or remove if unused |

---

## Moves to Perform

1. **`project_topics.md`** → **`docs/proposal.md`** (rename for clarity)
2. **`build_pdf.py`** → **`docs/scripts/build_pdf.py`**
3. **`markdown-pdf.css`** → **`docs/scripts/markdown-pdf.css`** (or delete if build_pdf uses inline CSS only — it does)
4. **Generated outputs**: `build_pdf.py` writes to `project_topics.html` and `project_topics.pdf` in its directory. After move, it will write to `docs/scripts/project_topics.html` and `docs/scripts/project_topics.pdf`. Alternatively, write to `docs/generated/proposal.html` and `docs/generated/proposal.pdf` for clearer naming.
5. Update **`build_pdf.py`** paths: `MD_FILE` and `OUT_FILE` to use `docs/proposal.md` and `docs/generated/proposal.pdf` (or `docs/scripts/` if we keep outputs next to script).
6. Update **`.gitignore`**: `project_topics.html`, `project_topics.pdf` → `docs/generated/*.html`, `docs/generated/*.pdf` (or equivalent).
7. Update **`README.md`**: Change "`project_topics.md`" to "`docs/proposal.md`" in Repo layout; add link to proposal.

---

## Decision: Generated Output Location

**Chosen**: `docs/generated/` for HTML and PDF. Keeps generated files separate from source docs and scripts.

- `docs/scripts/build_pdf.py` reads `docs/proposal.md`, writes `docs/generated/proposal.html` and `docs/generated/proposal.pdf`.
