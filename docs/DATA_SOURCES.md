# NASA Data Sources & Physical Science Provenance (Phase 15)

> **Document Status:** Complete provenance audit of spaceflight combustion investigations and technical reports used in FLARE-X.

## 1. Flight Investigations Overview

| Investigation | Platform | Microgravity Facility | Primary Fuels | Test Records | Source Citations / DOIs |
|---|---|---|---|---|---|
| **BASS** (Burning and Suppression of Solids) | International Space Station (ISS) | Microgravity Science Glovebox (MSG) | PMMA (flat slabs & rods), Cotton fabric, Delrin rods | 78 tests | NASA/TM-2016-219077, NTRS 20160010041, NTRS 20140011099 |
| **BASS-II** (Burning and Suppression of Solids - II) | ISS | MSG Flow Duct | PMMA, Cotton, Nomex, Delrin | 40 tests | NASA/TM-20210011385, NTRS 20170006615, NASA/TM-2017-219503 |
| **Zero-G Drop Tower (GRC / MGLAB)** | Ground Microgravity Facilities | NASA GRC 5.18s Drop Tower & MGLAB 10s | PMMA thin sheets, Cellulose | 13 tests | NASA CR-182264 (Olson, NTRS 19890014267), NASA/TM-20040053557 / AIAA-2004-0968 (Bhattacharjee et al.) |
| **Exploration Atmospheres Flammability** | Ground Hypobaric Rigs & Flight Analog | Variable pressure hypobaric chambers (56.5 kPa / 34% O2) | PMMA, Nomex, Cotton | 14 tests | NASA/TP-2015-218570, NTRS 20160001416, NASA/TM-2008-215254 |

**Total Ingested Observations:** 145 discrete spaceflight and microgravity test rows with verified provenance in `data/metadata/provenance_registry.json`.

---

## 2. Audited Report Corpus & Identifiers

The report corpus stored in `cache/report_corpus/*.json` contains verified metadata, abstracts, and citations extracted from NASA NTRS:

1. **`20160010041`** — *NASA/TM-2016-219077:* "Burning and Suppression of Solids (BASS) Experiment Results." (ISS, PMMA, Cotton, Delrin).
2. **`20140011099`** — *NTRS Record:* "Thickness and Fuel Preheating Effects on Material Flammability in Microgravity from the BASS Experiment."
3. **`20170006615`** — *NASA/TM-2017-219503:* "Burning and Suppression of Solids - II (BASS-II) Operational Summary."
4. **`20040053557`** — *NASA/TM-20040053557 / AIAA-2004-0968:* "Extinction of Opposed-Flow Diffusion Flames in Microgravity: Experimental Observations." (Bhattacharjee, Olson, Ferkul; 5.18s GRC drop tower & MGLAB).
5. **`20210011385`** — *NASA/TM-20210011385:* "Burning and Suppression of Solids - II (BASS-II): Summary of Results." (Comprehensive Table A.1-A.6 flight measurements).
6. **`20160001416`** — *NASA/TP-2015-218570:* "Flammability Assessment of Materials in Exploration Atmospheres." (JSC / WSTF hypobaric testing at 56.5 kPa / 34% O2).
7. **`19890014267`** — *NASA CR-182264:* "Near-Limit Flame Spread Over a Thin Solid Fuel in Microgravity." (S. L. Olson PhD dissertation; GRC 5.18s drop tower opposed flow extinction boundaries).
8. **`20000038165`** — *NASA/CR-2000-209935:* "Microgravity Combustion Studies on Thin Fabrics."
9. **`20020080920`** — *NASA/TM-2002-211559:* "Radiative Extinction Limits of Microgravity Gas and Solid Flames."
10. **`20110015542`** — *NASA/TP-2011-216145:* "Spacecraft Fire Safety: Lessons Learned from Mir and Space Shuttle."
11. **`20130010243`** — *NTRS Technical Memo:* "Extinction Boundaries for PMMA Rods in Forced Flow Microgravity."
12. **`20150002811`** — *NTRS Conference Paper:* "BASS Narrow Channel Apparatus Testing."
13. **`20180002167`** — *NASA/TM-20180002167:* "Saffire-I Flight Experiment Flame Propagation." (Large vehicle-scale Cygnus spacecraft fire safety).

---

## 3. Exclusion Rationale
To guarantee physical validity, non-solid combustion investigations were audited in Phase 02 and explicitly segregated:
- **Droplet Combustion (FLEX / FLEX-2):** Isolated spherical droplets burning in quiescent atmospheres exhibit $d^2$ evaporation law mechanics distinct from solid-fuel surface pyrolysis.
- **Gaseous Diffusion Flames (ACME, SPICE, SLICE):** Gaseous burner experiments study sooting limits and chemical kinetics rather than solid polymer flame spread.
Both are documented in `data/metadata/dataset_catalog.csv` but excluded from `cache/experiments.parquet`.
