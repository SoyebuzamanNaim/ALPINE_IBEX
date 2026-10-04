# PHASE 04 — Data Ingestion

## Goal
Build reproducible ingestion pipelines.

## Tasks
1. Download selected NASA files.
2. Preserve originals in data/raw.
3. Create SHA256 hashes.
4. Parse structured files.
5. Extract metadata.
6. Normalize units into processed tables.
7. Retain raw columns alongside normalized columns.
8. Preserve experiment and source IDs.
9. Generate data-quality reports.
10. Add ingestion tests.

## Required Tests
- row/record count reconciliation
- hash verification
- missingness profile
- duplicate detection
- invalid unit detection
- impossible value detection
- provenance retention
- no silent row loss

## Outputs
- src/ingestion/
- data/raw/
- data/interim/
- data/processed/
- reports/DATA_QUALITY.md
- tests/test_ingestion.py

## Pass Criteria
Ingestion must be reproducible from a clean environment.
