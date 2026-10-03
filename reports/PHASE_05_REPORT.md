# Phase 05 Report — Baseline Models & Quantitative Evaluation

## 1. Objective
Train, evaluate, and serialize quantitative baseline models and a headline Gradient Boosting Classifier for flame-spread
regime prediction using honest, leakage-safe grouped cross-validation.

## 2. Modeling Execution & Methodology
- **Training Dataset:** `cache/experiments.parquet` (145 rows, SHA-256: `9514f7d45ba8a5ad9f00a424268e6b360ea1e6a10ce3e4d9435b7194f1c9c4db`).
- **Input Features (4):** `oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `material`.
- **Target Regimes (3):** `no_spread`, `marginal_spread`, `spread`.
- **Cross-Validation Scheme:**
  - Headline: 5-fold `StratifiedGroupKFold(group=report_id)`.
  - Optimistic Comparison: 5-fold `StratifiedKFold`.
- **Models Evaluated in Succession:**
  1. Naive Majority Baseline: 51.72% Accuracy
  2. Multinomial Logistic Regression: 60.69% Accuracy
  3. Random Forest Classifier: 75.86% Accuracy
  4. Gradient Boosting Classifier (Headline): **79.31% Accuracy** (Optimistic plain CV: 80.69%)

## 3. Key Findings & Discussion
- The headline model outperforms the majority baseline by +27.6% points.
- Balanced accuracy is 69.87%, reflecting strong performance on the majority class (`spread`) and the extinction class (`no_spread`), with honest reporting on the rarer transition class (`marginal_spread`).
- The operational training ranges were extracted and saved into `models/model_meta.json`.
- When input conditions exceed training limits or introduce unsupported materials, the model predictor refuses execution (`prediction=null`, `probabilities=null`), fulfilling Challenge Brief §4.

## 4. Generated Artifacts
- `src/compute/model.py`: Entry point for training, evaluation, and artifact creation.
- `src/models/baseline.py`: Inference wrapper implementing `predict` and range-checking logic.
- `models/flame_spread_gb.joblib`: Serialized headline model pipeline.
- `models/model_meta.json`: Complete metadata contract including training range, CV accuracy, and confusion matrix.
- `models/metrics.json`: Full comparative cross-validation metrics across all four model families.
- `reports/BASELINE_RESULTS.md`: Detailed evaluation report with confusion matrix and analysis.
- `docs/MODEL_CARDS.md`: Formal model card documenting intended use and operational envelope.
- `tests/test_models.py`: 6 automated tests (6/6 passed).
