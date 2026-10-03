# Data Schema & Harmonization Architecture (Phase 03)

> **Document Status:** Authoritative specification for data normalization, storage, and validation.

## 1. Canonical Unit System

All data entering the processed layer and modeling pipelines must strictly adhere to the following
canonical SI/engineering units:

| Dimension | Canonical Unit | Symbol | Permitted Input Units & Conversions |
|---|---|---|---|
| Oxygen Concentration | Percent by volume | `%` | Mole fraction ($X_{O2} \times 100$), volume percent |
| Pressure | Kilopascals | `kPa` | `psia` ($p \times 6.894757$), `atm` ($p \times 101.325$), `bar` ($p \times 100.0$), `torr` ($p \times 0.133322$) |
| Flow Velocity | Centimeters per second | `cm/s` | `m/s` ($v \times 100.0$), `mm/s` ($v \times 0.1$), `ft/min` ($v \times 0.508$) |
| Length / Dimensions | Millimeters | `mm` | `inches` ($d \times 25.4$), `cm` ($d \times 10.0$), `µm` ($d \times 0.001$) |
| Spread Rate | Millimeters per second | `mm/s` | `cm/s` ($r \times 10.0$), `cm/min` ($r \times 0.166667$) |
| Time / Duration | Seconds | `s` | `minutes` ($t \times 60.0$) |
| Temperature | Degrees Celsius | `°C` | `Kelvin` ($K - 273.15$), `Fahrenheit` ($(F - 32) \times 5/9$) |

All conversions must preserve the original measured value and unit in corresponding `_raw` provenance columns.

---

## 2. Core Experiment Table Schema (`cache/experiments.parquet`)

The primary training dataset consists of one row per verified microgravity combustion test condition.

| Column Name | Type | Nullable? | Description |
|---|---|---|---|
| `experiment_id` | string | No | Unique run identifier from flight log or report (e.g. `BASS2_B10_173m`) |
| `investigation` | category | No | Experiment family (e.g. `BASS`, `BASS-II`, `SAFFIRE`, `DARTFire`) |
| `material` | category | No | Normalized material name (`PMMA`, `Cotton`, `Delrin`, `Nomex`, `Cellulose`) |
| `material_raw` | string | No | Verbatim material specification (e.g. `100-µm PMMA film, 2 cm wide`) |
| `sample_geometry` | category | No | Geometry category: `sheet`, `rod`, `slab`, `sphere` |
| `sample_thickness_mm`| float | Yes | Thickness or rod diameter in mm |
| `oxygen_pct` | float | No | Ambient O2 volume percentage (15.0–30.0%) |
| `oxygen_raw` | string | Yes | Original raw text or value from table |
| `pressure_kpa` | float | No | Total chamber pressure in kPa (typically 50.0–102.0 kPa) |
| `pressure_raw` | string | Yes | Original pressure notation (e.g. `14.7 psia`, `101 kPa`) |
| `flow_cm_s` | float | No | Imposed ventilation flow velocity in cm/s (0.0–55.0 cm/s) |
| `flow_direction` | category | No | `opposed`, `concurrent`, `quiescent` |
| `outcome` | category | No | Target regime: `no_spread`, `marginal_spread`, `spread` |
| `outcome_raw` | string | No | Verbatim PI observation or table notation |
| `outcome_interpreted`| boolean | No | True if outcome required rule-based interpretation; False if stated verbatim |
| `burn_duration_s` | float | Yes | Observed burn duration in seconds |
| `spread_rate_mm_s` | float | Yes | Measured flame spread rate in mm/s (if steady spread occurred) |
| `gravity_env` | category | No | Microgravity platform: `ISS`, `drop_tower`, `sounding_rocket`, `parabolic` |
| `report_id` | string | No | NTRS accession identifier (e.g. `20210011385`, `20160000593`) |
| `source_url` | string | No | Resolvable URL (`https://ntrs.nasa.gov/citations/<id>`) |
| `source_page` | integer | Yes | Page number in cited PDF where data was published |
| `source_table` | string | Yes | Table or Figure identifier in cited publication (e.g. `Table A.1`) |
| `extraction_method` | category | No | `table_parsed`, `digitized_figure`, `text_reported` |
| `extraction_notes` | string | Yes | Notes regarding test conditions, caveats, or anomalies |

---

## 3. Provenance Schema & Integrity Guarantees

Every data point in FLARE-X is traceable through a four-link provenance chain:
1. **Raw Source Hash:** Every source document is hashed (SHA-256) upon retrieval and stored in `data/metadata/source_manifest.csv`.
2. **Document Attribution:** Every row in `cache/experiments.parquet` carries an exact `report_id`, `source_url`, and `source_page`/`source_table`.
3. **Audit Trail:** Any derived or interpreted column maintains an `_interpreted` flag and an `_raw` column holding the original text.
4. **Immutability:** Raw PDF and JSON files stored in `data/raw/` are write-protected and never overwritten by pipeline processes.

---

## 4. Missingness Policy

1. **Input Features:** For the four core inputs (`oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `material`), **no missing values are permitted**. Any test row missing one of these four mandatory parameters cannot be used for model training and is quarantined in `data/interim/quarantine.csv`.
2. **Secondary Physical Attributes:** For variables such as `sample_thickness_mm`, `burn_duration_s`, and `spread_rate_mm_s`, missingness is represented explicitly as IEEE 754 `NaN`.
3. **No Synthetic Imputation:** Missing numerical values are never synthetically imputed using mean, median, or regression imputation. If a measurement is absent from the NASA report, it is reported as absent.

---

## 5. Grouped Cross-Validation Scheme (Leakage Prevention)

To prevent data leakage during model training and evaluation:
- Multiple test points extracted from the same publication or flight series share common hardware, sensor calibrations, and test procedures.
- A standard random train/test split would leak operational correlations and artificially inflate accuracy.
- **Mandatory CV Grouping:** All cross-validation must group rows by `report_id` using `StratifiedGroupKFold`. Rows from a given report appear exclusively in the training fold or exclusively in the validation fold.
- Both grouped CV metrics (the honest headline figure) and un-grouped stratified CV metrics (optimistic baseline) are published side by side.
