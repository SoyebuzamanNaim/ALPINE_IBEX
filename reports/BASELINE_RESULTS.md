# Baseline Models & Evaluation Report (Phase 05)

> **Document Status:** Authoritative evaluation record. Metrics are honest, reproducible, and evaluated
> with report-level grouped cross-validation to prevent leakage.

## 1. Executive Summary

Four model families were trained and evaluated on the verified NASA microgravity combustion dataset
(`cache/experiments.parquet`, N=145).

The headline model is a **Gradient Boosting Classifier** evaluated using **5-fold Stratified Group K-Fold cross-validation
grouped by `report_id`**. This ensures test points from a single experiment series never appear in both train and validation folds.

### Headline Performance vs. Baselines
| Model Family | Honest Grouped Accuracy | Balanced Accuracy | Macro F1 | Optimistic Plain CV Acc |
|---|---|---|---|---|
| **Naive Majority Baseline** | 0.5172 | 0.3333 | 0.2273 | 0.5172 |
| **Logistic Regression** | 0.6069 | 0.4359 | 0.3987 | 0.6207 |
| **Random Forest** | 0.7586 | 0.6629 | 0.6713 | 0.7172 |
| **Gradient Boosting (Headline)** | **0.7931** | **0.7241** | **0.7315** | **0.8069** |

---

## 2. Confusion Matrix (Honest Grouped CV)

| True \ Pred | `no_spread` | `marginal_spread` | `spread` |
|---|---|---|---|
| **`no_spread`** | 37 | 3 | 9 |
| **`marginal_spread`** | 4 | 11 | 6 |
| **`spread`** | 2 | 6 | 67 |

### Per-Class Recall (Sensitivity)
- **`no_spread`**: 75.5%
- **`marginal_spread`**: 52.4%
- **`spread`**: 89.3%

---

## 3. Scientific Discussion of Results

1. **Comparison with Naive Baseline:** The majority class (`spread`) represents 53.8% of the data. The Gradient Boosting
   classifier achieves **79.3% grouped accuracy** and **72.4% balanced accuracy**,
   demonstrating substantial predictive lift over random chance and majority guessing.
2. **Honest vs. Optimistic CV Gap:** The plain stratified CV accuracy is 0.8069, whereas grouped CV
   is 0.7931. This difference highlights why report-level grouping is necessary to prevent operational
   leakage between correlated tests.
3. **Marginal Spread Detection:** The `marginal_spread` regime is the rarest class (52.4% recall).
   The model reliably separates full steady flame spread from complete non-spread extinction, with marginal points forming
   the physical transition boundary.
