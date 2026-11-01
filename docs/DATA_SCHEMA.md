# Experiment data schema

The model table is `cache/experiments.parquet`. The ingestion pipeline builds it from curated CSV source records in `data/processed/` and validates each row with `src/schema/models.py::ExperimentRecord`. There is one row per curated test observation; the table currently contains 200 rows.

| Field | Type | Nullable | Meaning |
|---|---|---:|---|
| `experiment_id` | string | no | Source test/run identifier |
| `investigation` | string/category | no | NASA investigation or study |
| `material` | category | no | Normalized material label |
| `material_raw` | string | no | Source material description |
| `sample_geometry` | category | no | Rod, sheet, slab, sphere, or related geometry |
| `sample_thickness_mm` | float | yes | Sample thickness or rod diameter, mm |
| `oxygen_pct` | float | no | Oxygen concentration, percent by volume |
| `oxygen_raw` | string | yes | Source oxygen notation |
| `pressure_kpa` | float | no | Ambient pressure, kPa |
| `pressure_raw` | string | yes | Source pressure notation |
| `flow_cm_s` | float | no | Forced flow speed, cm/s |
| `flow_direction` | category | yes | Opposed, concurrent, or quiescent when stated |
| `outcome` | category | no | `no_spread`, `marginal_spread`, or `spread` |
| `outcome_raw` | string | no | Source observation text |
| `outcome_interpreted` | boolean | no | Whether the outcome required interpretation |
| `burn_duration_s` | float | yes | Burn duration, seconds |
| `spread_rate_mm_s` | float | yes | Spread rate, mm/s |
| `gravity_env` | category | no | Test environment such as ISS or drop tower |
| `report_id` | string | no | NASA report/accession identifier |
| `source_url` | string | no | Source document URL |
| `source_page` | integer | yes | Source page when recorded |
| `source_table` | string | yes | Source table or figure when recorded |
| `exact_source_citation` | string | yes | Precise citation text |
| `verification_tier` | string | no | Evidence verification classification |
| `data_origin` | string | no | Direct, digitized, or interpreted origin |
| `extraction_method` | category | no | Extraction approach |
| `extraction_notes` | string | yes | Source-specific notes and caveats |

Core model inputs (`oxygen_pct`, `pressure_kpa`, `flow_cm_s`, and `material`) are required. Secondary measurements may be absent when the source does not report them. The canonical material set and numerical envelope are derived from the current dataset and stored in `models/model_meta.json`; they can change when the data is rebuilt.
