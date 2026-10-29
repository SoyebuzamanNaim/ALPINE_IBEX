# Model Card: FLARE-X Flame-Spread Classifier

## Model Details
- **Model Name:** FLARE-X Flame Spread Gradient Boosting Classifier
- **Model Version:** 1.0.0
- **Model Type:** Scikit-Learn `GradientBoostingClassifier` with `StandardScaler` and `OneHotEncoder` (Zero-Leakage Pipeline)
- **Trained Date:** 2026-10-29T07:34:07+00:00
- **Dataset SHA-256:** `47a45022f27dc3bd6d4bef4e36e2423ccd00ae2fe8a14b3fe198f628e451a534`
- **Training Samples (N):** 117
- **Input Features (4):** `oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `material`
- **Target Classes (3):** `no_spread`, `marginal_spread`, `spread`

## Intended Use
- **Primary Use:** Decision support and physical regime estimation for microgravity solid combustible materials.
- **Intended Users:** Spacecraft fire-safety engineers, mission analysts, combustion researchers.
- **Out-of-Scope Use:** Never use for flight certification or safety-critical decisions without human verification and NASA-STD-6001 testing.

## Performance & Evaluation
- **Evaluation Scheme:** 5-fold Stratified Group K-Fold (`group=report_id`); investigation-level reported separately
- **Honest Grouped Accuracy:** 54.7%
- **Balanced Accuracy:** 40.9%
- **Macro F1 Score:** 0.3838
- **Naive Majority Baseline:** 55.6%

## Operational Envelope (Training Range)
- `oxygen_pct`: 14.0% to 24.0% vol
- `pressure_kpa`: 44.1 to 101.3 kPa
- `flow_cm_s`: 0.0 to 45.0 cm/s
- `material`: Cellulose, Cotton, Mylar, Nomex, PMMA, Ultem

Requests outside these boundaries trigger a strict refusal state per the FLARE-X safety contract.
