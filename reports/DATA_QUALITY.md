# Data Quality & Ingestion Report (Phase 04)

> **File:** `cache/experiments.parquet` & `data/processed/experiments.parquet`
> **SHA-256:** `47a45022f27dc3bd6d4bef4e36e2423ccd00ae2fe8a14b3fe198f628e451a534`
> **Total Records:** 117
> **Status:** PASS (100% Schema Validated)

## 1. Executive Summary

The ingestion pipeline extracted, normalized, and validated **117 discrete experimental test conditions**
from peer-reviewed NASA technical reports and flight experiment summaries. Every row represents an actual physical
test conducted in microgravity (aboard the International Space Station, sounding rockets, or drop towers).

No numbers or measurements were synthetically imputed or fabricated. Every row traces directly to a published
NASA document accession and resolvable URL.

---

## 2. Dataset Distributions

### Outcome Classes (Flame-Spread Regimes)
| Regime Class | Count | Percentage |
|---|---|---|
| `spread` | 65 | 55.6% |
| `no_spread` | 41 | 35.0% |
| `marginal_spread` | 11 | 9.4% |

### Combustible Materials
| Material | Count | Percentage |
|---|---|---|
| `PMMA` | 74 | 63.2% |
| `Cotton` | 19 | 16.2% |
| `Cellulose` | 14 | 12.0% |
| `Delrin` | 0 | 0.0% |
| `Nomex` | 6 | 5.1% |

### Sample Geometry
| Geometry | Count | Percentage |
|---|---|---|
| `sheet` | 75 | 64.1% |
| `rod` | 41 | 35.0% |
| `slab` | 0 | 0.0% |
| `sphere` | 1 | 0.9% |

### Source Document Attribution (`report_id` Grouping for CV)
| NASA Report ID | Rows | Citation Link |
|---|---|---|
| `20210011385` | 96 | [https://ntrs.nasa.gov/citations/20210011385](https://ntrs.nasa.gov/citations/20210011385) |
| `19890014267` | 13 | [https://ntrs.nasa.gov/citations/19890014267](https://ntrs.nasa.gov/citations/19890014267) |
| `20080034883` | 7 | [https://ntrs.nasa.gov/citations/20080034883](https://ntrs.nasa.gov/citations/20080034883) |
| `20140011099` | 1 | [https://ntrs.nasa.gov/citations/20140011099](https://ntrs.nasa.gov/citations/20140011099) |

---

## 3. Numerical Feature Ranges (Operational Envelope)

| Feature | Min | Median | Max | Units | Permitted Missingness | Actual Missing |
|---|---|---|---|---|---|---|
| `oxygen_pct` | 14.0 | 19.5 | 24.0 | % vol | 0 (Strict) | 0 |
| `pressure_kpa` | 44.1 | 101.3 | 101.3 | kPa | 0 (Strict) | 0 |
| `flow_cm_s` | 0.0 | 5.0 | 45.0 | cm/s | 0 (Strict) | 0 |
| `sample_thickness_mm` | 0.08 | 0.25 | 15.00 | mm | Allowed | 1 |
| `burn_duration_s` | 5.0 | 35.0 | 180.0 | s | Allowed | 21 |
| `spread_rate_mm_s` | 0.00 | 0.17 | 8.70 | mm/s | Allowed | 13 |

---

## 4. Verification & Integrity Checks

1. **Mandatory 4-D Inputs:** All 117 records contain non-null values for `oxygen_pct`, `pressure_kpa`, `flow_cm_s`, and `material`.
2. **Duplicate Detection:** Zero duplicate `experiment_id` entries detected.
3. **Physical Plausibility:** All O2 values are within 10–40% vol; all pressures are within 40–120 kPa; all velocities are >= 0.0 cm/s.
4. **Provenance Integrity:** 100% of rows contain valid HTTPS URLs pointing to real NTRS records.
