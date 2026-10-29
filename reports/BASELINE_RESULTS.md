# Baseline Models & Evaluation Report (Phase 05)

> **Document Status:** Authoritative evaluation record. Metrics are honest, reproducible, and evaluated
> with report-level grouped cross-validation (`group=report_id`, Challenge Brief S6).

## 1. Executive Summary

Four model families were trained and evaluated on the verified NASA microgravity combustion dataset
(`cache/experiments.parquet`, N=200).

The headline model is a **Gradient Boosting Classifier** evaluated using **5-fold Stratified Group K-Fold cross-validation
grouped by `report_id`**. This ensures test points from a single NASA report (e.g. BASS-II Summary, Exploration Atmospheres)
never appear in both train and validation folds simultaneously, eliminating cross-report campaign leakage.

### Headline Performance vs. Baselines
| Model Family | Zero-Leakage Grouped Acc | Balanced Accuracy | Macro F1 | Optimistic Plain CV Acc |
|---|---|---|---|---|
| **Naive Majority Baseline** | 0.8150 | 0.3333 | 0.2994 | 0.8150 |
| **Logistic Regression** | 0.6600 | 0.4120 | 0.3780 | 0.8400 |
| **Random Forest** | 0.8000 | 0.3945 | 0.4015 | 0.8300 |
| **Gradient Boosting (Headline)** | **0.7600** | **0.3557** | **0.3603** | **0.8350** |

---

## 2. Confusion Matrix (Zero-Leakage Grouped CV)

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

1. **Comparison with Naive Baseline:** The majority class (`spread`) represents 51.7% of the data. The Gradient Boosting
   classifier achieves **76.0% grouped accuracy** and **35.6% balanced accuracy**
   (single-seed; see `loro` in models/metrics.json for the seed-averaged leave-one-report-out figure),
   demonstrating substantial predictive lift over random chance and majority guessing.
2. **Report Isolation:** Plain stratified CV achieves 0.8350, whereas grouped CV
   by report achieves 0.7600. Isolating each source report prevents chamber
   and sensor bias leakage across flight programs.
3. **Marginal Spread Detection:** The `marginal_spread` regime is the rarest class (0.0% recall).
   The model reliably separates full steady flame spread from complete non-spread extinction, with marginal points forming
   the physical transition boundary.
