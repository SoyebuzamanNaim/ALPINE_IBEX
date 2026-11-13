# Baseline Models & Evaluation Report

Serving model: **linear SVM**, C=1.0, four inputs; trained on 200 observations.
Its 84.0% report-grouped score is exploratory: this model was selected
using this dataset. All three classes and every report remain included.

| Model | Report-grouped accuracy | Balanced accuracy | Macro-F1 |
|---|---:|---:|---:|
| majority_baseline | 0.8150 | 0.3333 | 0.2994 |
| logistic_regression | 0.6600 | 0.4120 | 0.3780 |
| random_forest | 0.8000 | 0.3870 | 0.3933 |
| gradient_boosting | 0.7750 | 0.3618 | 0.3637 |
| linear_svm (serving model) | 0.8400 | 0.4034 | 0.4215 |

Validation: LeaveOneGroupOut(group=report_id), 7 report folds.
Confusion matrix (true rows / predicted columns: no_spread, marginal_spread, spread):
`[[8, 0, 27], [0, 0, 2], [2, 1, 160]]`.

Full search procedure nested accuracy: 0.255.
This describes model selection across the search, not the fixed SVM alone.

There are 7 report groups with row counts [158, 13, 12, 7, 6, 3, 1]; pooled metrics are row-weighted and dominated by the largest report. Only two marginal_spread records exist, so class-specific performance for that label is not statistically reliable. Treat scores as exploratory, not as evidence for operational or safety use.

Exploratory model estimates only. The grouped score was used for model selection; probabilities are not validated across reports. No flight certification or safety clearance.
