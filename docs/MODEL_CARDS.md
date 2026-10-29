# Model Card: FLARE-X Flame-Spread Classifier

## Model Details
- **Model Name:** FLARE-X Flame Spread Gradient Boosting Classifier
- **Model Version:** 1.0.0
- **Model Type:** Scikit-Learn `GradientBoostingClassifier` with `StandardScaler` and `OneHotEncoder` (Zero-Leakage Pipeline)
- **Trained Date:** 2026-10-29T08:06:53+00:00
- **Dataset SHA-256:** `8063f6d900e91ab8bd9a892a4712ca12c2c1522881477a2353a55c2b06adf064`
- **Training Samples (N):** 200
- **Input Features (4):** `oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `material`
- **Target Classes (3):** `no_spread`, `marginal_spread`, `spread`

## Intended Use
- **Primary Use:** Decision support and physical regime estimation for microgravity solid combustible materials.
- **Intended Users:** Spacecraft fire-safety engineers, mission analysts, combustion researchers.
- **Out-of-Scope Use:** Never use for flight certification or safety-critical decisions without human verification and NASA-STD-6001 testing.

## Performance & Evaluation
- **Evaluation Scheme:** 5-fold Stratified Group K-Fold (`group=report_id`); investigation-level reported separately
- **Honest Grouped Accuracy:** 76.0%
- **Balanced Accuracy:** 35.6%
- **Macro F1 Score:** 0.3603
- **Naive Majority Baseline:** 81.5%

## Operational Envelope (Training Range)
- `oxygen_pct`: 14.0% to 31.0% vol
- `pressure_kpa`: 44.1 to 101.3 kPa
- `flow_cm_s`: 0.0 to 30.0 cm/s
- `material`: Cellulose, Cotton, Cotton-Fiberglass, Mylar, Nomex, PMMA, Silicone, Ultem

Requests outside these boundaries trigger a strict refusal state per the FLARE-X safety contract.
