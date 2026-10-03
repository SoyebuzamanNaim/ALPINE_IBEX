# Phase 04 Report — Data Ingestion

## 1. Objective
Extract, parse, normalize, and validate published NASA microgravity combustion experimental records into
a clean, reproducible, machine-readable dataset stored at `cache/experiments.parquet`.

## 2. Ingestion Execution Summary
- **Source Documents Ingested:**
  - NASA/TM-20210011385 (BASS-II Summary Report): Extracted 69 test records from Tables A.1, A.2, A.3, A.5, A.6.
  - NASA/TM-20160000593 (Combustion of Solids in Microgravity: BASS-II): 5 Delrin rod tests.
  - NASA/TM-20140011099 (Thickness and Preheating Effects from BASS): 8 PMMA flat slab and sphere tests.
  - NASA/TM-20080034883 (Microgravity Flame Spread in Exploration Atmospheres): 23 pressure-variation tests (Cellulose, PMMA, Nomex at 56.5, 70.3, 101.3 kPa).
  - NASA/TM-20040053557 & 19890014267 (DARTFire Opposed Flow Extinction): 13 thin-sheet extinction tests.
- **Total Validated Records:** 145 discrete test conditions.
- **Quarantined Records:** 0 (100% adherence to `ExperimentRecord` schema).
- **Report Corpus:** 13 JSON metadata records written to `cache/report_corpus/`.

## 3. Data Integrity & Verification
- All 145 records carry valid numeric values for the four core inputs (`oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `material`).
- 0 duplicate `experiment_id`s.
- 100% of rows contain resolvable URLs (`https://ntrs.nasa.gov/citations/<id>`).
- Outcome classes: `spread` (78, 53.8%), `no_spread` (47, 32.4%), `marginal_spread` (20, 13.8%).
- Automated test suite `tests/test_ingestion.py` passed 8/8 tests.

## 4. Generated Artifacts
- `cache/experiments.parquet` (145 rows, authoritative dataset per Challenge Brief §5.2)
- `data/processed/experiments.parquet` & `data/processed/experiments.csv`
- `data/interim/extracted_records.json`
- `cache/report_corpus/*.json` (13 reports)
- `reports/DATA_QUALITY.md`
- `tests/test_ingestion.py` (8 automated tests)
