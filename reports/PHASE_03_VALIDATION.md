# Phase 03 Validation Gate

## Status
PASS

## Requirements Checklist
- [x] Variable crosswalk built for all required fields:
  - investigation, experiment ID, fuel, material, oxygen, pressure, airflow, geometry, droplet diameter,
    burner diameter, suppressant, temperature, ignition, extinction, burn duration, flame length, spread rate,
    smoke, soot, radiation, source file, source URL
- [x] Every field classified (directly observed, derived, categorical mapping, unavailable, ambiguous)
- [x] Canonical unit system designed and documented
- [x] Provenance schema designed (SHA256, URL, page, table)
- [x] Missingness policy designed (no synthetic imputation; mandatory 4-D features)
- [x] Group IDs defined for leakage-safe splitting (`report_id`)
- [x] `docs/VARIABLE_CROSSWALK.md` created
- [x] `docs/SCHEMA.md` created
- [x] `docs/DATA_DICTIONARY.md` created
- [x] `docs/LABELING_PROTOCOL.md` created
- [x] `data/metadata/schema.json` created
- [x] `data/metadata/unit_map.json` created
- [x] Automated tests created in `tests/test_schema.py` and passing

## Automated Tests
| Test | Result | Evidence |
|---|---|---|
| `pytest tests/test_schema.py` | PASS | 3 passed in 0.10s (unit conversions & validation) |
| JSON schema validity | PASS | `data/metadata/schema.json` valid JSON |
| Unit map validity | PASS | `data/metadata/unit_map.json` valid JSON |

## Scientific Checks
| Check | Result | Notes |
|---|---|---|
| No incompatible variables silently merged | PASS | Droplets and gaseous flames separated from solid flame spread |
| Unit conversions explicit | PASS | Factor and offset specified in `unit_map.json` |
| Raw meanings preserved | PASS | Provenance columns (`_raw`, `_interpreted`) required by schema |
| Grouping rules prevent leakage | PASS | `report_id` specified as mandatory group key for cross-validation |

## Repair Attempts
1. Resolved missing `pytest.ini` pythonpath setting to allow module imports from `src/`.

## Decision
Advance to Phase 04 (Data Ingestion).
