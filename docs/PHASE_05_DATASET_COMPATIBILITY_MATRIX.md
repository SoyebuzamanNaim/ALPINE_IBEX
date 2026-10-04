# Phase 5 — Dataset Compatibility Matrix

> **Status:** ✅ COMPLETE  
> **Challenge:** Flame in Freefall (NASA Space Apps Challenge 2026)  
> **Primary Scope:** Cross-Investigation Alignment across BASS-II, FLEX, SPICE, SAFFIRE, and SAME  
> **Scientific Backbone:** One Unified Evidence Ontology + Multiple Experiment-Family Schemas + Specialized Analytical Models  
> **Discipline:** Zero-Fabrication, Dimensional Consistency, Strict Partitioning of Incompatible Physics

---

## 5.1 প্রথম Locked Decision

আমরা একটা giant flat CSV বানাব না।

Instead:
> **One unified evidence ontology + multiple experiment-family schemas + specialized analytical models.**

```
                                  FLARE-X
                                     │
                        Unified Scientific Ontology
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        ▼                            ▼                            ▼
   Solid Fire                  Droplet Fire                   Gas Flame
  BASS / SAFFIRE                   FLEX                         SPICE
        │                            │                            │
        └─────────────┬──────────────┴─────────────┬──────────────┘
                      │                            │
                      ▼                            ▼
                    Smoke                     Supporting
                     SAME                    ACME / SLICE
```

এটাই এখন official architecture assumption।

---

## 5.2 Five Primary Datasets

Phase 5-এ আমরা পাঁচটা primary family ব্যবহার করছি:
1. **FLEX** (`PSI-69`) — Droplet extinction / flammability limits.
2. **BASS-II** (`PSI-25`) — Solid-fuel combustion & low-speed extinction.
3. **SPICE** (`PSI-107`) — Co-flow gaseous diffusion flames (526 flames).
4. **SAFFIRE** (`PSI-98, 99, 100`) — Spacecraft-scale solid-fire behavior.
5. **SAME** (`PSI-102`) — Smoke aerosols & detector response.

NASA-এর official PSI pages confirm করে যে এগুলো বিভিন্ন combustion phenomena, variables এবং outputs measure করে।

---

## 5.3 Master Variable Compatibility Matrix

**Legend:**  
● = directly available / core variable  
◐ = related or conditionally available  
— = not a core verified variable  

| Variable | FLEX | BASS-II | SPICE | SAFFIRE | SAME | Compatibility Classification |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Experiment ID** | ● | ● | ● | ● | ● | Level A (Fully harmonizable) |
| **Investigation** | ● | ● | ● | ● | ● | Level A (Fully harmonizable) |
| **NASA source / DOI** | ● | ● | ● | ● | ● | Level A (Fully harmonizable) |
| **Microgravity platform** | ● | ● | ● | ● | ● | Level A (Fully harmonizable) |
| **Fuel / material identity** | ● | ● | ● | ● | ● | Level B (Semantically common, contextual) |
| **Oxygen concentration** | ● | ● | ◐ | ● | ◐ | Level A (Convertible to vol fraction) |
| **Pressure** | ● | ◐ | ◐ | ● (measured) | ◐ | Level A (Convertible to kPa) |
| **Airflow velocity** | ◐ | ● | ● | ● | ● | Level B (Magnitude harmonizable; physics differs) |
| **Airflow direction** | ◐ | ● | co-flow | ● | ◐ | Level B (Opposed vs concurrent vs coflow) |
| **Geometry** | droplet | ● | burner | ● | sample | Level B / Level D (Family-specific shapes) |
| **Sample dimension** | droplet dia | ● | burner dia | ● | metadata | Level D (Family-specific fields) |
| **Fuel flow rate** | — | — | ● | — | — | Level D (SPICE gas burner specific) |
| **Suppressant / diluent** | ● | ◐ | ◐ | — | — | Level B / Level D |
| **Ignition conditions** | ● | ● | ● | ● | pyrolysis | Level B (Electrical spark vs wire vs coil) |
| **Burn duration** | ● / derived | ◐ | ◐ | ● | ◐ | Level A (Convertible to seconds) |
| **Extinction** | ● | ● | ◐ | ◐ | — | Level B (Droplet vs surface spread vs liftoff) |
| **Flame spread** | — | ● | — | ● | — | Level C (Solid combustion only) |
| **Flame length / height** | ◐ | ◐ | ● | ● (video) | — | Level C (Linear dimension mm) |
| **Burning rate** | ● | ◐ | ◐ | ◐ | mass-loss | Level C (Droplet $K$ vs solid regression) |
| **Soot** | ● | ◐ | ● | ◐ | particulate | Level C (Related optical/mass observables) |
| **Smoke** | ◐ | ◐ | ● | ◐ | ● | Level C (SPICE smoke point $\rightarrow$ SAME aerosol) |
| **Particle size** | — | — | — | — | ● | Level D (SAME aerosol specific) |
| **Temperature** | ● | ◐ | ◐ | ● | ◐ | Level A (Convertible to Kelvin / °C) |
| **Radiation** | ● | ◐ | ● | ● | — | Level C (Broadband radiometers $W/\text{cm}^2$) |
| **$CO_2$ Concentration** | atmosphere | — | — | ● (sensor) | ◐ | Level A (Atmospheric composition) |
| **Video / images** | ● | ● | ● | ● | ◐ | Multimodal Evidence Layer |
| **Raw numerical data** | ● | ● | ● | ● | ● | Structured Numerical Layer |
| **Reports / docs** | ● | ● | ● | ● | ● | Unstructured Evidence Layer |

---

## 5.4 Important Physical Observation

The biggest overlapping variables are:
$$\text{material/fuel} + \text{oxygen} + \text{airflow} + \text{geometry} + \text{combustion outcome}$$

But those words do not automatically mean the same physical thing in every experiment:
* **FLEX airflow:** Air moving around a burning liquid fuel droplet in quiescent/slow drift.
* **BASS airflow:** Forced flow relative to a solid fuel sample inside a duct.
* **SPICE airflow:** Controlled co-flow around a gaseous jet flame.
* **SAFFIRE airflow:** Forced ventilation through a spacecraft-like cabin compartment.

*Same unit ($\text{cm/s}$ or $\text{m/s}$). Different physics.* That distinction is critical.

---

## 5.5 Four Levels of Compatibility

1. **Level A — Fully Harmonizable:** Same scientific concept and convertible units.
   - *Examples:* Oxygen concentration, pressure, time, temperature, airflow magnitude, NASA source, experiment identifier.
   - *Handling:* Common metadata fields in Tier 1.
2. **Level B — Semantically Common, Physically Contextual:** Same broad concept, but physical mechanism depends heavily on experiment family.
   - *Examples:* Fuel/material, geometry, airflow configuration, burn duration, extinction, ignition.
   - *Example:* "Extinction" in FLEX means droplet extinction ($d_{\text{ext}}$); in BASS it means flame spread arrest on a solid surface ($V_f \rightarrow 0$).
   - *Handling:* Shared ontology terms, but separate targets for modeling.
3. **Level C — Related Outcomes:** Different measurements describing related combustion phenomena.
   - *Examples:* Flame length, flame spread rate, burning rate, weight loss, smoke point, soot, particle size, radiation.
   - *Handling:* Connected in knowledge graph; never treated as equivalent numerical quantities.
4. **Level D — Family-Specific:** Phenomena exclusive to one physical combustion class.
   - *Examples:* Droplet diameter (FLEX), burner diameter & fuel flow rate (SPICE), particle diameter & aging time (SAME), ignition power (SAFFIRE), sample thickness & orientation (BASS).
   - *Handling:* Maintained as specialized family-specific extensions.

---

## 5.6 Core Ontology Design (Six Conceptual Layers)

```
                            CORE ONTOLOGY
                                  │
       ┌──────────────┬───────────┴───────────┬──────────────┐
       ▼              ▼                       ▼              ▼
[1. Identity]  [2. Environment]      [3. Combustible] [4. Intervention]
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
                [5. Outcomes]                                   [6. Evidence]
```

### Layer 1 — Identity
`experiment_id`, `investigation_id`, `experiment_family`, `NASA_PSI_id`, `NASA_DOI`, `source_file`, `source_url`.

### Layer 2 — Environment
`gravity_regime`, `oxygen_fraction`, `pressure`, `gas_composition`, `airflow_velocity`, `airflow_direction`, `flow_configuration`, `ambient_temperature`.

### Layer 3 — Combustible Object
`fuel_phase` (`SOLID`, `LIQUID`, `GAS`, `PYROLYSIS_SMOKE_SOURCE`), `fuel_name`, `material_name`, `material_family`, `fuel_composition`, `geometry_type`, `sample_length`, `sample_width`, `sample_thickness`, `droplet_diameter`, `burner_diameter`.  
*`fuel_phase` prevents FLARE-X from treating methane and PMMA as though they were options in the same flat dropdown.*

### Layer 4 — Intervention
`suppressant`, `suppressant_fraction`, `diluent`, `diluent_fraction`, `ignition_power`, `ignition_duration`, `forced_flow`.  
*Separates ambient environment from deliberate human/experimental intervention, enabling counterfactual sweeps.*

### Layer 5 — Outcomes
`ignition_status`, `combustion_status`, `extinction_status`, `extinction_time`, `burn_time`, `flame_spread_rate`, `flame_length`, `burning_rate`, `smoke_point_status`, `soot_measurement`, `particle_size`, `temperature`, `radiative_heat_flux`.  
*Maintains distinct physical observables rather than collapsing into one vague "result" column.*

### Layer 6 — Evidence & Provenance
Every observation carries: `measurement_type`, `measurement_method`, `value`, `unit`, `uncertainty`, `derived_or_measured`, `source_file`, `source_page_or_record`, `NASA_DOI`.  
*Example:* `airflow.value = 20`, `airflow.unit = "cm/s"`, `airflow.source = "NASA PSI-98"`, `airflow.doi = "10.60555/0t15-1z43"`.

---

## 5.7 Canonical Unit System & Presentation Mapping

| Dimension | Canonical Internal Unit | Presentation Unit | Transformation Formula |
| :--- | :---: | :---: | :--- |
| **Oxygen** | **fraction (0.0–1.0)** | `%` | $X_{\text{canonical}} = \text{percent} / 100.0$ |
| **Pressure** | **kPa** | $\text{kPa}$ or $\text{psia}$ | $P_{\text{canonical}} = P_{\text{psia}} \times 6.894757 = P_{\text{atm}} \times 101.325$ |
| **Airflow** | **m/s** | $\text{cm/s}$ | $u_{\text{canonical}} = u_{\text{cm/s}} / 100.0$ |
| **Temperature** | **Kelvin (K)** | $\text{°C}$ | $T_{\text{canonical}} = T_{\text{°C}} + 273.15$ |
| **Length / Size** | **meters (m)** | $\text{mm}$, $\text{cm}$, $\mu\text{m}$ | Automatically scaled in UI based on magnitude |
| **Time** | **seconds (s)** | $\text{s}$ or $\text{min}$ | $t_{\text{canonical}} = \text{seconds}$ |

---

## 5.8 Material, Geometry & Flow Taxonomies

* **Material Taxonomy:** Stores both raw and canonical names:  
  `material_raw = "100-µm PMMA film"` $\rightarrow$ `material_canonical = "polymethyl methacrylate"` $\rightarrow$ `material_family = "acrylic polymer"` $\rightarrow$ `fuel_phase = SOLID`.  
  `fuel_raw = "ethylene"` $\rightarrow$ `fuel_canonical = "ethylene"` $\rightarrow$ `material_family = "hydrocarbon gas"` $\rightarrow$ `fuel_phase = GAS`.
* **Geometry Taxonomy (`geometry_family`):** `DROPLET`, `ROD`, `SLAB`, `FILM`, `FABRIC`, `SHEET`, `JET`, `BURNER`, `SPHERE`, `OTHER`.
* **Flow Taxonomy (`flow_configuration`):** `QUIESCENT`, `CO_FLOW`, `OPPOSED`, `CONCURRENT`, `FORCED`, `SLOW_CONVECTIVE`, `UNKNOWN`.  
  *Prevents treating $20\text{ cm/s}$ opposed flow as equivalent to $20\text{ cm/s}$ concurrent flow.*
* **Combustion State Taxonomy:** `NOT_IGNITED`, `IGNITED`, `SUSTAINED`, `PARTIAL_BURN`, `EXTINGUISHED`, `BURNED_TO_COMPLETION`, `UNSTABLE`, `SMOKE_POINT_REACHED`, `UNKNOWN`. Original PI wording is preserved alongside the normalized state.

---

## 5.9 Cross-Dataset Comparison Matrix

**Legend:**  
🟢 = Strong direct comparison  
🟡 = Contextual / qualitative comparison  
🔴 = Do not merge quantitatively  

| Investigation | FLEX | BASS-II | SPICE | SAFFIRE | SAME |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **FLEX** | — | 🔴 | 🟡 | 🔴 | 🔴 |
| **BASS-II** | 🔴 | — | 🔴 | 🟢 | 🟡 |
| **SPICE** | 🟡 | 🔴 | — | 🟡 | 🟡 |
| **SAFFIRE** | 🔴 | 🟢 | 🟡 | — | 🟡 |
| **SAME** | 🔴 | 🟡 | 🟡 | 🟡 | — |

### Scientific Pairing Insights
1. **BASS-II $\leftrightarrow$ SAFFIRE (Strongest Cross-Dataset Pairing):** Both study solid combustibles in microgravity. Overlap in material, oxygen, airflow, geometry, ignition, and burn behavior. Supports cross-experiment evidence comparison (lab-scale glovebox vs. large compartment fire).
2. **FLEX $\leftrightarrow$ SPICE (Combustion Physics Pairing):** Both study flame dynamics, soot, and extinction under gas/ambient flow. Conceptually comparable in knowledge graphs; separate in predictive models.
3. **SPICE $\leftrightarrow$ SAME (Soot to Smoke Chain):** Connects gaseous flame soot inception (SPICE) to smoke aerosol particulate sizing and transport (SAME).
4. **BASS $\leftrightarrow$ SAME (Polymer Pyrolysis to Smoke):** Connects solid material combustion to toxic smoke particulate characterization.

---

## 5.10 Three Meanings of "Integration"

When we state *"FLARE-X integrates NASA datasets,"* we maintain three precise distinctions:
* **Integration A — Search Integration:** All datasets appear in one unified discovery system. (✅ **100% Implemented**)
* **Integration B — Semantic Integration:** Datasets share a common ontology of fuel, atmosphere, flow, and extinction. (✅ **100% Implemented**)
* **Integration C — Statistical Pooling:** Rows from multiple datasets merged into a single training set. (❌ **Rejected** except where scientifically identical).

---

## 5.11 Scientific Similarity & Relevance Ranking Formulation

When a user submits a query (e.g. solid PMMA at 18% $O_2$, $15\text{ cm/s}$ flow), candidate experiments are scored via a **Physically Weighted Similarity Metric**:

$$\text{Similarity}(q, e) = \Big[ w_1 \cdot \text{Sim}_{\text{mat}} + w_2 \cdot \text{Sim}_{O_2} + w_3 \cdot \text{Sim}_{\text{flow}} + w_4 \cdot \text{Sim}_{\text{geom}} + w_5 \cdot \text{Sim}_{\text{dir}} + w_6 \cdot \text{Sim}_{\text{scale}} \Big] \times \text{Penalty}_{\text{family}}$$

* **Family Compatibility Penalty ($\text{Penalty}_{\text{family}}$):** If the requested question involves solid polymer flame spread, an SPICE gas-flame test with identical airflow receives a steep compatibility penalty ($\approx 0.1$), ensuring BASS-II and SAFFIRE tests rank highest.

---

## 5.12 Missingness vs. Non-Applicability

A SPICE gaseous flame test does not have a `sample_thickness_mm`. That is not a "missing data error"—the physical concept simply does not apply.  
FLARE-X explicitly tracks:
* `VALUE`: Measured and present.
* `NOT_APPLICABLE`: Parameter does not exist for this combustion family.
* `NOT_REPORTED`: Parameter applies but was omitted in the source paper.
* `UNKNOWN`: Status unverified.

---

## 5.13 Hybrid Storage Architecture

* **Structured Store (PostgreSQL / Parquet):** Experimental metadata, numerical measurements, canonical units, regime labels.
* **Vector Store:** NASA reports, NTRS technical papers, PI narrative notes, PSI descriptions.
* **Object Store:** Raw `.mp4` video files, TIFF/JPEG calibrated images, time-series sensor files.
* **Graph Layer:** Semantic relations connecting Materials $\rightarrow$ Investigations $\rightarrow$ Regimes $\rightarrow$ Sources.

---

## 5.14 Hybrid Evidence Retrieval Workflow

```
USER QUESTION / SCENARIO
          │
          ├───────────────────────────────┐
          ▼                               ▼
   SEMANTIC RETRIEVER            STRUCTURED FILTER
  (NTRS PDF abstracts,          (Oxygen, flow, pressure,
   scientific papers)            material, geometry)
          │                               │
          └───────────────┬───────────────┘
                          ▼
                 SCIENTIFIC RERANKER
             • Multidimensional similarity
             • Family compatibility weighting
             • Provenance verification
                          │
                          ▼
                RANKED NASA EVIDENCE
```

---

## 5.15 Video 1 Script Lock: The Harmonization Strategy

For the October 7 prescreening video, we explain our architecture with technical authority:

> *"Because NASA's combustion investigations span fundamentally different physical systems, we will not force them into one universal model. FLARE-X harmonizes shared metadata such as oxygen, flow, pressure, material, geometry, and outcomes while preserving experiment-specific variables. Specialized analytical models operate within compatible experiment families, while a unified evidence layer connects their findings for search, comparison, and interpretation."*

---

## 5.16 Phase 5 Acceptance Gate

- [x] **Master Compatibility Matrix Created:** 14-dimension analysis across BASS-II, FLEX, SPICE, SAFFIRE, and SAME.
- [x] **Four Compatibility Levels Defined:** Level A (Harmonizable), Level B (Contextual), Level C (Related Outcomes), Level D (Family-Specific).
- [x] **Six-Layer Core Ontology Established:** Identity, Environment, Combustible, Intervention, Outcomes, Evidence.
- [x] **Canonical Units & Conversions Locked:** Internal SI standard with user-friendly UI presentation.
- [x] **Domain Taxonomies Built:** Fuel phase, material canonicalization, geometry families, and flow configurations.
- [x] **Dataset-to-Dataset Pairings Audited:** BASS-II $\leftrightarrow$ SAFFIRE confirmed as strongest pair; SPICE $\leftrightarrow$ SAME confirmed as soot/smoke bridge.
- [x] **Scientific Similarity & Family Penalty Formulated:** Mathematical ranking prevents gas flames from polluting solid fuel searches.
- [x] **Hybrid Storage Architecture Defined:** Structured tables, vector store, object store, and graph layer.

---

## ✅ Phase 5 Status: COMPLETE

The harmonization schema and compatibility boundaries are fully specified and locked.

We now proceed to **Phase 6: Scientific Questions & ML Targets**.
