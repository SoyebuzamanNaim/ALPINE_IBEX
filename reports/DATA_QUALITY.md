# Data Quality & Ingestion Report (Phase 04)

> **File:** `cache/experiments.parquet` & `data/processed/experiments.parquet`
> **SHA-256:** `8063f6d900e91ab8bd9a892a4712ca12c2c1522881477a2353a55c2b06adf064`
> **Total Records:** 200
> **Status:** PASS (100% Schema Validated)

## 1. Executive Summary

The ingestion pipeline extracted, normalized, and validated **200 discrete experimental test conditions**
from peer-reviewed NASA technical reports and flight experiment summaries. Every row represents an actual physical
test conducted in microgravity (aboard the International Space Station, sounding rockets, or drop towers).

No numbers or measurements were synthetically imputed or fabricated. Every row traces directly to a published
NASA document accession and resolvable URL.

---

## 2. Dataset Distributions

### Outcome Classes (Flame-Spread Regimes)
| Regime Class | Count | Percentage |
|---|---|---|
| `spread` | 163 | 81.5% |
| `no_spread` | 35 | 17.5% |
| `marginal_spread` | 2 | 1.0% |

### Combustible Materials
| Material | Count | Percentage |
|---|---|---|
| `PMMA` | 151 | 75.5% |
| `Cotton` | 1 | 0.5% |
| `Cellulose` | 14 | 7.0% |
| `Delrin` | 0 | 0.0% |
| `Nomex` | 5 | 2.5% |

### Sample Geometry
| Geometry | Count | Percentage |
|---|---|---|
| `sheet` | 93 | 46.5% |
| `rod` | 55 | 27.5% |
| `slab` | 23 | 11.5% |
| `sphere` | 1 | 0.5% |

### Source Document Attribution (`report_id` Grouping for CV)
| NASA Report ID | Rows | Citation Link |
|---|---|---|
| `20210011385` | 158 | [https://ntrs.nasa.gov/citations/20210011385](https://ntrs.nasa.gov/citations/20210011385) |
| `19890014267` | 13 | [https://ntrs.nasa.gov/citations/19890014267](https://ntrs.nasa.gov/citations/19890014267) |
| `20170008805` | 12 | [https://ntrs.nasa.gov/citations/20170008805](https://ntrs.nasa.gov/citations/20170008805) |
| `20080034883` | 7 | [https://ntrs.nasa.gov/citations/20080034883](https://ntrs.nasa.gov/citations/20080034883) |
| `20210011521` | 6 | [https://ntrs.nasa.gov/citations/20210011521](https://ntrs.nasa.gov/citations/20210011521) |
| `20240002981` | 3 | [https://ntrs.nasa.gov/citations/20240002981](https://ntrs.nasa.gov/citations/20240002981) |
| `20140011099` | 1 | [https://ntrs.nasa.gov/citations/20140011099](https://ntrs.nasa.gov/citations/20140011099) |

---

## 3. Numerical Feature Ranges (Operational Envelope)

| Feature | Min | Median | Max | Units | Permitted Missingness | Actual Missing |
|---|---|---|---|---|---|---|
| `oxygen_pct` | 14.0 | 18.9 | 31.0 | % vol | 0 (Strict) | 0 |
| `pressure_kpa` | 44.1 | 101.3 | 101.3 | kPa | 0 (Strict) | 0 |
| `flow_cm_s` | 0.0 | 5.0 | 30.0 | cm/s | 0 (Strict) | 0 |
| `sample_thickness_mm` | 0.08 | 4.00 | 15.00 | mm | Allowed | 24 |
| `burn_duration_s` | nan | nan | nan | s | Allowed | 200 |
| `spread_rate_mm_s` | 1.90 | 3.55 | 8.70 | mm/s | Allowed | 192 |

---

## 4. Verification & Integrity Checks

1. **Mandatory 4-D Inputs:** All 200 records contain non-null values for `oxygen_pct`, `pressure_kpa`, `flow_cm_s`, and `material`.
2. **Duplicate Detection:** Zero duplicate `experiment_id` entries detected.
3. **Physical Plausibility:** All O2 values are within 10–40% vol; all pressures are within 40–120 kPa; all velocities are >= 0.0 cm/s.
4. **Provenance Integrity:** 100% of rows contain valid HTTPS URLs pointing to real NTRS records.
