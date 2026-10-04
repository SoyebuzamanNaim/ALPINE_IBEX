# PHASE 13 — Validation & Red Team

## Goal
Try to break the prototype.

## Data Validation
- duplicate audit
- missingness
- unit consistency
- impossible values
- provenance

## ML Validation
- leakage
- split quality
- class imbalance
- calibration
- confidence
- error analysis

## Retrieval Validation
- wrong source
- irrelevant source
- contradictory source
- zero evidence

## Agent Red Team
Prompts that request:
- invented NASA facts
- unsupported certainty
- invalid units
- impossible conditions
- hidden evidence
- bypass of safety guard

## Frontend Red Team
- mobile
- no data
- bad API
- long citations
- slow responses
- empty charts

## Outputs
- reports/VALIDATION_REPORT.md
- reports/RED_TEAM_REPORT.md
- reports/LIMITATIONS.md

## Pass Criteria
Critical failures fixed or explicitly blocked with safe UX.
