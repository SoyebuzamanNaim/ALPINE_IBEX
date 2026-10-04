# PHASE 03 — Data Audit & Schema

## Goal
Create a scientifically safe harmonization strategy.

## Build a crosswalk for
- investigation
- experiment ID
- fuel
- material
- oxygen
- pressure
- airflow
- geometry
- droplet diameter
- burner diameter
- suppressant
- temperature
- ignition
- extinction
- burn duration
- flame length
- spread rate
- smoke
- soot
- radiation
- source file
- source URL

## For every field classify
- directly observed
- derived
- categorical mapping
- unavailable
- ambiguous

## Design
- canonical unit system
- provenance schema
- missingness policy
- dataset-specific extension tables
- group IDs for leakage-safe splitting

## Outputs
- docs/VARIABLE_CROSSWALK.md
- docs/SCHEMA.md
- data/metadata/schema.json
- data/metadata/unit_map.json

## Pass Criteria
- no incompatible variables are silently merged
- unit conversions are explicit
- raw meanings are preserved
- provenance is mandatory
