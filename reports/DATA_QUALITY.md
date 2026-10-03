# Data Quality & Ingestion Report (Phase 04)

> **File:** `cache/experiments.parquet` & `data/processed/experiments.parquet`
> **SHA-256:** `d5a06d2d0cce4e2fe2207bd490df4ec1213ca6eeabc1436243eb8d49dafd0be0`
> **Total Records:** 145
> **Status:** PASS (100% Schema Validated)

## 1. Executive Summary

The ingestion pipeline extracted, normalized, and validated **145 discrete experimental test conditions**
from peer-reviewed NASA technical reports and flight experiment summaries. Every row represents an actual physical
test conducted in microgravity (aboard the International Space Station, sounding rockets, or drop towers).

No numbers or measurements were synthetically imputed or fabricated. Every row traces directly to a published
NASA document accession and resolvable URL.

---

## 2. Dataset Distributions

### Outcome Classes (Flame-Spread Regimes)
| Regime Class | Count | Percentage |
|---|---|---|
| `spread` | 75 | 51.7% |
| `no_spread` | 49 | 33.8% |
| `marginal_spread` | 21 | 14.5% |

### Combustible Materials
| Material | Count | Percentage |
|---|---|---|
| `PMMA` | 92 | 63.4% |
| `Cotton` | 19 | 13.1% |
| `Cellulose` | 22 | 15.2% |
| `Delrin` | 5 | 3.4% |
| `Nomex` | 7 | 4.8% |

### Sample Geometry
| Geometry | Count | Percentage |
|---|---|---|
| `sheet` | 91 | 62.8% |
| `rod` | 46 | 31.7% |
| `slab` | 5 | 3.4% |
| `sphere` | 3 | 2.1% |

### Source Document Attribution (`report_id` Grouping for CV)
| NASA Report ID | Rows | Citation Link |
|---|---|---|
| `20210011385` | 96 | [https://ntrs.nasa.gov/citations/20210011385](https://ntrs.nasa.gov/citations/20210011385) |
| `20080034883` | 23 | [https://ntrs.nasa.gov/citations/20080034883](https://ntrs.nasa.gov/citations/20080034883) |
| `20040053557` | 11 | [https://ntrs.nasa.gov/citations/20040053557](https://ntrs.nasa.gov/citations/20040053557) |
| `20140011099` | 8 | [https://ntrs.nasa.gov/citations/20140011099](https://ntrs.nasa.gov/citations/20140011099) |
| `20160000593` | 5 | [https://ntrs.nasa.gov/citations/20160000593](https://ntrs.nasa.gov/citations/20160000593) |
| `19890014267` | 2 | [https://ntrs.nasa.gov/citations/19890014267](https://ntrs.nasa.gov/citations/19890014267) |

---

## 3. Numerical Feature Ranges (Operational Envelope)

| Feature | Min | Median | Max | Units | Permitted Missingness | Actual Missing |
|---|---|---|---|---|---|---|
| `oxygen_pct` | 15.0 | 19.7 | 34.0 | % vol | 0 (Strict) | 0 |
| `pressure_kpa` | 56.5 | 101.3 | 101.3 | kPa | 0 (Strict) | 0 |
| `flow_cm_s` | 0.0 | 5.0 | 45.0 | cm/s | 0 (Strict) | 0 |
| `sample_thickness_mm` | 0.08 | 0.25 | 15.00 | mm | Allowed | 0 |
| `burn_duration_s` | 5.0 | 30.0 | 210.0 | s | Allowed | 0 |
| `spread_rate_mm_s` | 0.00 | 0.15 | 2.45 | mm/s | Allowed | 0 |

---

## 4. Verification & Integrity Checks

1. **Mandatory 4-D Inputs:** All 145 records contain non-null values for `oxygen_pct`, `pressure_kpa`, `flow_cm_s`, and `material`.
2. **Duplicate Detection:** Zero duplicate `experiment_id` entries detected.
3. **Physical Plausibility:** All O2 values are within 10–40% vol; all pressures are within 40–120 kPa; all velocities are >= 0.0 cm/s.
4. **Provenance Integrity:** 100% of rows contain valid HTTPS URLs pointing to real NTRS records.
