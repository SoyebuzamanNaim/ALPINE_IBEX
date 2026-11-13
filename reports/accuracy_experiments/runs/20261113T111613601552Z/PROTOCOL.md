# Accuracy experiment protocol — 2026-11-13

This protocol is frozen before running the new experiments. The canonical 200-row,
three-class dataset and all labels stay unchanged. Its SHA-256 is recorded by the runner.
No fabricated observations, synthetic test data, outcome-derived features, label merging,
random row splits, seed shopping, or NASA equations fitted on these observations are used.

## Selection and evaluation

- Primary experiment: the existing four API inputs only: oxygen, pressure, flow, material.
- Separate context experiment: also use recorded sample geometry, thickness, and flow
  direction. These are pre-experiment inputs, but require a different API contract.
- Each pool uses nested leave-one-report-out CV. Seven outer reports are held out in turn.
  Each candidate is selected using leave-one-report-out CV on the remaining six reports.
  The selection objective is pooled accuracy, then balanced accuracy, then macro-F1;
  exact ties prefer the earlier candidate in the frozen grid. No outer score selects settings.
- All scaling, imputation, category encoding, and model fitting occur inside training folds.
  An absent class in training stays absent; the two marginal cases are retained in evaluation.
- Report the frozen production model and the training-fold majority predictor on the same
  outer folds. Report full-grid ordinary grouped CV as tuning evidence only, not a fresh test.
- Save every candidate's score, each selected configuration, and every nested outer prediction.
  The runner hashes its own source and the grid for reproducibility. All estimator seeds are 42.
- Report pooled accuracy, three-class balanced accuracy, macro-F1, per-class recall,
  no_spread precision, false-safe calls, and per-report accuracy. A report bootstrap provides
  a descriptive uncertainty interval; seven reports are too few for a strong inference.
- As a sensitivity check, repeat scoring of the selected procedure after purging exact
  four-input condition overlaps across train/test reports. Independently measured identical
  conditions are not necessarily duplicate observations, so distinguish this from report CV.

## Candidate grid

The complete machine-readable grid is saved before fitting. It covers logistic regression
with regularization and class weights; RBF and linear SVMs; random forests and extra trees;
shallow gradient and histogram boosting; nearest neighbors; shrinkage discriminant analysis;
Gaussian naive Bayes; and a majority control. Numeric variants are raw inputs, quadratic
terms, and unfitted oxygen partial-pressure/flow transformations. Context candidates are
scored separately and never compete with four-input candidates for the primary result.

## Interpretation and promotion

This dataset has already been examined and tuned in earlier work. Nested CV reduces selection
bias within this run; it does not create an independent external validation set or erase prior
human exposure. Do not claim a global maximum or operational safety from these experiments.
Any saved candidate is a research artifact. Production artifacts and the public inference gate
are preserved unless the complete evaluation supports a separately documented promotion.
