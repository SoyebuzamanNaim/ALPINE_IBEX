# Model Card: FLARE-X Flame-Spread Classifier

## Model Details
- **Model Name:** FLARE-X Flame Spread Gradient Boosting Classifier
- **Model Version:** 1.0.0
- **Model Type:** Scikit-Learn `GradientBoostingClassifier` with `StandardScaler` and `OneHotEncoder`
- **Trained Date:** 2026-10-03T17:49:01+00:00
- **Dataset SHA-256:** `d5a06d2d0cce4e2fe2207bd490df4ec1213ca6eeabc1436243eb8d49dafd0be0`
- **Training Samples (N):** 145
- **Input Features (4):** `oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `material`
- **Target Classes (3):** `no_spread`, `marginal_spread`, `spread`

## Intended Use
- **Primary Use:** Decision support and physical regime estimation for microgravity solid combustible materials.
- **Intended Users:** Spacecraft fire-safety engineers, mission analysts, combustion researchers.
- **Out-of-Scope Use:** Never use for flight certification or safety-critical decisions without human verification and NASA-STD-6001 testing.

## Performance & Evaluation
- **Evaluation Scheme:** 5-fold Stratified Group K-Fold (`group=report_id`)
- **Honest Grouped Accuracy:** 79.3%
- **Balanced Accuracy:** 72.4%
- **Macro F1 Score:** 0.7315
- **Naive Majority Baseline:** 51.7%

## Operational Envelope (Training Range)
- `oxygen_pct`: 15.0% to 34.0% vol
- `pressure_kpa`: 56.5 to 101.3 kPa
- `flow_cm_s`: 0.0 to 45.0 cm/s
- `material`: Cellulose, Cotton, Delrin, Nomex, PMMA

Requests outside these boundaries trigger a strict refusal state per the FLARE-X safety contract.
