# Phase 03 Report — Data Audit & Schema

## 1. Objective
Establish a scientifically safe harmonization strategy, canonical unit system, variable crosswalk, data dictionary,
labeling protocol, and machine-readable schema for microgravity combustion data.

## 2. Key Scientific & Schema Decisions
1. **Canonical Unit System:**
   - Oxygen: Volume percent (`%`, 0–100)
   - Pressure: Kilopascals (`kPa`)
   - Ventilation flow: Centimeters per second (`cm/s`)
   - Sample dimensions: Millimeters (`mm`)
   - Flame spread rate: Millimeters per second (`mm/s`)
   - All original measured units and values are preserved in `_raw` provenance fields.
2. **Harmonization Crosswalk (`docs/VARIABLE_CROSSWALK.md`):**
   - Audited 23 variables across NASA combustion literature.
   - Classified each field as directly observed, derived, categorical mapping, unavailable, or ambiguous.
   - Strictly separated incompatible physics (droplets, gaseous burner flows, smoke detector aerosols) from solid fuel
     flame spread.
3. **Target Labeling Protocol (`docs/LABELING_PROTOCOL.md`):**
   - Established deterministic rules mapping literature observations to three regimes: `no_spread`, `marginal_spread`, `spread`.
   - Any row requiring interpretation is flagged with `outcome_interpreted: true`.
4. **Leakage Prevention Architecture:**
   - Documented grouped cross-validation policy (`StratifiedGroupKFold` grouped by `report_id`) in `docs/SCHEMA.md`.
5. **Schema Validation & Tests:**
   - Created Pydantic models in `src/schema/models.py`.
   - Verified schema constraints and unit conversions with automated tests in `tests/test_schema.py`.

## 3. Generated Artifacts
- `docs/VARIABLE_CROSSWALK.md`: Classification of all 23 candidate variables.
- `docs/SCHEMA.md`: Canonical units, provenance rules, missingness policy, and grouped CV scheme.
- `docs/DATA_DICTIONARY.md`: Field-by-field definitions for the experiment table.
- `docs/LABELING_PROTOCOL.md`: Deterministic mapping rules for flame-spread regimes.
- `data/metadata/schema.json`: Machine-readable JSON Schema (Draft-07).
- `data/metadata/unit_map.json`: Machine-readable unit conversion map with conversion factors.
- `src/schema/models.py`: Pydantic validation models and `convert_units` function.
- `tests/test_schema.py`: Automated unit tests for unit conversion and schema validation (3/3 passing).
