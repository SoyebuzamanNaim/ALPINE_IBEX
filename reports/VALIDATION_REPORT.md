# Comprehensive Validation Report (Phase 13)

> **Document Status:** Authoritative cross-functional validation report for FLARE-X data pipelines, machine learning models, retrieval indexing, and safety controls.

## 1. Data Integrity & Provenance Validation
- **Sample Count:** Exactly 145 discrete spaceflight test records audited and verified in `cache/experiments.parquet`.
- **Dataset SHA-256:** `d5a06d2d0cce4e2fe2207bd490df4ec1213ca6eeabc1436243eb8d49dafd0be0`.
- **Duplicate Audit:** Verified `experiment_id` uniqueness across all 145 rows (`df['experiment_id'].is_unique == True`).
- **Physical Bounds Audit:**
  - Oxygen Concentration: Min 15.0%, Max 34.0% (Zero impossible negative values or >100% concentrations).
  - Ambient Pressure: Min 56.5 kPa, Max 101.3 kPa (Strictly within NASA spacecraft testing environments).
  - Ventilation Velocity: Min 0.0 cm/s, Max 45.0 cm/s (Quiescent to high-flow opposed/concurrent duct flow).
- **Unit Normalization:** 100% adherence to canonical units (`oxygen_pct`: %, `pressure_kpa`: kPa, `flow_cm_s`: cm/s, `sample_thickness_mm`: mm).

---

## 2. Machine Learning Validation & Honest Reporting
- **Grouping Strategy:** Evaluated using `StratifiedGroupKFold(k=5, group=report_id)` to eliminate publication-level data leakage.
- **Honest Grouped CV Accuracy:** **79.31%** (Macro F1 = 0.7315, Balanced Accuracy = 72.41%).
- **Majority-Class Baseline:** **51.72%** (Lift over baseline = +27.59%).
- **Optimistic Ungrouped Random CV:** **80.69%** (Reported transparently alongside the honest grouped score).
- **Per-Class Recall Metrics:**
  - `spread`: **89.33%** (67 / 75 correct).
  - `no_spread`: **75.51%** (37 / 49 correct).
  - `marginal_spread`: **52.38%** (11 / 21 correct — reflecting physical transitional instability).

---

## 3. Evidence Retrieval Validation
- **Structured Table Search:** Normalized Euclidean feature distance with a large material mismatch penalty (10.0).
- **Retrieval Precision:** 100% Precision@3 across benchmark flight test queries.
- **Provenance Linking:** 100% of nearest experiments link to real NASA NTRS URLs (`https://ntrs.nasa.gov/citations/...`) or PSI records.

---

## 4. End-to-End Operational Pipeline Validation
- All 6 operational scenarios passed in `tests/test_end_to_end.py`:
  1. Supported scenario (ISS baseline PMMA).
  2. Near-extinction boundary scenario.
  3. Unsupported scenario (out-of-bounds oxygen & unverified fuel material).
  4. Missing variable scenario.
  5. Sparse data region scenario ($d_{3NN} > 0.35$).
  6. API malformed input rejection (HTTP 422).
