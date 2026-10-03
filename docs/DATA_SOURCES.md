# NASA Data Sources & Physical Science Provenance (Phase 15)

> **Document Status:** Complete provenance audit of spaceflight combustion investigations and technical reports used in FLARE-X.

## 1. Flight Investigations Overview

| Investigation | Platform | Microgravity Facility | Primary Fuels | Test Records | Source Citations / DOIs |
|---|---|---|---|---|---|
| **BASS** (Burning and Suppression of Solids) | International Space Station (ISS) | Microgravity Science Glovebox (MSG) | PMMA (flat slabs & rods), Cotton fabric, Delrin rods | 78 tests | NASA/TM-2016-219077, NTRS 20160010041, NTRS 20140011099 |
| **BASS-II** (Burning and Suppression of Solids - II) | ISS | MSG Flow Duct | PMMA, Cotton, Nomex, Delrin | 35 tests | NTRS 20170006615, NASA/TM-2017-219503 |
| **DARTFire** (Diffusive and Radiative Transport in Fires) | Sounding Rockets / Drop Towers | 2.2s & 5.18s Zero-G Facilities | PMMA slabs, Cellulose paper | 18 tests | NASA/CR-2004-213123, NTRS 20040053557 |
| **Exploration Atmospheres Flammability** | Ground Hyperbaric Chambers & Drop Rigs | Variable pressure hypobaric chambers | PMMA, Nomex, Cellulose | 14 tests | NASA/TP-20210011385, NASA/TM-2008-215254 |

**Total Ingested Observations:** 145 discrete spaceflight and microgravity test rows.

---

## 2. Audited Report Corpus & Identifiers

The report corpus stored in `cache/report_corpus/*.json` contains verified metadata, abstracts, and citations extracted from NASA NTRS:

1. **`20160010041`** — *NASA/TM-2016-219077:* "Burning and Suppression of Solids (BASS) Experiment Results." (ISS, PMMA, Cotton, Delrin).
2. **`20140011099`** — *NTRS Record:* "Thickness and Fuel Preheating Effects on Material Flammability in Microgravity from the BASS Experiment."
3. **`20170006615`** — *NASA/TM-2017-219503:* "Burning and Suppression of Solids - II (BASS-II) Operational Summary."
4. **`20040053557`** — *NASA/CR-2004-213123:* "DARTFire: Diffusive and Radiative Transport in Fires in Microgravity."
5. **`20210011385`** — *NASA/TP-20210011385:* "Material Flammability in Exploration Atmospheres."
6. **`20080034883`** — *NASA/TM-2008-215254:* "Flammability Testing in Reduced Gravity and Reduced Pressure Environments."
7. **`19890014267`** — *NASA/TM-102104:* "Solid Fuel Flame Spread in Low Gravity Environments."
8. **`20000038165`** — *NASA/CR-2000-209935:* "Microgravity Combustion Studies on Thin Fabrics."
9. **`20020080920`** — *NASA/TM-2002-211559:* "Radiative Extinction Limits of Microgravity Gas and Solid Flames."
10. **`20110015542`** — *NASA/TP-2011-216145:* "Spacecraft Fire Safety: Lessons Learned from Mir and Space Shuttle."
11. **`20130010243`** — *NTRS Technical Memo:* "Extinction Boundaries for PMMA Rods in Forced Flow Microgravity."
12. **`20150002811`** — *NTRS Conference Paper:* "BASS Narrow Channel Apparatus Testing."
13. **`20180005214`** — *NASA/TM-2018-220011:* "Saffire-I Flight Experiment Flame Propagation."

---

## 3. Exclusion Rationale
To guarantee physical validity, non-solid combustion investigations were audited in Phase 02 and explicitly segregated:
- **Droplet Combustion (FLEX / FLEX-2):** Isolated spherical droplets burning in quiescent atmospheres exhibit $d^2$ evaporation law mechanics distinct from solid-fuel surface pyrolysis.
- **Gaseous Diffusion Flames (ACME, SPICE, SLICE):** Gaseous burner experiments study sooting limits and chemical kinetics rather than solid polymer flame spread.
Both are documented in `data/metadata/dataset_catalog.csv` but excluded from `cache/experiments.parquet`.
