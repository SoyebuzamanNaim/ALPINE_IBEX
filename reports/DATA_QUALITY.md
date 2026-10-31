# Data quality and ingestion report

> **File:** `cache/experiments.parquet` & `data/processed/experiments.parquet`
> **SHA-256:** `8063f6d900e91ab8bd9a892a4712ca12c2c1522881477a2353a55c2b06adf064`
> **Total Records:** 200
> **Source Rows:** 200
> **Schema Validated:** 200
> **Quarantined:** 0
> **Status:** PASS (all source rows validated)

## 1. Executive Summary

The ingestion pipeline extracted, normalized, and validated **200 curated experimental test conditions**
from NASA technical reports and flight experiment summaries. The table contains the source records selected for
the microgravity research dataset; it does not claim that all NASA tests or report observations are represented.

The canonical dataset is written only when every selected source record passes the `ExperimentRecord` schema.
Rejected rows and validation errors are saved to `data/interim/quarantine.json`, and any rejection aborts the
build before canonical dataset files are overwritten.

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
| `Cellulose` | 14 | 7.0% |
| `Cotton` | 1 | 0.5% |
| `Cotton-Fiberglass` | 21 | 10.5% |
| `Mylar` | 2 | 1.0% |
| `Nomex` | 5 | 2.5% |
| `PMMA` | 151 | 75.5% |
| `Silicone` | 4 | 2.0% |
| `Ultem` | 2 | 1.0% |

### Sample Geometry
| Geometry | Count | Percentage |
|---|---|---|
| `fabric_sheet` | 24 | 12.0% |
| `rod` | 55 | 27.5% |
| `sheet` | 93 | 46.5% |
| `slab` | 23 | 11.5% |
| `sphere` | 1 | 0.5% |
| `spherical_section` | 4 | 2.0% |

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

1. **Mandatory Inputs:** All 200 records contain non-null values for `oxygen_pct`, `pressure_kpa`, `flow_cm_s`, and `material`.
2. **Duplicate Detection:** Zero duplicate `experiment_id` entries detected.
3. **Schema Bounds:** Every selected record passed the explicit field constraints in `ExperimentRecord`.
4. **Provenance Fields:** Every row contains a report ID and source URL field. Schema validation checks URL format, not remote availability.
