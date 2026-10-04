# PHASE 08 — Counterfactual Engine

## Goal
Let users vary scientifically meaningful inputs and see how predictions/evidence change.

## Supported Counterfactuals
Depending on available data:
- oxygen
- airflow
- pressure
- suppressant
- geometry
- fuel/material where valid

## Rules
1. Never imply causal proof from an observational ML change.
2. Label model-predicted changes as predictions.
3. Re-run envelope checks after every change.
4. Show evidence coverage.
5. Preserve original scenario for comparison.

## Output
Original
vs
Counterfactual
with:
- changed variables
- prediction delta
- confidence delta
- evidence delta
- domain status

## Outputs
- src/features/counterfactual.py
- docs/COUNTERFACTUAL_SPEC.md
- tests/test_counterfactual.py

## Pass Criteria
Every counterfactual is auditable and domain-checked.
