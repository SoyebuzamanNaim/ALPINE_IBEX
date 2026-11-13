# Model Card: FLARE-X Flame-Spread Classifier

- Serving model: linear SVM, C=1.0, StandardScaler and training-fold OneHotEncoder.
- Mode: research estimates; not an operational safety model.
- Dataset: 200 observations; SHA-256 `26c383559b63ddee3cd5e1260fe15924d8438af89b8a8b74e5cf87d353af28e0`.
- Artifact SHA-256: `731043ccb86598c4563864b278bb60c3c5be6d4ceef96556c98a522ec3da18ca`.
- Trained: 2026-11-13T11:18:50+00:00.
- Inputs: oxygen_pct, pressure_kpa, flow_cm_s, material.
- Classes: no_spread, marginal_spread, spread.
- Exploratory grouped selection score: 84.0%.
- Majority baseline: 81.5%.
- Balanced accuracy: 40.3%.
- Macro-F1: 0.4215.
- Full search procedure nested accuracy: 0.255.
- Probability calibration: Internal SVM calibration; not validated across reports.

There are 7 report groups with row counts [158, 13, 12, 7, 6, 3, 1]; pooled metrics are row-weighted and dominated by the largest report. Only two marginal_spread records exist, so class-specific performance for that label is not statistically reliable. Treat scores as exploratory, not as evidence for operational or safety use.

The legacy `flame_spread_gb.joblib` filename is retained for loader compatibility;
`type=linear_svm` identifies its contents. Retraining uses the same fixed SVM configuration.

Public research estimates require dataset/artifact hashes to match and a grouped score above
the majority baseline. Individual predictions still abstain outside the material's joint
experimental domain, at conflicting conditions, or with insufficient material evidence.
Neither a no_spread prediction nor a model transition establishes safety. Geometry, flow
direction and ignition history are omitted by this four-input model. No independent external
validation or certification is claimed. The original gradient booster remains a comparison
in metrics.json; the experiment evidence records selection separately.

Exploratory model estimates only. The grouped score was used for model selection; probabilities are not validated across reports. No flight certification or safety clearance.
