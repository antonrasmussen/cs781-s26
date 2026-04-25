# Experiment protocol

- **Operative scope (Spring 2026 checkpoint):** **PubMed 20k RCT first** — full pipeline and data inventory target PubMed. **MedNLI is deferred** (PhysioNet DUA / path not configured in-repo); hypotheses that require MedNLI are out of scope until access is confirmed.
- **Splits**: train / val / calibration (15% of val) / test. Calibration set used only for post-hoc calibration; ECE on test only. Calibration indices are a deterministic 15% of validation (`seed=42`, see `src/reliability_eval/data/splits.py`).
- **Decoding**: Deterministic (temperature=0).
- **Metrics**: Macro F1, per-class F1, accuracy, ECE (15 equal-width bins), ACE (15 equal-mass), reliability diagrams. Bootstrap CIs n=1000. **Macro** F1 is primary for PubMed because of strong class imbalance (METHODS/RESULTS dominate).
- **Prompt robustness**: Target **5** meaning-preserving PubMed templates (`pubmed_t1`–`pubmed_t5` in `configs/prompts/pubmed_templates.yaml`); Fleiss’ kappa; no test-set template tuning.

See `proposal.md` for full methodology. Dataset acquisition status: `docs/data_inventory.md`.
