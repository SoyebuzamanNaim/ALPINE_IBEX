# Phase 05 Validation Gate

## Status
PASS

## Requirements Checklist
- [x] Small gradient-boosting classifier trained for flame-spread regime
- [x] Features: `oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `material`
- [x] Compared against naive majority-class baseline and logistic regression
- [x] Honest cross-validation: `StratifiedGroupKFold` grouped by `report_id`
- [x] Plain stratified k-fold reported beside grouped CV
- [x] Accuracy, balanced accuracy, macro-F1, per-class recall, and confusion matrix published
- [x] Fixed random seed (`RANDOM_SEED = 42`)
- [x] Results saved in `reports/BASELINE_RESULTS.md` and `models/metrics.json`
- [x] Artifact saved to `models/flame_spread_gb.joblib`
- [x] Metadata saved to `models/model_meta.json` with `training_range`
- [x] Automated tests created in `tests/test_models.py` and passing (6/6)

## Automated Tests
| Test | Result | Evidence |
|---|---|---|
| `test_model_files_exist` | PASS | Artifact, meta, and metrics exist |
| `test_model_meta_schema` | PASS | All contract fields present; grouped CV verified |
| `test_prediction_in_range` | PASS | Probabilities sum to 1.0; valid class returned |
| `test_refusal_when_out_of_range` | PASS | Out-of-range returns `prediction=null`, `probabilities=null` |
| `test_refusal_on_unsupported_material` | PASS | Refusal on unseen materials |
| `test_metrics_comparisons_exist` | PASS | 4 model families evaluated with grouped metrics |

## Scientific Checks
| Check | Result | Notes |
|---|---|---|
| No leakage across experiments | PASS | `report_id` used for grouped splitting |
| Real metrics reported honestly | PASS | 79.31% grouped accuracy reported with full confusion matrix |
| Operational range strictly checked | PASS | Training ranges enforced; refuses out-of-domain extrapolation |

## Repair Attempts
1. n/a (clean run)

## Decision
Advance to Phase 06 (Evidence Retrieval Engine).
