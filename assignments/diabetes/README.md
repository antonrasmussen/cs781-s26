# Diabetes Prediction Assignment

Binary classification on the Pima Indians Diabetes Database: predict diabetes (Outcome 1) vs no diabetes (0) from clinical measurements, with SHAP-based interpretation and a written report.

## Contents

| Item | Description |
|------|-------------|
| `diabetes.csv` | Pima Indians Diabetes dataset (768 rows, 8 features + Outcome) |
| `diabetes_prediction.ipynb` | Full pipeline: EDA, preprocessing, modeling, SHAP, calibration |
| `report.md` | Written report (methods, results, interpretation, limitations) |
| `requirements.txt` | Python dependencies for this assignment |

## Setup

From this directory (`assignments/diabetes/`):

```bash
pip install -r requirements.txt
```

**Note:** XGBoost requires OpenMP (e.g. `brew install libomp` on macOS). If XGBoost fails to load, the notebook falls back to Logistic Regression and Random Forest.

## Run

Open `diabetes_prediction.ipynb` in Jupyter and run all cells. The notebook expects `diabetes.csv` in the same directory.

## Pipeline Summary

1. **Data profiling** – Zero-to-NaN conversion for implausible clinical zeros, missingness analysis  
2. **Pipelines** – Leakage-safe imputation and scaling; LR, RF, XGBoost (if available)  
3. **Evaluation** – Stratified 5-fold CV, holdout test, ROC/PR curves, threshold sweep, calibration  
4. **SHAP** – Global summary, mean abs SHAP, dependence plots, local waterfall explanations  
5. **Plausibility & limitations** – Medical interpretation and dataset caveats (see `report.md`)
