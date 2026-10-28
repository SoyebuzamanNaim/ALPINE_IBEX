# Model Card: FLARE-X Flame-Spread Classifier

## Model Details
- **Model Name:** FLARE-X Flame Spread Gradient Boosting Classifier
- **Model Version:** 1.0.0
- **Model Type:** Scikit-Learn `GradientBoostingClassifier` with `StandardScaler` and `OneHotEncoder` (Zero-Leakage Pipeline)
- **Trained Date:** 2026-10-28T11:14:49+00:00
- **Dataset SHA-256:** `428cec44e6b4b29a22d0cc4bf229d4e594e5c16db87823bf9f71c1b04e633bd6`
- **Training Samples (N):** 145
- **Input Features (4):** `oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `material`
- **Target Classes (3):** `no_spread`, `marginal_spread`, `spread`

## Intended Use
- **Primary Use:** Decision support and physical regime estimation for microgravity solid combustible materials.
- **Intended Users:** Spacecraft fire-safety engineers, mission analysts, combustion researchers.
- **Out-of-Scope Use:** Never use for flight certification or safety-critical decisions without human verification and NASA-STD-6001 testing.

## Performance & Evaluation
- **Evaluation Scheme:** 5-fold Stratified Group K-Fold (`group=report_id`); investigation-level reported separately
- **Honest Grouped Accuracy:** 83.5%
- **Balanced Accuracy:** 76.2%
- **Macro F1 Score:** 0.7809
- **Naive Majority Baseline:** 51.7%

## Operational Envelope (Training Range)
- `oxygen_pct`: 15.0% to 34.0% vol
- `pressure_kpa`: 56.5 to 101.3 kPa
- `flow_cm_s`: 0.0 to 45.0 cm/s
- `material`: Cellulose, Cotton, Delrin, Nomex, PMMA

Requests outside these boundaries trigger a strict refusal state per the FLARE-X safety contract.
