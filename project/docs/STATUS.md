# Project status (scientific SoT)

**Freeze date:** 2026-08-07  
**Course package HEAD context:** CS781 Spring 2026 submission + May 2026 claim-boundary cleanup.

## Verdict

This `project/` tree is **historical course provenance**. It is **not** the source of truth for [arXiv:2608.03854](https://arxiv.org/abs/2608.03854).

| Role | Location |
|------|----------|
| Published manuscript + redesigned experiments | [hongqin/fss26_antonLLM](https://github.com/hongqin/fss26_antonLLM) |
| Day-to-day editable fork | [antonrasmussen/fss26_antonLLM](https://github.com/antonrasmussen/fss26_antonLLM) |
| CS781 grade artifacts + class-code collapse record | **This repository** (`cs781-s26`) |

**Do not use this repo to reproduce the preprint.**

## Protocol supersession (short)

| This course package | Preprint / `fss26_antonLLM` |
|---------------------|----------------------------|
| BioMistral-7B only | BioMistral + Mistral-Instruct + Mistral-Base (+ PubMedBERT reference) |
| Zero-shot A–E class-code restricted softmax | Answer-text templates (t6–t9) + summed / mean token log-likelihood |
| Collapse-dominated ~0.11–0.15 accuracy regime | Non-collapse decoder results reported in the paper |
| Partial 10/15 precision×template matrix at n=2000 | Multi-model answer-text matrix with tracked runs in `artifacts/runs/` |
| Course final report / claim boundaries | AAAI FSS 2026 TeX under `reports/aaai26/` |

Shared surface (PubMed RCT, BioMistral, FP16/INT8/INT4, ECE language, `reliability_eval` ancestry) is **not** enough to treat CS781 numbers as preprint results.

## What to preserve here

- Course final PDF/TeX, metrics, hypothesis outcomes, run-ID manifest
- Verification subset and integrity scripts under `project/`
- Collapse forensics (`reports/diagnostics/`) as **negative-result provenance** that motivated the redesign
- [`evidence_registry.md`](evidence_registry.md) and [`manuscript_claim_boundaries.md`](manuscript_claim_boundaries.md) as the **course evidence freeze** only

## What not to claim from this package

- That these artifacts reproduce arXiv:2608.03854
- That the 10/15 class-code matrix is the current research claim for conference/journal extension
- That expanding this tree is the path to next quantization experiments (contribute via PRs on `fss26_antonLLM` instead)

## Pointers

- Course claim boundaries: [`manuscript_claim_boundaries.md`](manuscript_claim_boundaries.md)
- Course evidence inventory: [`evidence_registry.md`](evidence_registry.md)
- Preprint: https://arxiv.org/abs/2608.03854
- Manuscript SoT README: https://github.com/hongqin/fss26_antonLLM
