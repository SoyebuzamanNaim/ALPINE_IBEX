# PHASE 10 — Backend API

## Goal
Expose all verified FLARE-X capabilities through stable APIs.

## Suggested Endpoints
- GET /health
- GET /datasets
- GET /experiments
- POST /scenario/parse
- POST /evidence/search
- POST /predict
- POST /envelope/check
- POST /counterfactual
- POST /analyze
- GET /sources/{id}

## API Requirements
- Pydantic/schema validation
- unit validation
- source IDs in output
- model version
- dataset version
- error codes
- timeouts
- logging

## Outputs
- src/api/
- docs/API_CONTRACT.md
- tests/test_api.py

## Pass Criteria
All endpoints have tests and never emit fake values.
