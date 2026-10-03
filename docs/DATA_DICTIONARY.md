# Data Dictionary — Microgravity Combustion Dataset (Phase 03)

> **Dataset:** `cache/experiments.parquet` and `data/processed/experiments.csv`
> **Author:** FLARE-X Autonomous Data Engineering Team
> **Target:** Microgravity Solid Fuel Flammability & Flame Spread

| Column Name | Type | Canonical Unit | Valid Range / Categories | Description | Example Value |
|---|---|---|---|---|---|
| `experiment_id` | String | — | Unique alphanumeric | Unique run identifier assigned from flight log or report | `"BASS2_B1_147"` |
| `investigation` | Categorical | — | `BASS`, `BASS-II`, `SAFFIRE`, `DARTFire`, `SIBAL` | NASA combustion investigation name | `"BASS-II"` |
| `material` | Categorical | — | `PMMA`, `Cotton`, `Delrin`, `Nomex`, `Cellulose` | Standardized combustible material designation | `"PMMA"` |
| `material_raw` | String | — | — | Exact description of material from cited paper | `"100-µm PMMA film, 2 cm wide"` |
| `sample_geometry` | Categorical | — | `sheet`, `rod`, `slab`, `sphere` | Physical sample geometry form | `"sheet"` |
| `sample_thickness_mm` | Float | mm | `0.05` to `25.0` | Fuel sample thickness (sheet/slab) or rod diameter | `0.1` |
| `oxygen_pct` | Float | % vol | `14.0` to `35.0` | Ambient oxygen concentration in chamber (% by volume) | `21.0` |
| `oxygen_raw` | String | — | — | Verbatim O2 measurement from publication | `"21.0 vol%"` |
| `pressure_kpa` | Float | kPa | `40.0` to `110.0` | Total ambient chamber pressure | `101.3` |
| `pressure_raw` | String | — | — | Verbatim pressure measurement from publication | `"101.3 kPa (1 atm)"` |
| `flow_cm_s` | Float | cm/s | `0.0` to `60.0` | Imposed ventilation flow velocity over the fuel | `5.0` |
| `flow_direction` | Categorical | — | `opposed`, `concurrent`, `quiescent` | Flow direction relative to flame propagation front | `"opposed"` |
| `outcome` | Categorical | — | `no_spread`, `marginal_spread`, `spread` | Target flame-spread regime classification | `"spread"` |
| `outcome_raw` | String | — | — | Verbatim observation from PI notes or report table | `"Steady spread at 5 cm/s"` |
| `outcome_interpreted` | Boolean | — | `True`, `False` | Whether target was mapped using the labeling protocol | `False` |
| `burn_duration_s` | Float | s | `> 0.0` | Observed duration of flame burning | `26.0` |
| `spread_rate_mm_s` | Float | mm/s | `>= 0.0` | Measured flame front velocity along solid fuel | `0.85` |
| `gravity_env` | Categorical | — | `ISS`, `drop_tower`, `sounding_rocket`, `parabolic` | Microgravity test platform | `"ISS"` |
| `report_id` | String | — | NASA Accession string | NTRS document identifier | `"20210011385"` |
| `source_url` | String | — | Valid HTTPS URL | Resolvable citation link | `"https://ntrs.nasa.gov/citations/20210011385"` |
| `source_page` | Integer | — | `> 0` | Page number in publication containing data | `103` |
| `source_table` | String | — | — | Table or figure reference in publication | `"Table A.1"` |
| `extraction_method` | Categorical | — | `table_parsed`, `digitized_figure`, `text_reported` | Method used to extract numerical data | `"table_parsed"` |
| `extraction_notes` | String | — | — | Narrative remarks, sensor details, or boundary conditions | `"Fan flow turned down to locate extinction"` |
