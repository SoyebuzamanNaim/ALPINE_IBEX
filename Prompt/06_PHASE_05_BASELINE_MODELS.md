# PHASE 05 — Baseline Models

## Goal
Establish scientifically defensible quantitative tasks.

## Candidate Tasks
Only enable a task if the actual data support it.

### FLEX
Possible:
- sustained vs extinction classification
- extinction-condition analysis

### SPICE
Possible:
- flame length regression
- smoke-point-related classification/regression

### BASS / SAFFIRE
Possible:
- flame spread behavior
- extinction
- burn behavior

## Required Modelling Order
1. naive baseline
2. linear/logistic baseline
3. random forest
4. gradient boosting
5. optional advanced model only if justified

## Split Rules
Use grouping where repeated conditions/experiments could leak.
Never random-split correlated measurements without analysis.

## Metrics
Classification:
- precision
- recall
- F1
- balanced accuracy
- ROC-AUC when valid
- PR-AUC for imbalance
- Brier/calibration

Regression:
- MAE
- RMSE
- R²

## Outputs
- src/models/
- models/
- reports/BASELINE_RESULTS.md
- docs/MODEL_CARDS.md
- tests/test_models.py

## Pass Criteria
- baseline comparison exists
- metrics reproducible
- no leakage
- limitations documented
