# Experiment protocol

- **Splits**: train / val / calibration (15% of val) / test. Calibration set used only for post-hoc calibration; ECE on test only.
- **Decoding**: Deterministic (temperature=0).
- **Metrics**: Macro F1, per-class F1, accuracy, ECE (15 equal-width bins), ACE (15 equal-mass), reliability diagrams. Bootstrap CIs n=1000.
- **Prompt robustness**: 5 meaning-preserving templates per task; Fleiss’ kappa; no test-set template tuning.

See `proposal.md` for full methodology.
