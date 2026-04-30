# Hypothesis Tests

Matrix completeness note: computed from the finalized partial `n=2000` matrix (`10/15` cells).
Missing cells are `int4 / pubmed_t2, pubmed_t3, pubmed_t4, pubmed_t5` and `int8 / pubmed_t5` due to runtime failures.

## Primary: |Delta_ECE| > |Delta_F1| at INT4 vs FP16
- Statistic: `(|Delta_ECE| - |Delta_F1|)` (absolute deltas, per preregistration)
- point=0.098465, ci=[0.098465, 0.098465]
- Decision (available evidence): **supported** for the completed comparison (`int4 / pubmed_t1` vs `fp16 / pubmed_t1`) because the CI is positive and excludes 0.
- Caveat: only 1 INT4 template completed at `n=2000`; treat this as conditional support under partial matrix completeness.

## Secondary: temperature scaling recovery <= 110% FP16 ECE
- Decision: **not evaluated** on the `n=2000` matrix because post-hoc calibrated counterparts were not generated for the finalized 10-run evidence set.

## Tertiary: Fleiss' kappa degradation and non-recovery
- fp16: kappa=-0.182616, ci=[-0.186162, -0.178843]
- int8: kappa=-0.049778, ci=[-0.057222, -0.041049]
- Decision: **descriptive only**. INT4 lacks template-complete coverage on `n=2000`, so the preregistered INT4-vs-FP16 non-recovery claim cannot be formally tested.
