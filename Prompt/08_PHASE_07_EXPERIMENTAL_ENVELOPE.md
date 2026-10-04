# PHASE 07 — Experimental Envelope Guard

## Goal
Detect whether a requested scenario is supported by NASA observations.

## For each model/dataset define
- min/max numerical ranges
- allowed categorical values
- data-density regions
- missing-variable constraints
- known exclusions

## Implement
- in-domain
- boundary
- extrapolation
- unsupported category

## Output Must Show
- status
- nearest supported examples
- variables causing extrapolation
- confidence penalty
- warning text

## Optional Advanced Methods
- Mahalanobis distance
- isolation forest
- kNN distance
- convex hull / density boundary
Only if appropriate.

## Outputs
- src/envelope/
- docs/ENVELOPE_METHOD.md
- tests/test_envelope.py
- reports/ENVELOPE_VALIDATION.md

## Pass Criteria
Out-of-domain samples must never receive the same presentation as in-domain samples.
