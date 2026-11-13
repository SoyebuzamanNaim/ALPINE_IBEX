# Model Card: FLARE-X Flame-Spread Classifier

## Model Details
- **Model Name:** FLARE-X Flame Spread Gradient Boosting Classifier
- **Model Version:** 1.0.0
- **Model Type:** Scikit-Learn `GradientBoostingClassifier` with `StandardScaler` and `OneHotEncoder`
- **Trained Date:** 2026-11-13T10:23:38+00:00
- **Dataset SHA-256:** `26c383559b63ddee3cd5e1260fe15924d8438af89b8a8b74e5cf87d353af28e0`
- **Model Artifact SHA-256:** `b19a775e2f4af1f76ecf2ed789fa3c95b33d0ab42dae48bd008d201665e06d8a`
- **Training Samples (N):** 200
- **Input Features (4):** `oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `material`
- **Target Classes (3):** `no_spread`, `marginal_spread`, `spread`

## Intended Use
- **Primary Use:** Research and software evaluation only. Public model estimates are withheld while the model fails the baseline gate.
- **Intended Users:** Combustion researchers and software maintainers inspecting the evidence pipeline.
- **Out-of-Scope Use:** Flight certification, operational spacecraft fire-safety decisions, or emergency response.

## Performance & Evaluation
- **Evaluation Scheme:** LeaveOneGroupOut(group=report_id); investigation-level evaluation is reported separately
- **Honest Grouped Accuracy:** 77.5%
- **Balanced Accuracy:** 36.2%
- **Macro F1 Score:** 0.3637
- **Naive Majority Baseline:** 81.5%

## Operational Envelope (Training Range)
- `oxygen_pct`: 14.0% to 31.0% vol
- `pressure_kpa`: 44.1 to 101.3 kPa
- `flow_cm_s`: 0.0 to 30.0 cm/s
- `material`: Cellulose, Cotton, Cotton-Fiberglass, Mylar, Nomex, PMMA, Silicone, Ultem

The envelope guard also checks joint empirical coverage and abstains for unsupported or sparse material evidence.
