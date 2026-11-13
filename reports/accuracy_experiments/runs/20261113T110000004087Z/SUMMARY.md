# Accuracy experiments — 2026-11-13

Ran **135 frozen configurations** on the unchanged **200-row,
three-class dataset**, with seven report groups. Each candidate has 7 outer fits and
21 reusable pair-exclusion fits for nested selection. Repeating the complete procedure
with exact-condition purging gives **7,560 validation fits** in total.

The highest ordinary report-grouped accuracy is **84.0%**, versus
**77.5%** for production and **81.5%** for the majority
control. It is a **selection score**, chosen from the grid; it is not an independent estimate
of the selected model's accuracy. The nested procedure did not establish an improvement.
**No candidate is promoted; public predictions remain withheld.**

## Results

| Procedure | Accuracy | Balanced accuracy (3 classes) | Macro-F1 | no_spread precision | False-safe calls |
|---|---:|---:|---:|---:|---:|
| Current production (fixed) | 77.5% | 36.2% | 0.3637 | 31.6% | 13 |
| Training-fold majority | 81.5% | 33.3% | 0.2994 | N/A | 0 |
| Best four-input candidate (selection score only) | 84.0% | 40.3% | 0.4215 | 80.0% | 2 |
| Nested selection, four inputs | 25.5% | 26.9% | 0.1706 | 14.2% | 133 |
| Nested selection, seven inputs | 81.5% | 34.1% | 0.3172 | 50.0% | 1 |

All 200 rows, including both marginal_spread examples, count in these scores. The three-class
majority balanced-accuracy floor is 33.3%. Older binary evaluations in
REBUILT_MODEL_EVALUATION.md dropped the marginal class and cannot be compared directly.
"False-safe" counts true spread or marginal_spread observations predicted as no_spread.

## Best candidate and why it is still experimental

The four-input candidate is **exp_065**, a `svm` with
`{"C": 1.0, "class_weight": null, "kernel": "linear"}` and fold-fitted scaling/category encoding. Its ordinary grouped
confusion matrix, rows=true and columns=predicted in order no_spread, marginal_spread, spread:

```text
[[8, 0, 27], [0, 0, 2], [2, 1, 160]]
```

It detects only 8/35 no_spread cases and
0/2 marginal cases. Its no_spread precision rests on
10 predictions. Probabilities have not been validated or calibrated
across reports. The seven-input candidate requires sample thickness, geometry and flow
direction, which the current API does not collect.

## Nested evaluation exposes a transfer failure

Every outer report is excluded from both tuning and fitting. Inner selection ranks candidates
by pooled accuracy, then balanced accuracy, then macro-F1. Each outer fold uses its own selected
candidate. This evaluates the entire selection procedure, rather than quoting its best score.

| Excluded report | Train rows | Test rows | Inner-selected candidate | Inner accuracy | Outer accuracy |
|---|---:|---:|---|---:|---:|
| 19890014267 | 187 | 13 | exp_100 (hist_boosting) | 83.4% | 46.2% |
| 20080034883 | 193 | 7 | exp_065 (svm) | 83.9% | 57.1% |
| 20140011099 | 199 | 1 | exp_065 (svm) | 83.4% | 0.0% |
| 20170008805 | 188 | 12 | exp_020 (logistic) | 84.6% | 41.7% |
| 20210011385 | 42 | 158 | exp_110 (gaussian_nb) | 73.8% | 17.1% |
| 20210011521 | 194 | 6 | exp_103 (knn) | 82.0% | 100.0% |
| 20240002981 | 197 | 3 | exp_016 (logistic) | 82.7% | 100.0% |

BASS-II supplies 158/200 rows. Excluding it leaves only 42 training rows from six different
reports. The inner-selected model transfers poorly to BASS-II; its failure remains included
in the headline nested result. Choosing another model after seeing that failure would use
outer evaluation results for tuning. The frozen search was not changed to repair this score.

The descriptive report-bootstrap 95% interval for nested four-input accuracy is
[18.7%,
73.2%]. With only seven highly unequal reports,
this is not strong uncertainty quantification or evidence of operational safety.

## Leakage checks and sensitivity

- Outcomes, observation text, failure mode, burn duration/rate, IDs, report identity and
  citations are excluded from model features. All classes and observations are retained.
- Preprocessing fits inside every training fold. Whole reports, including sibling sweep
  observations, stay together. The two-report exclusion cache is equivalent to the nested
  inner folds and never fits on the outer report.
- There is one cross-report exact four-input condition overlap (Saffire II/IV). Purging such
  conditions from training and rerunning the entire nested search yields
  **25.5%** for four inputs and
  **81.5%** for seven inputs.
  It does not repair the transfer failure.
- No synthetic rows, relabeling, class merging, favorable row splits, seed selection, fitted
  NASA boundary features, or exclusion of bad folds was used. All random seeds are 42.
- The dataset was already inspected in previous work. Nested CV does not erase that exposure.
  An independent report with source-supported outcomes is required to confirm an improvement.

## Best ordinary grouped score per family (tuning evidence only)

| Input pool | Family | Candidate | Accuracy | Balanced accuracy |
|---|---|---|---:|---:|
| base | boosting | exp_092 | 81.0% | 35.4% |
| base | extra_trees | exp_079 | 82.0% | 35.0% |
| base | forest | exp_067 | 81.5% | 33.3% |
| base | gaussian_nb | exp_111 | 76.5% | 34.3% |
| base | hist_boosting | exp_098 | 76.5% | 35.0% |
| base | knn | exp_103 | 81.5% | 34.1% |
| base | lda | exp_108 | 79.0% | 38.3% |
| base | logistic | exp_016 | 82.5% | 36.0% |
| base | majority | exp_000 | 81.5% | 33.3% |
| base | production | exp_113 | 77.5% | 36.2% |
| base | svm | exp_065 | 84.0% | 40.3% |
| context | boosting | exp_129 | 79.0% | 39.0% |
| context | extra_trees | exp_124 | 81.5% | 34.1% |
| context | forest | exp_120 | 82.0% | 35.8% |
| context | logistic | exp_116 | 81.5% | 36.3% |
| context | majority | exp_134 | 81.5% | 33.3% |
| context | svm | exp_132 | 81.5% | 34.1% |

## Artifacts and reproduction

```bash
.venv/bin/python -m src.compute.experiments --jobs 6
.venv/bin/pytest -q tests/test_accuracy_experiments.py tests/test_models.py tests/test_model_governance.py
.venv/bin/python scripts/verify_artifacts.py
```

`grid.json` records every configuration; `candidate_scores.csv` includes unsuccessful models;
`outer_predictions.csv` records all outer answers, including the selected candidates' ordinary
grouped predictions; `results.json` includes nested choices, confusion matrices, warnings,
versions and hashes. `PROTOCOL.md` was written before the experiment.

Saved research models: `models/accuracy_candidate_base.joblib` and
`models/accuracy_candidate_context.joblib`, with separate metadata files. Their metadata
explicitly withholds public approval. Production model, dataset, metrics, and API gate were
not replaced. The base candidate uses the existing four fields; the context candidate needs
seven. No global optimum or validated accuracy gain is claimed.

Method reference: [scikit-learn nested versus non-nested cross-validation](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html).

Dataset SHA-256: `26c383559b63ddee3cd5e1260fe15924d8438af89b8a8b74e5cf87d353af28e0`.
