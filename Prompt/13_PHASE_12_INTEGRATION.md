# PHASE 12 — Full Integration

## Goal
Make FLARE-X work end to end.

## Flow
User scenario
→ API
→ scenario parser
→ evidence retrieval
→ model router
→ model prediction
→ envelope guard
→ counterfactual option
→ evidence auditor
→ frontend

## Tasks
- freeze API contracts
- connect all services
- version models/datasets
- add structured logs
- graceful failure states
- offline/local fallback where feasible
- end-to-end tests

## Required End-to-End Test Cases
1. supported scenario
2. boundary scenario
3. unsupported scenario
4. missing variable scenario
5. no evidence found
6. API/model failure

## Outputs
- tests/test_end_to_end.py
- reports/INTEGRATION_REPORT.md
- scripts/run_local.*

## Pass Criteria
One command launches the complete prototype and all E2E scenarios behave correctly.
