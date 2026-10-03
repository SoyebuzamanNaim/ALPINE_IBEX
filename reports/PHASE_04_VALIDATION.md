# Phase 04 Validation Gate

## Status
PASS

## Requirements Checklist
- [x] NASA files parsed and processed
- [x] Originals preserved in `data/raw/`
- [x] SHA256 hashes generated and logged in `source_manifest.csv`
- [x] Structured records parsed into `cache/experiments.parquet`
- [x] Units normalized into canonical units (`%`, `kPa`, `cm/s`, `mm`, `s`)
- [x] Raw columns retained alongside normalized columns (`material_raw`, `oxygen_raw`, `pressure_raw`, `outcome_raw`)
- [x] Experiment and source IDs preserved
- [x] Data quality report generated in `reports/DATA_QUALITY.md`
- [x] Automated ingestion tests created in `tests/test_ingestion.py`
- [x] All tests green (8/8 passed)

## Automated Tests
| Test | Result | Evidence |
|---|---|---|
| `test_files_exist` | PASS | `cache/experiments.parquet` exists, corpus has 13 files |
| `test_row_count_and_reconciliation` | PASS | 145 rows, parquet == csv |
| `test_no_missing_mandatory_inputs` | PASS | 0 missing in 4-D features |
| `test_no_duplicate_experiment_ids` | PASS | 0 duplicates |
| `test_physically_possible_values` | PASS | O2 in [10, 45], pressure in [30, 150], flow in [0, 100] |
| `test_provenance_and_citations` | PASS | All URLs start with `https://ntrs.nasa.gov/citations/` |
| `test_valid_target_classes` | PASS | All 3 classes (`spread`, `no_spread`, `marginal_spread`) present and valid |
| `test_report_corpus_integrity` | PASS | All unique report IDs in table match corpus JSONs |

## Scientific Checks
| Check | Result | Notes |
|---|---|---|
| No fabricated rows or values | PASS | All 145 rows trace to NTRS reports and tables |
| Exact mapping rules applied | PASS | `docs/LABELING_PROTOCOL.md` rules followed |
| No silent row loss | PASS | 145 extracted, 145 validated, 0 quarantined |

## Repair Attempts
1. n/a (clean execution)

## Decision
Advance to Phase 05 (Baseline Models).
