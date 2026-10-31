# Baseline Models & Evaluation Report

> **Generated report:** Metrics are computed from the checked-in dataset and training code.
> Report grouping prevents records from one report appearing in both sides of a fold; it does not establish physical predictive skill.

## 1. Executive Summary

Four model families were trained and evaluated on the verified NASA microgravity combustion dataset
(`cache/experiments.parquet`, N=200).

The headline model is a **Gradient Boosting Classifier** evaluated using report-grouped
`StratifiedGroupKFold` cross-validation. Rows from a held-out report do not occur in its
training fold. This split has few unevenly sized groups, so scores are uncertain and must
be interpreted with the baseline and per-class metrics.

### Grouped Performance and Baselines
| Model Family | Report-Grouped Accuracy | Balanced Accuracy | Macro F1 | Plain Stratified Accuracy |
|---|---|---|---|---|
| **Naive Majority Baseline** | 0.8150 | 0.3333 | 0.2994 | 0.8150 |
| **Logistic Regression** | 0.6600 | 0.4120 | 0.3780 | 0.8400 |
| **Random Forest** | 0.7950 | 0.3925 | 0.4004 | 0.8300 |
| **Gradient Boosting (Headline)** | **0.7600** | **0.3557** | **0.3603** | **0.8350** |

---

## 2. Confusion Matrix (Report-Grouped CV)

| True \ Pred | `no_spread` | `marginal_spread` | `spread` |
|---|---|---|---|
| **`no_spread`** | 6 | 0 | 29 |
| **`marginal_spread`** | 0 | 0 | 2 |
| **`spread`** | 13 | 4 | 146 |

### Per-Class Recall (Sensitivity)
- **`no_spread`**: 17.1%
- **`marginal_spread`**: 0.0%
- **`spread`**: 89.6%

---

## 3. Scientific Discussion of Results

1. The majority-class baseline is **81.5%**. Gradient boosting reaches
   **76.0% grouped accuracy**, **35.6% balanced accuracy**,
   and `17.1%` recall for `no_spread`.
2. The classifier does not beat the majority baseline on accuracy, and its balanced accuracy is below 0.5.
   Public inference must remain withheld until an evaluated model meets the readiness gate.
3. `marginal_spread` recall is 0.0%. The current model does not
   reliably distinguish the three outcome classes and must not be presented as a safety predictor.
