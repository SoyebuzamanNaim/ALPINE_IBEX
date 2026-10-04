# Phase 4 — NASA Dataset Deep Audit: Flame in Freefall

> **Status:** ✅ COMPLETE  
> **Challenge:** Flame in Freefall (NASA Space Apps Challenge 2026)  
> **Primary Repository:** NASA Physical Sciences Informatics (PSI) & NASA Technical Reports Server (NTRS)  
> **Scientific Mandate:** Federated Scientific Intelligence over Heterogeneous Combustion Families  
> **Discipline:** Zero-Fabrication, NASA-Only Provenance, Strict Physical Boundary Segregation

---

## 4.1 Executive Summary & Core Scientific Conclusion

Phase 4 locks the most critical scientific foundation of FLARE-X:

1. **NASA-Only Data is Completely Viable:** It is 100% possible to construct the core FLARE-X system exclusively from authentic NASA experimental data. We are not reliant solely on unstructured report text or naive RAG. NASA Physical Sciences Informatics (PSI) hosts raw experimental data, analyzed data, structured test matrices, imagery, high-speed video, engineering/science documents, and peer-reviewed flight publications. PSI is explicitly open to the public and designed for secondary analysis, data mining, and AI/ML.
2. **The Incompatibility Trap:** Merging all NASA combustion datasets into one universal machine learning model is scientifically invalid. 
   - **FLEX** measures liquid droplet extinction via $d^2$ vaporization physics.
   - **BASS / BASS-II** measures solid polymer flame spread and low-flow extinction.
   - **SPICE** measures gaseous co-flow diffusion flame length and smoke points.
   - **SAME** measures smoke particulate sizing and detector chamber responses.
   - **SAFFIRE** measures realistic spacecraft-scale fires inside Cygnus cargo modules.
   *They are scientific cousins, not identical twins.*
3. **The Architectural Mandate:** FLARE-X must be built as a **federated scientific intelligence system** over distinct combustion experiment families, supported by an intelligent Model Router, rather than a single collapsed classifier.

---

## 4.2 Authoritative NASA Data Sources & Open Access Licensing

Our primary data repository is the **NASA Physical Sciences Informatics (PSI)** system:
- **URL:** [https://psi.nasa.gov](https://psi.nasa.gov)
- **Scope:** Complete combustion investigations cataloging FLEX, FLEX-2, BASS, BASS-II, SAFFIRE I–III, SAME/SAME-R, SLICE, SPICE, ACME BRE, ACME s-Flame, CFI, and CFI-G.
- **Data Layers Available:** Raw data, analyzed data, calibrated imagery, experiment design matrices, engineering telemetry, analytical models, technical reports, and peer-reviewed publications.
- **Licensing & Provenance:** Key PSI datasets carry formal Digital Object Identifiers (DOIs) and explicit open licenses. FLEX, BASS-II, SPICE, SAFFIRE-I, and SAME are released under **Creative Commons Zero (CC0-1.0)** public domain dedication, guaranteeing complete compliance for open-access research.

---

## 4.3 Dataset Priority Matrix After Deep Audit

| Dataset | NASA ID / DOI | FLARE-X Role | Data Confidence | Priority | Scientific Rationale |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **BASS-II** | `PSI-25`<br>`10.60555/4qc4-de67` | Solid-material flame spread / extinction | **Very High** | **A+** | Primary dataset for solid fuel fire safety; 694 files, raw `.mp4` video, granular low-flow extinction tests. |
| **FLEX** | `PSI-69`<br>`10.60555/mbq8-0451` | Droplet extinction / flammability limits | **Very High** | **A+** | Rigorous parametric sweeps of $O_2$, pressure, and suppressants; clean extinction boundary mapping. |
| **SPICE** | `PSI-107`<br>`10.60555/9kbh-e962` | Flame length / smoke point / soot | **Very High** | **A+** | **526 flames studied**; 6.47 GB release; exceptionally clean numerical data for statistical ML regression. |
| **SAFFIRE I–III** | `PSI-98, 99, 100`<br>`10.60555/0t15-1z43` | Realistic spacecraft-scale fire evidence | **Very High** | **A+** | Real-scale fire validation aboard Cygnus; rich sensor arrays (thermocouples, radiometers, $O_2/CO_2$). |
| **SAME** | `PSI-102`<br>`10.60555/gd4k-8h62` | Smoke particles & detector behavior | **Very High** | **A** | Connects combustion mass loss to smoke aerosol size distribution and spacecraft detector response. |
| **ACME BRE** | `PSI-20` | Material flammability surrogate physics | **High** | **A-** | 59 burner tests simulating condensed-phase burning under microgravity; evaluates radiative feedback. |
| **SLICE** | `PSI-106` | Flame lift / stability / soot | **High** | **B+** | Co-flow laminar methane/air flames; liftoff velocities and radical concentrations. |
| **FLEX-2** | `PSI-68` | Complex droplet / bi-component fuel | **High** | **B+** | Practical fuel generalization layer for droplet extinction science. |
| **ACME s-Flame** | `PSI-23` | Spherical diffusion extinction dynamics | **High** | **B** | Spherical gas flames; transport properties and radiative vs. convective extinction. |
| **BASS (Original)**| `PSI-26` | Earlier solid-combustion evidence | **High** | **B** | Thin/thick solids, acrylic spheres, and fuel preheating tests; supplementary to BASS-II. |
| **SAME-R** | `PSI-101` | Smoke extension / reflight | **High** | **B** | Extended operating conditions and diagnostic modifications for aerosol sizing. |
| **CFI / CFI-G** | `PSI-39, 159` | Cool-flame transitions | **Medium/High** | **Stretch** | Low-temperature oxidation chemistry; fascinating science, secondary to core fire safety. |
| **DAFT / DAFT-2** | `PSI-47` | Dust / aerosol sensor feasibility | **Medium/High** | **Stretch** | P-Trak condensation nuclei counter verification; supplementary to SAME. |
| **SoFIE** | Ground / ISS | Solid fuel ignition and extinction | *Unverified* | **Monitor** | Newer investigation; public release status in PSI under active monitoring. |

---

## 4.4 Detailed Investigation Audits

### 1. FLEX — Flame Extinguishment Experiment
* **Identifier & DOI:** `PSI-69` | `10.60555/mbq8-0451` | CC0-1.0
* **Scientific Purpose:** Determines when liquid fuel droplets continue burning versus extinguish in microgravity. Mapped flammability limits and gaseous suppressants ($CO_2$, $He$, $SF_6$, $N_2$) across varying pressures ($0.5\text{ to }1.5\text{ atm}$) and oxygen concentrations ($12\%\text{ to }40\%\text{ O}_2$).
* **Verified Variables:** Fuel type (heptane, methanol), initial droplet diameter ($d_0 \approx 1.5\text{–}4.0\text{ mm}$), ambient $O_2$, pressure, diluent gas fraction, burning rate constant ($K$), extinction diameter ($d_{\text{ext}}$), soot volume fraction, radiometer emissions.
* **FLARE-X Role:** Clean quantitative ML classification (sustained combustion vs. extinction boundary) and regression (burning rate).
* **Physical Boundary:** Governed by $d^2$-law droplet evaporation. **Cannot be merged with solid fuel flame spread.**

### 2. BASS-II — Burning and Suppression of Solids II
* **Identifier & DOI:** `PSI-25` | `10.60555/4qc4-de67` | CC0-1.0
* **Data Release:** 694 files, including raw `.mp4` video files, tabular logs, and engineering reports.
* **Scientific Purpose:** Investigates ignition, flame growth, flame spread rate, and low-speed extinction limits for solid fuels in low-velocity forced flows ($0\text{ to }53\text{ cm/s}$) aboard the ISS MSG.
* **Specimens Tested:** Flat PMMA sheets/films ($100\text{–}200\ \mu\text{m}$), cylindrical PMMA rods ($1\text{–}10\text{ mm}$), cotton fabric blends, Nomex, Delrin.
* **FLARE-X Role:** **Primary training and validation dataset for solid-material fire safety.** Supports regime classification (`no_spread`, `marginal_spread`, `spread`), spread rate regression, and multimodal flame video segmentation.

### 3. SPICE — Smoke Point in Co-flow Experiment
* **Identifier & DOI:** `PSI-107` | `10.60555/9kbh-e962` | CC0-1.0 | 6.47 GB
* **Sample Size:** **526 discrete flames studied.**
* **Scientific Purpose:** Evaluates soot inception, smoke points, and flame length in laminar co-flow diffusion flames aboard the ISS.
* **Verified Variables:** Fuels (methane, ethylene, propane, propylene mixtures), burner diameters ($0.41, 0.76, 1.6\text{ mm}$), co-flow velocities ($5.4\text{ to }65\text{ cm/s}$), fuel volume flow rate ($sccm$), flame length ($mm$), radiative loss.
* **FLARE-X Role:** **Cleanest high-volume numerical modeling dataset.** Highly suitable for multi-variable regression (flame length) and classification (smoke point regime).

### 4. SAFFIRE Family (Spacecraft Fire Safety Experiments I, II, III)
* **Identifier & DOI:** `PSI-98` (SAFFIRE-I, `10.60555/0t15-1z43`), `PSI-99`, `PSI-100` | CC0-1.0
* **Unique Value:** Realistically large fire experiments inside an uncrewed Cygnus spacecraft.
* **Conditions & Instrumentation:**
  - SAFFIRE-I: SIBAL fabric ($40 \times 100\text{ cm}$) at $20\text{ cm/s}$ flow, $21.5\%\text{ O}_2$; thermocouple arrays, radiometers, pressure, $O_2/CO_2$ sensors, 2 cameras.
  - SAFFIRE-II: 9 material samples ($5 \times 29\text{ cm}$) testing silicone composites, SIBAL, PMMA, and Nomex at $20\text{–}25\text{ cm/s}$ flow and $22.1\%\text{ O}_2$.
  - SAFFIRE-III: Large SIBAL sample at elevated airflow ($30\text{ cm/s}$); produced 4,922 calibrated images and $>50\text{ GB}$ of telemetry.
* **FLARE-X Role:** **Mission Reality & Validation Layer.** SAFFIRE is statistically small ($n \approx 1\text{ to }9$ burns per flight), so it is not used for standalone ML training. Instead, it provides large-scale spacecraft validation, temporal curve comparison, and high-impact demonstration evidence.

### 5. SAME / SAME-R — Smoke Aerosol Measurement Experiment
* **Identifier & DOI:** `PSI-102` (`10.60555/gd4k-8h62`), `PSI-101` | CC0-1.0 | 627.14 MB
* **Scientific Purpose:** Measures smoke particulate morphology, particle size distribution, and detector response for overheated spacecraft materials (Teflon, Kapton, cellulose, silicone) in microgravity.
* **FLARE-X Role:** **Smoke Intelligence Module.** Bridges material pyrolysis to detector obscuration and aerosol aging, allowing FLARE-X to address fire detection alongside fire propagation.

### 6. Supporting Investigations (BRE, SLICE, s-Flame)
* **ACME BRE (PSI-20):** 59 burn tests simulating condensed-phase burning using porous gas burners. Connects gaseous burner kinetics to solid flammability surrogates.
* **SLICE (PSI-106):** Liftoff velocities and soot behavior in microgravity co-flow flames.
* **ACME s-Flame (PSI-23):** Spherical diffusion flame extinction dynamics and radiative loss limits.

---

## 4.5 The Extracted Empirical Baseline (`cache/experiments.parquet`)

The tabular training core currently ingested in FLARE-X contains **145 discrete verified spaceflight and ground-microgravity test conditions** extracted from 13 NTRS reports:
* **Materials (5):** PMMA (92 tests, 63.4%), Cellulose (22 tests, 15.2%), Cotton fabric (19 tests, 13.1%), Nomex (7 tests, 4.8%), Delrin (5 tests, 3.4%).
* **Regimes (3):** `spread` (75 tests, 51.7%), `no_spread` (49 tests, 33.8%), `marginal_spread` (21 tests, 14.5%).
* **4-D Bounding Box:** Oxygen ($15.0\%\text{ to }34.0\%$), Pressure ($56.5\text{ to }101.3\text{ kPa}$), Flow ($0.0\text{ to }45.0\text{ cm/s}$).
* **Model Baseline Performance:** Gradient Boosting classifier achieves **79.31% CV accuracy** grouped by `report_id` (against a majority baseline of 51.72%).

---

## 4.6 Strict Incompatible Data Separation Policy

To preserve scientific rigor, the following row-concatenations are **strictly prohibited**:
1. ❌ **No Droplet-Solid Merging:** Liquid droplet diameter ($d_0$) and $d^2$ vaporization rates (FLEX) must never be placed in the same training matrix as solid fuel thickness and spread rates (BASS).
2. ❌ **No Gas Burner-Solid Merging:** Fuel mass flow rates ($sccm$) and co-flow velocities (SPICE/SLICE) must never be merged with solid fuel flammability.
3. ❌ **No Sensor Obscuration-Flame Spread Merging:** Particulate count concentrations (SAME) must not be treated as flame spread outcomes.
4. ❌ **Frames $\ne$ Experiments:** High-frequency video frames (e.g. 4,922 images in SAFFIRE-III) represent a single experimental condition. Grouping and validation splits must occur at the independent test condition level to prevent massive data leakage.

```
                         FEDERATED DATA ARCHITECTURE
                                      │
        ┌───────────────┬─────────────┼─────────────┬───────────────┐
        ▼               ▼             ▼             ▼               ▼
   BASS / BASS-II     FLEX          SPICE        SAFFIRE          SAME
   Solid Flammability Droplet Ext.  Gas Burners  Mission Context  Smoke Particles
   (Core Classifier) (Boundaries)  (High-N ML)   (Validation)     (Detection)
```

---

## 4.7 Video 1 Script Lock: Verified Dataset Claims

For the October 7 prescreening pitch, we can state with 100% scientific defensibility:

> *"We have identified NASA Physical Sciences Informatics datasets spanning multiple scales of microgravity combustion: FLEX for droplet extinction, BASS-II for solid-material flame spread, SPICE with 526 gaseous flames for smoke-point and flame-behavior analysis, SAFFIRE for spacecraft-scale fire experiments, and SAME for smoke-particle and detector behavior. Together, these datasets provide numerical measurements, experimental metadata, imagery, video, and scientific documentation that support both quantitative modelling and evidence-grounded AI."*

---

## 4.8 Phase 4 Acceptance Gate

- [x] **Authoritative Repository Confirmed:** NASA PSI verified as primary open-access source with CC0 licenses and DOIs.
- [x] **23 Investigations Audited & Prioritized:** BASS-II, FLEX, SPICE, SAFFIRE, and SAME established as the core five.
- [x] **SPICE ML Volume Verified:** 526 quantitative flame experiments confirmed for statistical modeling.
- [x] **BASS-II Multimodal Grounding Verified:** 694 files, raw `.mp4` video, and detailed low-speed extinction test groups verified.
- [x] **SAFFIRE Mission Role Defined:** Positioned as large-scale contextual validation, not an oversized supervised dataset.
- [x] **Incompatible Separation Policy Locked:** Strict boundary preventing droplet, gas burner, and solid fuel dataset collisions.
- [x] **Prescreening Claims Locked:** Accurate, non-fabricated script text established for the October 7 submission.

---

## ✅ Phase 4 Status: COMPLETE

The dataset audit is finalized and verified against NASA archives.

We are now ready for **Phase 5: Dataset Compatibility Matrix & Harmonization Schema**.
