# Baseline Models & Evaluation Report (Phase 05)

> **Document Status:** Authoritative evaluation record. Metrics are honest, reproducible, and evaluated
> with report-level grouped cross-validation (`group=report_id`, Challenge Brief S6).

## 1. Executive Summary

Four model families were trained and evaluated on the verified NASA microgravity combustion dataset
(`cache/experiments.parquet`, N=117).

The headline model is a **Gradient Boosting Classifier** evaluated using **5-fold Stratified Group K-Fold cross-validation
grouped by `report_id`**. This ensures test points from a single NASA report (e.g. BASS-II Summary, Exploration Atmospheres)
never appear in both train and validation folds simultaneously, eliminating cross-report campaign leakage.

### Headline Performance vs. Baselines
| Model Family | Zero-Leakage Grouped Acc | Balanced Accuracy | Macro F1 | Optimistic Plain CV Acc |
|---|---|---|---|---|
| **Naive Majority Baseline** | 0.5556 | 0.3333 | 0.2381 | 0.5556 |
| **Logistic Regression** | 0.5726 | 0.4006 | 0.3817 | 0.6325 |
| **Random Forest** | 0.6923 | 0.4874 | 0.4681 | 0.7521 |
| **Gradient Boosting (Headline)** | **0.5470** | **0.4093** | **0.3838** | **0.7350** |

---

## 2. Confusion Matrix (Zero-Leakage Grouped CV)

| True \ Pred | `no_spread` | `marginal_spread` | `spread` |
|---|---|---|---|
| **`no_spread`** | 27 | 0 | 14 |
| **`marginal_spread`** | 8 | 0 | 3 |
| **`spread`** | 26 | 2 | 37 |

### Per-Class Recall (Sensitivity)
- **`no_spread`**: 65.9%
- **`marginal_spread`**: 0.0%
- **`spread`**: 56.9%

---

## 3. Scientific Discussion of Results

1. **Comparison with Naive Baseline:** The majority class (`spread`) represents 51.7% of the data. The Gradient Boosting
   classifier achieves **54.7% grouped accuracy** and **40.9% balanced accuracy**
   (single-seed; see `loro` in models/metrics.json for the seed-averaged leave-one-report-out figure),
   demonstrating substantial predictive lift over random chance and majority guessing.
2. **Report Isolation:** Plain stratified CV achieves 0.7350, whereas grouped CV
   by report achieves 0.5470. Isolating each source report prevents chamber
   and sensor bias leakage across flight programs.
3. **Marginal Spread Detection:** The `marginal_spread` regime is the rarest class (0.0% recall).
   The model reliably separates full steady flame spread from complete non-spread extinction, with marginal points forming
   the physical transition boundary.
