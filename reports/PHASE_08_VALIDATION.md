# Phase 08 Validation: Counterfactual Engine

## Status: PASS
- **Test File:** `tests/test_counterfactual.py`
- **Results:** 6 passed in 1.82s
- **All Project Tests:** 35 passed in 3.65s

## Verification Matrix

| Test Name | Conditions Evaluated | Metric / Feature Tested | Result |
|---|---|---|---|
| `test_evaluate_scenario_in_domain` | PMMA, 21% O2, 101.3 kPa, 5 cm/s | Prediction, class probabilities, nearest experiments | PASS |
| `test_evaluate_scenario_out_of_range` | PMMA, 45% O2, 101.3 kPa, 5 cm/s | Refusal contract (`prediction: null`, reasons given) | PASS |
| `test_compute_perturbation_oxygen_drop` | PMMA, 21% -> 16.5% O2 | Delta calculation, probability drop in spread, evidence shift | PASS |
| `test_run_sweep_oxygen_boundary` | PMMA, 21% -> 16% O2 (11 steps) | Transition detection, midpoint estimation, safety margin | PASS |
| `test_sweep_invalid_parameter` | Sweep over categorical 'material' | Raises ValueError with descriptive message | PASS |
| `test_counterfactual_unsupported_material` | PMMA -> Teflon | Refuses counterfactual with `unsupported_category` | PASS |

## Pass Criteria Verification
- [x] Every counterfactual is auditable and domain-checked through EnvelopeGuard.
- [x] Original scenario is preserved alongside counterfactual for direct comparison.
- [x] Model-predicted changes are explicitly labeled as observational predictions.
- [x] Non-causal scientific disclaimer included in all perturbation results.
- [x] Oxygen sweep demonstration detects physical flammability boundary with real NASA evidence cited on both sides.
