# Prioritized Consistency Issues

Issues identified during the audit. Fix immediately vs. later.

---

## Fix Immediately (before presenting as professional)

| # | Issue | Location | Action |
|---|-------|----------|--------|
| 1 | Artifacts in `artifacts/runs/` are mock outputs but not labeled | `run_mvp.py`, `metadata.json` | **Resolved** — Added `mode` and `dataset_source` to metadata; README updated |
| 2 | README "Repo layout" points to `project_topics.md` at root | `README.md` | **Resolved** — Updated to `docs/proposal.md` |
| 3 | Root clutter: proposal, build script, generated files mixed with code | Root | **Resolved** — Moved to `docs/` |

---

## Fix Soon (documentation hygiene)

| # | Issue | Location | Action |
|---|-------|----------|--------|
| 4 | Docs claim 5 templates per task; only 2 PubMed exist | `docs/proposal.md`, `experiment_protocol.md` | Add note: "Scaffold: 2 PubMed templates; target 5 per task" or update to match current state |
| 5 | Prompt templates duplicated: YAML vs. hardcoded in `render.py` | `configs/prompts/`, `render.py` | Either load from YAML in renderer or document YAML as reference-only; eliminate drift risk |
| 6 | `resolved_config.yaml` is written as JSON | `artifact_store.py` | Use PyYAML for proper YAML, or rename to `resolved_config.json` |

---

## Fix Later (implementation work)

| # | Issue | Location | Action |
|---|-------|----------|--------|
| 7 | PubMed loader silently falls back to tiny sample | `pubmed_rct.py` | Log warning when falling back; document in docstring |
| 8 | MedNLI, ACE, bootstrap CIs, Fleiss' kappa, calibration recovery | Various stubs | Implement per phase plan |
| 9 | Reliability diagram can emit 1x1 placeholder PNG | `reliability_diagrams.py` | Add matplotlib to requirements or document fallback behavior |
