# Variable Crosswalk & Harmonization Strategy (Phase 03)

> **Document Status:** Authoritative scientific crosswalk for FLARE-X microgravity combustion datasets.

## 1. Variable Classification & Crosswalk Table

This crosswalk audits every variable encountered across the NASA Physical Sciences Informatics (PSI)
investigations and NASA Technical Reports (NTRS) and classifies each according to its observational nature
and harmonization status.

| Variable Name | Canonical Field Name | Scientific Meaning | Classification | In Core Model? | Handling & Harmonization Rule |
|---|---|---|---|---|---|
| **investigation** | `investigation` | NASA project/mission (BASS, BASS-II, SAFFIRE, etc.) | Categorical mapping | Yes (metadata) | Preserved verbatim; maps to PSI accession when available. |
| **experiment ID** | `experiment_id` | Specific test / run identifier (e.g. B1, B10, P22a) | Directly observed | Yes (metadata) | Preserved verbatim from flight logs and PI test matrices. |
| **fuel** | `fuel_raw` / `material` | Chemical description of combustible solid | Directly observed / Categorical mapping | Yes (input feature) | Raw fuel name preserved in `material_raw`; normalized to standard key in `material` (e.g. `PMMA`, `Cotton`, `Delrin`, `Nomex`, `Cellulose`). |
| **material** | `material` | Standardized combustible material name | Categorical mapping | Yes (input feature) | Restricted to materials present in training table; out-of-table materials trigger envelope refusal. |
| **oxygen** | `oxygen_pct` | Ambient oxygen concentration in test chamber (% by volume) | Directly observed | Yes (input feature) | Normalized to volume percent (% O2, 0.0–100.0). Original values/units preserved in `oxygen_raw`. |
| **pressure** | `pressure_kpa` | Total ambient chamber pressure | Directly observed | Yes (input feature) | Normalized to kilopascals (kPa). Conversions from psia (`* 6.894757`) or atm (`* 101.325`) explicitly tracked in provenance. |
| **airflow** | `flow_cm_s` | Imposed ventilation flow velocity over the fuel surface | Directly observed | Yes (input feature) | Normalized to centimeters per second (cm/s). Flow direction recorded separately in `flow_direction`. |
| **flow direction** | `flow_direction` | Relative direction of forced flow vs flame spread | Directly observed | Yes (metadata/filter) | Categorical: `opposed`, `concurrent`, or `quiescent`. |
| **geometry** | `sample_geometry` | Fuel sample physical form and dimensions | Directly observed | Yes (metadata/filter) | Form (`rod`, `sheet`, `slab`, `sphere`) + thickness/diameter in mm. Used for filtering and slice display; not in core 4-D input to prevent overfitting unless CV justifies. |
| **droplet diameter** | `droplet_diameter_mm` | Initial liquid fuel droplet diameter (FLEX) | Directly observed | **NO (Excluded)** | Droplet physics cannot be mapped to solid surface flammability. Kept in separate extension table. |
| **burner diameter** | `burner_diameter_mm` | Nozzle diameter for gaseous diffusion flames (ACME/SPICE) | Directly observed | **NO (Excluded)** | Gaseous burner geometry cannot be merged with solid fuel dimensions. |
| **suppressant** | `suppressant_type` / `suppressant_pct` | Chemical fire extinguishing agent (e.g. CO2, N2, CF3Br) | Directly observed | Metadata only | In BASS-II, N2 is an atmospheric diluent (sets O2 fraction), not an injected extinguishing agent. Recorded where tested; not an independent model slider. |
| **temperature** | `temperature_c` | Ambient or sample initial temperature | Directly observed | Metadata | Nominal ambient room temperature (~20–25 °C) on ISS MSG unless preheated; recorded in metadata. |
| **ignition** | `ignition_status` | Whether ignition source successfully initiated pyrolysis | Directly observed | Derived target component | Binary flag: True/False. Non-ignitions or immediate flame dropouts map to `no_spread`. |
| **extinction** | `extinction_observed` | Whether the flame extinguished prior to consuming the fuel | Directly observed | Derived target component | Binary flag: True/False; records extinction mechanism (blowoff, quench, radiation limit). |
| **burn duration** | `burn_duration_s` | Elapsed time from ignition to extinction or burnout | Directly observed | Derived target component | Recorded in seconds. Short duration drop tower tests (<5 s) flagged. |
| **flame length** | `flame_length_mm` | Visible or pyrometric flame extent | Directly observed | Metadata / Analysis | Direct physical measurement; varies dynamically. Kept in observation records. |
| **spread rate** | `spread_rate_mm_s` | Rate of flame front movement along solid surface | Directly observed / Derived | Analysis output | Measured in mm/s. Zero indicates extinction/no spread; positive rate indicates spread. |
| **smoke** | `smoke_obscuration_pct` | Optical obscuration from smoke particulates | Directly observed | **NO (Excluded)** | Specific to detector studies (SAME/DAFT); absent from flame-spread matrices. |
| **soot** | `soot_volume_fraction` | Soot concentration in flame zone | Directly observed / Derived | Metadata | Observed via laser attenuation or pyrometry in select tests. |
| **radiation** | `radiometer_reading_w_cm2` | Radiative heat emission from flame | Directly observed | Metadata | Measured by MSG broad-band radiometers in BASS/BASS-II. |
| **source file** | `source_file` | Specific publication or flight report PDF | Directly observed | Yes (provenance) | e.g. `TM-20210011385.pdf`, `20160000593.pdf`. |
| **source URL** | `source_url` | Resolvable web address for report citation | Directly observed | Yes (provenance) | Mandatory; resolves to `https://ntrs.nasa.gov/citations/<id>`. |

---

## 2. Classification Definitions

1. **Directly Observed:** Measurements obtained directly from sensors, video timers, or flow meters (e.g. `oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `burn_duration_s`).
2. **Derived:** Values calculated through analytical or data-reduction formulas (e.g. `spread_rate_mm_s` calculated from delta position over delta time; `in_training_range` calculated from bounding box).
3. **Categorical Mapping:** Scientific classifications mapped via documented rules (e.g. mapping textual PI observations to standard regime labels `no_spread`, `marginal_spread`, `spread`).
4. **Unavailable:** Parameters not reported in the literature for that specific run (handled via explicit NaN policies, never imputed silently).
5. **Ambiguous:** Reports where boundary conditions or units were unclear. Any ambiguous test point is excluded from model training and logged in `known_limitations`.

---

## 3. Incompatible Data Separation Policy

To preserve scientific validity, variables belonging to physically distinct combustion modes **MUST NOT** be merged:
- **Rule 1 (Droplets vs Solids):** Droplet diameter ($d_0$), droplet lifetime ($t_b$), and $d^2$-law evaporation constants from FLEX/FLEX-2 are strictly separated. They do not share rows or columns with solid fuel flame spread.
- **Rule 2 (Gas Burners vs Solid Fuel):** Fuel mass flow rate (sccm) and co-flow velocity from SPICE/SLICE/ACME are kept in separate extension tables.
- **Rule 3 (Smoke Detectors vs Flames):** Ionization voltage drops and obscuration percentages from SAME/DAFT are excluded from flammability prediction.
