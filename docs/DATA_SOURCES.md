# NASA Data Sources & Physical Science Provenance

> **Document Status:** Generated from `data/processed/experiments.csv` and `cache/report_corpus/`.
> Every NTRS identifier below was resolved against the live NASA Technical Reports Server and its
> title verified. No identifier or report designator on this page is constructed.

## 1. Flight Investigations Overview

| Investigation | Gravity Environment | Materials | Rows | Verified Source |
|---|---|---|---|---|
| **BASS-II** | ISS | Cotton, Nomex, PMMA | 96 | [NTRS 20210011385](https://ntrs.nasa.gov/citations/20210011385) |
| **ExplorationAtmospheres** | drop_tower | Cellulose, Nomex, PMMA | 23 | [NTRS 20080034883](https://ntrs.nasa.gov/citations/20080034883) |
| **MGLAB & GRC Drop Tower Extinction Synthesis** | drop_tower | Cellulose, PMMA | 11 | [NTRS 20040053557](https://ntrs.nasa.gov/citations/20040053557) |
| **BASS** | ISS | PMMA | 8 | [NTRS 20140011099](https://ntrs.nasa.gov/citations/20140011099) |
| **BASS** | ISS | Delrin | 5 | [NTRS 20160000593](https://ntrs.nasa.gov/citations/20160000593) |
| **NASA GRC 5.18s Drop Tower Near-Limit Study** | drop_tower | Cellulose | 2 | [NTRS 19890014267](https://ntrs.nasa.gov/citations/19890014267) |

**Total ingested observations:** 145 rows, drawn from 6 distinct NTRS reports.
Row-level provenance lives in `data/metadata/provenance_registry.json`.

> Legacy `NASA/TM-…` and `NASA/TP-…` designators previously listed here could not be verified
> and have been removed. Reports are cited by NTRS identifier, which is resolvable.

---

## 2. Audited Report Corpus & Identifiers

`cache/report_corpus/*.json` holds 13 verified NTRS records (title, abstract, URL).
Six of these supply the training rows; the rest provide supporting context and are **not**
used as model inputs.

1. **`19890014267`** — "An experimental study of opposed flow diffusion flame extinction over a thin fuel in microgravity" ([NTRS record](https://ntrs.nasa.gov/citations/19890014267)) · _training rows_
2. **`19970020617`** — "Extinguishment of a Diffusion Flame Over a PMMA Cylinder by Depressurization in Low-Gravity" ([NTRS record](https://ntrs.nasa.gov/citations/19970020617)) · _context only_
3. **`20040053557`** — "Extinction Criteria for Opposed-Flow Flame Spread in a Microgravity Environment" ([NTRS record](https://ntrs.nasa.gov/citations/20040053557)) · _training rows_
4. **`20080034883`** — "Microgravity Flame Spread in Exploration Atmospheres: Pressure, Oxygen, and Velocity Effects on Opposed and Concurrent Flame Spread" ([NTRS record](https://ntrs.nasa.gov/citations/20080034883)) · _training rows_
5. **`20140004923`** — "Opposed-Flow Flame Spread in a Narrow Channel Apparatus over Thin PMMA Sheets" ([NTRS record](https://ntrs.nasa.gov/citations/20140004923)) · _context only_
6. **`20140011099`** — "Thickness and Fuel Preheating Effects on Material Flammability in Microgravity from the BASS Experiment" ([NTRS record](https://ntrs.nasa.gov/citations/20140011099)) · _training rows_
7. **`20150008961`** — "Microgravity Flammability of PMMA Rods in Concurrent Flow" ([NTRS record](https://ntrs.nasa.gov/citations/20150008961)) · _context only_
8. **`20150008962`** — "Concurrent Flame Growth, Spread and Extinction over Composite Fabric Samples in Low Speed Purely Forced Flow in Microgravity" ([NTRS record](https://ntrs.nasa.gov/citations/20150008962)) · _context only_
9. **`20160000593`** — "Combustion of Solids in Microgravity: Results from the BASS-II Experiment" ([NTRS record](https://ntrs.nasa.gov/citations/20160000593)) · _training rows_
10. **`20160012691`** — "Correlation of Normal Gravity Mixed Convection Blowoff Limits with Microgravity Forced Flow Blowoff Limits" ([NTRS record](https://ntrs.nasa.gov/citations/20160012691)) · _context only_
11. **`20170006615`** — "Mixed Convection Blowoff Limits as a Function of Oxygen Concentration and Upward Forced Stretch Rate for Burning Pmma Rods of Various Sizes" ([NTRS record](https://ntrs.nasa.gov/citations/20170006615)) · _context only_
12. **`20200000361`** — "Solid Fuel Ignition and Extinction (SoFIE) Project on ISS" ([NTRS record](https://ntrs.nasa.gov/citations/20200000361)) · _context only_
13. **`20210011385`** — "Burning and Suppression of Solids–II  (BASS-II) Summary Report" ([NTRS record](https://ntrs.nasa.gov/citations/20210011385)) · _training rows_

---

## 3. Exclusion Rationale
To guarantee physical validity, non-solid combustion investigations were audited in Phase 02 and explicitly segregated:
- **Droplet Combustion (FLEX / FLEX-2):** Isolated spherical droplets burning in quiescent atmospheres exhibit $d^2$ evaporation law mechanics distinct from solid-fuel surface pyrolysis.
- **Gaseous Diffusion Flames (ACME, SPICE, SLICE):** Gaseous burner experiments study sooting limits and chemical kinetics rather than solid polymer flame spread.
Both are documented in `data/metadata/dataset_catalog.csv` but excluded from `cache/experiments.parquet`.
