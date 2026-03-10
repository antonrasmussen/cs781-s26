# Diabetes Prediction Report

## Overview

This report summarizes the development and evaluation of a machine learning model to predict diabetes status using the Pima Indians Diabetes dataset in `diabetes.csv`. The goal was not only to obtain a reasonable classifier, but also to understand which clinical variables most influenced the predictions and whether those explanations were medically plausible.

The target variable was `Outcome`, where `1` indicates diabetes and `0` indicates no diabetes. Predictor variables included `Pregnancies`, `Glucose`, `BloodPressure`, `SkinThickness`, `Insulin`, `BMI`, `DiabetesPedigreeFunction`, and `Age`.

## Dataset Description

The dataset contains `768` patient records with `8` predictor variables and `1` binary target. The class distribution is moderately imbalanced:

- `500` observations with `Outcome = 0`
- `268` observations with `Outcome = 1`

This is a small tabular classification dataset, so performance estimates can vary depending on the train/test split. For that reason, the workflow used both stratified cross-validation and a held-out test set.

## Data Quality and Preprocessing

One of the best-known issues in this dataset is that several physiologic variables contain zero values that are not medically realistic and are commonly interpreted as placeholders for missing data. In this project, zeros were converted to missing values in the following columns:

- `Glucose`
- `BloodPressure`
- `SkinThickness`
- `Insulin`
- `BMI`

After conversion, the missingness counts were:

| Feature | Missing Count | Missing Percent |
|---|---:|---:|
| `Glucose` | 5 | 0.7% |
| `BloodPressure` | 35 | 4.6% |
| `SkinThickness` | 227 | 29.6% |
| `Insulin` | 374 | 48.7% |
| `BMI` | 11 | 1.4% |

This pattern matters for both prediction and interpretation. In particular, `Insulin` and `SkinThickness` have so much missingness that any model signal from those variables should be interpreted cautiously.

To prevent data leakage, preprocessing was built directly into the model pipelines. Median imputation was applied within the pipeline, and standardization was applied only for linear models that benefit from scaling.

## Modeling Approach

The final workflow used:

- An `80/20` stratified train/test split
- Stratified `5`-fold cross-validation on the training set
- Model comparison across interpretable and nonlinear baselines

The models implemented were:

- Logistic regression with median imputation and standardization
- Random forest with median imputation
- XGBoost as an optional model if the environment supports it

In the execution environment used here, XGBoost was made optional because it depends on the macOS OpenMP runtime (`libomp`). The notebook falls back cleanly to logistic regression and random forest when XGBoost is unavailable. This did not materially weaken the analysis, because logistic regression emerged as the best overall model anyway.

## Evaluation Metrics

The main ranking metrics were:

- ROC-AUC
- PR-AUC

Threshold-dependent metrics were also reported:

- Recall (sensitivity)
- Precision
- F1 score
- Balanced accuracy

In addition, the notebook includes:

- A confusion matrix for the selected model
- ROC and precision-recall curves
- A threshold sweep to explore sensitivity-specificity tradeoffs
- A calibration plot

## Cross-Validation Results

Cross-validation on the training set showed:

| Model | Mean ROC-AUC | Approx. Variation |
|---|---:|---:|
| Logistic Regression | 0.844 | +/- 0.032 |
| Random Forest | 0.821 | +/- 0.048 |

These results suggest that logistic regression generalized slightly better than random forest on this dataset, while also offering a more interpretable structure.

## Held-Out Test Results

Performance on the held-out test set was:

| Model | ROC-AUC | PR-AUC | Recall | Precision | F1 | Balanced Accuracy |
|---|---:|---:|---:|---:|---:|---:|
| Logistic Regression | 0.813 | 0.673 | 0.704 | 0.603 | 0.650 | 0.727 |
| Random Forest | 0.811 | 0.677 | 0.574 | 0.660 | 0.614 | 0.707 |

The two models were quite close on ranking performance, but logistic regression had:

- slightly higher ROC-AUC,
- notably higher recall at the default threshold,
- better balanced accuracy,
- and greater interpretability.

For those reasons, logistic regression was selected as the final model.

## Confusion Matrix and Operating Point

At the default threshold of `0.50`, the final logistic regression model produced the following confusion matrix:

|  | Predicted No Diabetes | Predicted Diabetes |
|---|---:|---:|
| Actual No Diabetes | 75 | 25 |
| Actual Diabetes | 16 | 38 |

This corresponds to:

- Sensitivity around `70%`
- Specificity around `75%`

That is a reasonable balance for a small dataset. The model is not perfect, but it captures a meaningful portion of positive cases without collapsing specificity.

## Threshold Analysis

The threshold sweep shows the expected tradeoff between sensitivity and specificity.

Examples from the reported table:

| Threshold | Sensitivity | Specificity | Precision |
|---|---:|---:|---:|
| 0.10 | 0.981 | 0.240 | 0.411 |
| 0.20 | 0.981 | 0.500 | 0.515 |
| 0.25 | 0.926 | 0.560 | 0.532 |
| 0.50 | 0.704 | about 0.750 | 0.603 |

This matters because the right threshold depends on the application:

- For **screening**, a lower threshold may be appropriate because missing a true diabetes case can be costly.
- For a **more conservative decision rule**, a threshold closer to `0.50` may be preferable because it reduces false positives.

The notebook therefore supports discussing the model as a tool whose behavior can be tuned to clinical priorities rather than judged only at one arbitrary threshold.

## Model Interpretation

To understand which variables most influenced predictions, the notebook applied SHAP to the final model and also computed permutation importance as a robustness check.

### SHAP Global Importance

Mean absolute SHAP values ranked the features as follows:

| Feature | Mean Absolute SHAP |
|---|---:|
| `Glucose` | 1.016 |
| `BMI` | 0.583 |
| `Pregnancies` | 0.337 |
| `DiabetesPedigreeFunction` | 0.215 |
| `Age` | 0.159 |
| `Insulin` | 0.031 |
| `BloodPressure` | 0.010 |
| `SkinThickness` | 0.009 |

### Permutation Importance

Permutation importance produced a very similar ordering:

| Feature | Mean Importance |
|---|---:|
| `Glucose` | 0.153 |
| `BMI` | 0.031 |
| `Pregnancies` | 0.025 |
| `DiabetesPedigreeFunction` | 0.010 |
| `Age` | 0.004 |
| `Insulin` | 0.002 |
| `BloodPressure` | 0.001 |
| `SkinThickness` | 0.000 |

The agreement between SHAP and permutation importance is encouraging. It suggests the model is not relying on arbitrary artifacts and that the most influential variables are relatively stable across explanation methods.

## Medical Plausibility of the Explanations

The explanation patterns are medically plausible.

### `Glucose`

`Glucose` was by far the strongest predictor, which is exactly what would be expected in a diabetes classification task. Elevated glucose is central to diagnosing and characterizing diabetes, so this result strongly supports the model's face validity.

### `BMI`

`BMI` emerged as the second most important feature. This is also clinically sensible because higher BMI is associated with insulin resistance and type 2 diabetes risk.

### `Pregnancies`

`Pregnancies` showed moderate influence. In this dataset, that is plausible because pregnancy history can interact with age and metabolic risk, and the Pima dataset is known to preserve some signal in this feature.

### `DiabetesPedigreeFunction`

This variable acts as a family-history-related risk indicator. Its positive contribution is consistent with known hereditary influences on diabetes risk.

### `Age`

`Age` also contributed meaningfully, which is medically reasonable because diabetes risk generally rises with age in adult populations.

### `Insulin`, `SkinThickness`, and `BloodPressure`

These variables contributed little in the final explanation results. That is believable here, especially for `Insulin` and `SkinThickness`, because the missingness burden was extremely high after cleaning. Weak importance for these variables should not be interpreted as evidence that they are clinically unimportant in general; rather, they were not very usable in this specific dataset under this preprocessing strategy.

## Why Logistic Regression Was a Good Final Choice

Although nonlinear models are often attractive in biomedical prediction, logistic regression was a strong choice here for several reasons:

- It performed at least as well as random forest on the holdout ROC-AUC.
- It produced higher recall at the default threshold.
- It is more transparent and easier to explain.
- Its explanation structure aligns well with a small clinical tabular dataset.

Given the dataset size and quality limitations, a simpler, well-calibrated, interpretable model is arguably more appropriate than a more flexible model with only marginal benefit.

## Limitations

Several limitations should be acknowledged.

### Small sample size

With only `768` observations, estimates of performance are uncertain and can vary noticeably across splits. The cross-validation variance already reflects that instability.

### Limited representativeness

This is a historical dataset from a specific population and does not represent all patient groups or modern clinical settings. Performance and feature behavior may not generalize broadly.

### Missingness encoded as zero

Several variables used zeros to represent missing data. Even after correcting that issue through imputation, the original data quality problem still limits confidence in some features and explanations.

### Predictive, not causal, interpretation

SHAP values explain how the model uses variables, not why diabetes occurs biologically. A large SHAP value does not imply a causal mechanism.

### No external validation

The model was evaluated only with internal train/test splitting and cross-validation. Real clinical use would require independent external validation and likely subgroup analysis.

### Environment-dependent model availability

XGBoost was made optional due to dependency constraints in the environment. While this did not change the best model in this case, it is still worth documenting.

## Conclusion

The final modeling workflow produced a sensible and interpretable diabetes prediction model. Logistic regression achieved the strongest overall balance of performance and explainability, with test ROC-AUC around `0.81` and clinically reasonable sensitivity-specificity tradeoffs.

The feature explanations were consistent across SHAP and permutation importance, and the top predictors, especially `Glucose`, `BMI`, `Age`, and `DiabetesPedigreeFunction`, aligned with clinical expectations. The model therefore appears to be learning meaningful patterns rather than obvious artifacts.

At the same time, the dataset has important weaknesses, particularly its small size, limited representativeness, and heavy missingness in some features. As a result, the model should be viewed as a useful educational and exploratory example of interpretable clinical prediction, not as a deployment-ready diagnostic tool.

## Files (this assignment)

| File | Description |
|------|-------------|
| `diabetes_prediction.ipynb` | Notebook: data, models, evaluation, SHAP |
| `diabetes.csv` | Pima Indians Diabetes dataset |
| `report.md` | This report |
| `README.md` | Setup and run instructions |
