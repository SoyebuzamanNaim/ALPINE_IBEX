# NASA Data Sources & Physical Science Provenance

> **Document Status:** Generated from `data/processed/experiments.csv` and `cache/report_corpus/`.
> Every NTRS identifier below was resolved against the live NASA Technical Reports Server and its
> title verified. No identifier or report designator on this page is constructed.

## 1. Flight Investigations Overview

| Investigation | Gravity Environment | Materials | Rows | Verified Source |
|---|---|---|---|---|
| **BASS-II** | ISS | Cotton-Fiberglass, Nomex, PMMA | 158 | [NTRS 20210011385](https://ntrs.nasa.gov/citations/20210011385) + [PSI-25](https://psi.nasa.gov/physci/repo/data/investigations/PSI-25) |
| **GRC Zero Gravity Facility opposed-flow extinction** | drop_tower | Cellulose | 13 | [NTRS 19890014267](https://ntrs.nasa.gov/citations/19890014267) |
| **Saffire-I** | ISS | Cotton-Fiberglass, Nomex, PMMA, Silicone | 12 | [NTRS 20170008805](https://ntrs.nasa.gov/citations/20170008805) |
| **Exploration Atmospheres flammability limits** | drop_tower | Cellulose, Mylar, Nomex, Ultem | 7 | [NTRS 20080034883](https://ntrs.nasa.gov/citations/20080034883) |
| **Saffire-III** | ISS | Cotton, Cotton-Fiberglass, PMMA | 6 | [NTRS 20210011521](https://ntrs.nasa.gov/citations/20210011521) |
| **Saffire-VI** | ISS | Cotton-Fiberglass, PMMA | 3 | [NTRS 20240002981](https://ntrs.nasa.gov/citations/20240002981) |
| **BASS** | ISS | PMMA | 1 | [NTRS 20140011099](https://ntrs.nasa.gov/citations/20140011099) |

**Total ingested observations:** 200 rows, drawn from 7 distinct NTRS reports, spanning
14.0-31.0 % oxygen and 44.1-101.3 kPa.

BASS-II conditions come from NASA PSI (PSI-25, DOI 10.60555/4qc4-de67, CC0-1.0), which publishes
the calibrated values but no outcome column; the outcomes are hand-assigned from the report's
observations per `docs/LABELING_PROTOCOL.md`. Flow direction is not in PSI and is read off the
appendix test matrices of NTRS 20210011385 (pp. 111-121). Every other row is hand transcribed
from its source table or from an exact statement in the text, with the quote kept beside it.

Two reports that used to supply rows supply none: `20040053557` is a four-page theory abstract
with no test table, and `20160000593` is a programme-overview slide deck.
Row-level provenance lives in `data/metadata/provenance_registry.json`.

> Legacy `NASA/TM-…` and `NASA/TP-…` designators previously listed here could not be verified
> and have been removed. Reports are cited by NTRS identifier, which is resolvable.

---

## 2. Audited Report Corpus & Identifiers

`cache/report_corpus/*.json` holds 13 verified NTRS records (title, abstract, URL).
Seven supply rows to the current 200-observation canonical dataset; the other six provide
supporting context and are **not** model inputs.

1. **`19890014267`** — "An experimental study of opposed flow diffusion flame extinction over a thin fuel in microgravity" ([NTRS record](https://ntrs.nasa.gov/citations/19890014267)) · _training rows_
2. **`19970020617`** — "Extinguishment of a Diffusion Flame Over a PMMA Cylinder by Depressurization in Low-Gravity" ([NTRS record](https://ntrs.nasa.gov/citations/19970020617)) · _context only_
3. **`20040053557`** — "Extinction Criteria for Opposed-Flow Flame Spread in a Microgravity Environment" ([NTRS record](https://ntrs.nasa.gov/citations/20040053557)) · _context only_ (a four-page theory abstract; it has no test table)
4. **`20080034883`** — "Microgravity Flame Spread in Exploration Atmospheres: Pressure, Oxygen, and Velocity Effects on Opposed and Concurrent Flame Spread" ([NTRS record](https://ntrs.nasa.gov/citations/20080034883)) · _training rows_
5. **`20140004923`** — "Opposed-Flow Flame Spread in a Narrow Channel Apparatus over Thin PMMA Sheets" ([NTRS record](https://ntrs.nasa.gov/citations/20140004923)) · _context only_
6. **`20140011099`** — "Thickness and Fuel Preheating Effects on Material Flammability in Microgravity from the BASS Experiment" ([NTRS record](https://ntrs.nasa.gov/citations/20140011099)) · _training rows_
7. **`20150008961`** — "Microgravity Flammability of PMMA Rods in Concurrent Flow" ([NTRS record](https://ntrs.nasa.gov/citations/20150008961)) · _context only_
8. **`20150008962`** — "Concurrent Flame Growth, Spread and Extinction over Composite Fabric Samples in Low Speed Purely Forced Flow in Microgravity" ([NTRS record](https://ntrs.nasa.gov/citations/20150008962)) · _context only_
9. **`20160000593`** — "Combustion of Solids in Microgravity: Results from the BASS-II Experiment" ([NTRS record](https://ntrs.nasa.gov/citations/20160000593)) · _context only_ (a programme-overview slide deck; it has no test table)
10. **`20160012691`** — "Correlation of Normal Gravity Mixed Convection Blowoff Limits with Microgravity Forced Flow Blowoff Limits" ([NTRS record](https://ntrs.nasa.gov/citations/20160012691)) · _context only_
11. **`20170006615`** — "Mixed Convection Blowoff Limits as a Function of Oxygen Concentration and Upward Forced Stretch Rate for Burning Pmma Rods of Various Sizes" ([NTRS record](https://ntrs.nasa.gov/citations/20170006615)) · _context only_
12. **`20200000361`** — "Solid Fuel Ignition and Extinction (SoFIE) Project on ISS" ([NTRS record](https://ntrs.nasa.gov/citations/20200000361)) · _context only_
13. **`20210011385`** — "Burning and Suppression of Solids–II  (BASS-II) Summary Report" ([NTRS record](https://ntrs.nasa.gov/citations/20210011385)) · _training rows_

---

## 2b. Audited Saffire source extract (included in the canonical dataset)

`data/processed/experiments_saffire_verified.csv` holds **21 hand-transcribed microgravity
rows** from the Saffire large-scale spacecraft fire experiments. This file remains available as
an auditable source extract; all 21 rows are also included in `cache/experiments.parquet` and in
the current model training run.

| Source | Table | Flights | Rows |
|---|---|---|---|
| [20170008805](https://ntrs.nasa.gov/citations/20170008805) | Table I "Summary of Samples, Test Conditions, and Selected Results"; cross-checked with [PSI-98](https://psi.nasa.gov/physci/repo/data/investigations/PSI-98) and [PSI-99](https://psi.nasa.gov/physci/repo/data/investigations/PSI-99) | Saffire I, II | 12 |
| [20210011521](https://ntrs.nasa.gov/citations/20210011521) | Table 1 "Saffire IV-V Sample Test Conditions"; Table 2 (thin samples) | Saffire III, IV, V | 6 |
| [20240002981](https://ntrs.nasa.gov/citations/20240002981) | Table 1 "Saffire IV-VI Sample Test Conditions" | Saffire VI | 3 |

[PSI-100](https://psi.nasa.gov/physci/repo/data/investigations/PSI-100)
also supplies a Saffire-III sample matrix. Its two condition rows are retained in
`data/external/psi/` as source data, but do not add independently labeled outcomes
to the NTRS-derived training extract. The DOI and file hashes for all three
Saffire PSI tables are recorded in [the PSI source README](../data/external/psi/README.md).

Two Saffire-II oxygen entries were corrected after comparing PSI-99 and NTRS Table I:
sample 2-8 changed from end-of-burn 22.0% to initial 22.1%, and sample 2-9
from end-of-burn 21.9% to initial 22.0%. PSI-99 conflicts with the NTRS report
on sample 2-1 oxygen and sample 2-6 flow, so those NTRS values are retained and
the discrepancies are described in the PSI source README.

**Why these were chosen.** Unlike the BASS-II appendix matrices, these reports tabulate the
test conditions explicitly (material, length, flow cm/s, flow direction, ambient pressure kPa,
oxygen mol %), so transcription does not depend on parsing prose or rotated table headers.

**Verification.** Every numeric value was checked to appear verbatim in the fulltext of the
report cited on that row. Two values are cross-report material properties and are annotated as
such in `extraction_notes` rather than presented as measurements from their own report
(`SAF_III_1` and `SAF_IV_1` thickness, taken from the SIBAL specification in 20170008805).

**Coverage in the canonical dataset.** Saffire contributes 21 flight rows at 54.1-100.0 kPa and
21.0-31.0 % oxygen, including the dataset's highest oxygen conditions. Its samples include
Cotton-Fiberglass (SIBAL), Nomex, PMMA, Silicone, and Cotton. The tabulated opposed-flow
reduced-pressure case Saffire V-4 is 72.6 kPa and 25.7 % O2. Flow is 20-25 cm/s throughout, so
these rows do not extend the canonical flow range. Outcome labels follow
`docs/LABELING_PROTOCOL.md`; 2 of 21 are marked `outcome_interpreted`.

**Not included:** the Saffire VI Nomex sample, which the report states "did not ignite" but omits
from its condition table. Its oxygen and pressure cannot be assigned from the source, so it was
left out rather than inferred.

---

## 2c. BASS-II rebuild: labelling worksheet

`data/processed/bass2_labelling_worksheet.csv` holds **249 candidate conditions from 119 of the
129 PSI tests**, built by joining the authoritative PSI conditions to the observation text of
NTRS `20210011385` on `Test #`.

**What is authoritative in this file**

- `oxygen_pct` is `Calibrated initial O2 % by vol` straight from the PSI table. Range
  **14.2 to 22.2 %**. In the current canonical table, all 158 BASS-II rows match their PSI
  test's initial oxygen value after joining on `Test #`.
- `flow_cm_s` comes from the PSI `Air display` column, which is the duct velocity in cm/s.
  Six tests checked by hand against the source reproduce exactly (`B1`, `B3`, `B14`, `B18`,
  `O4`, `P1`), on both oxygen and velocity.
- `material`, `sample_geometry` and `sample_thickness_mm` are derived from the PSI
  `Fuel Sample Material` string; `fan_display_raw` and `air_display_raw` are kept verbatim so
  every derived value can be rechecked.

**What is not filled in.** `outcome` is deliberately **blank**. Only 20 of 249 rows carry a
`suggested_outcome`, and only where the observation text names that specific velocity. The
`evidence` column states why, or says the row needs a human read. The remaining 229 rows have
observation text but no machine-checkable per-velocity evidence.

This is a deliberate stop. Four successive attempts to assign outcomes automatically each
produced demonstrably wrong labels (a velocity the test never reached marked as spreading, a
fan-pot reading recorded as a cm/s velocity, and *"flame extinguished before spreading"*
classified as spread). Outcome is the safety-critical column, and the existing defect in this
repository was caused by exactly this kind of unchecked derivation. Conditions are machine
-recoverable; outcomes are not.

**For any future labeling work:** review each `observation` against the exact test and velocity
using `docs/LABELING_PROTOCOL.md`. Keep the outcome blank when the narrative does not identify
that condition; do not merge a candidate row or retrain from a guessed mapping.

**A note on low-flow velocities.** `PSI-25_Fan_calibration_data.xlsx` does map potentiometer
settings to velocity, but pooled across its 27 calibration blocks the same pot maps to a wide
range of velocities (pot 10 spans 20 to 59 cm/s), because the mapping depends on date and flow
restrictor. The extinction points in the data sit at pot 0.35 to 0.5, below the lowest
calibrated pot of 1.0. Those velocities are therefore **not** reliably recoverable, and this
worksheet drops any number adjacent to the token `pot` rather than converting it. Earlier
revisions of this document first called them unrecoverable, then recoverable; this is the
accurate position.

---

## 2d. BASS-II relabelled dataset

`data/processed/experiments_bass2_relabelled.csv` holds **158 rows from 76 BASS-II tests**:
PSI conditions joined to NTRS `20210011385` observations, with every outcome assigned by
reading that test's observation text against `docs/LABELING_PROTOCOL.md`. Each row keeps its
`observation` and `label_source`, so any label can be re-checked against the sentence it came
from.

**Class balance: 135 `spread`, 23 `no_spread`, 0 `marginal_spread`.**

That imbalance is a property of the source, not a sampling choice, and it is the single most
important thing this rebuild revealed. In BASS-II most extinction events occur at fan-pot
settings *below* the lowest velocity recorded in cm/s. Those are precisely the rows that carry
the flammability limit, and their velocity is not recoverable (see 2c). A dataset restricted to
velocities actually stated in cm/s therefore keeps most of the "it burned" cases and loses most
of the "it went out" cases.

The previous table's tidy 75 / 49 / 21 balance came from treating those pot readings as cm/s
velocities. Remove that error and the apparent balance goes with it.

**What the negatives do still cover.** The 23 `no_spread` rows span both branches of the
flammability boundary, which is what makes them worth having:

- low-flow quenching at 2 to 5 cm/s (`B14`, `O3a`, `T20`, `T10`, `T12`, `T22`, `M19`, `O5b`)
- high-flow blowoff at 10 to 18 cm/s (`B18`, `B19`, `M11`, `M9`, `M3`)
- outright non-ignition (`F2`, `F3`, `P8`, Nomex at 8 and 15 cm/s)

### Two limitations that follow from the data

**Pressure is not identifiable.** Every BASS-II row sits at 101.3 kPa. Pressure varies only in
the 21 Saffire rows (54.1 to 100.0 kPa). Any pressure dependence the model appears to learn
comes from those 21 rows alone.

**Three feature-identical pairs carry opposite labels**, and they are real rather than
transcription errors:

| Conditions | Outcomes | Why |
|---|---|---|
| PMMA, 18.0 % O2, 3 cm/s | spread and no_spread | `O3b` burned at low flow; `O3a` "extinguished as soon as he turned flow down, probably overshot" |
| Cotton-Fiberglass, 17.1 % O2, 5 cm/s | spread and no_spread | `T11` "burned completely, steady"; `T22` "ignited at 11, turned down to 5 and extinguished" |
| PMMA, 17.3 % O2, 10 cm/s | spread and no_spread | one test blew off, the other sustained |

Near the limit the outcome depends on whether a flame was already established before the flow
was changed. `oxygen_pct`, `pressure_kpa`, `flow_cm_s` and `material` cannot express that
history, so these points set an irreducible noise floor on any model using these four features.

### Excluded

89 rows across 43 tests are excluded, each with a stated reason: an empty observation field
(about 20 tests), a velocity that is actually a potentiometer or fan-display reading, a
truncated observation, or an outcome that cannot be attributed to one velocity. `P21b` is
excluded as an igniter hardware failure rather than a flammability result.

---

## 3. Exclusion Rationale
Non-solid combustion investigations were reviewed and explicitly segregated from the solid-fuel model table:
- **Droplet Combustion (FLEX / FLEX-2):** Isolated spherical droplets burning in quiescent atmospheres exhibit $d^2$ evaporation law mechanics distinct from solid-fuel surface pyrolysis.
- **Gaseous Diffusion Flames (ACME, SPICE, SLICE):** Gaseous burner experiments study sooting limits and chemical kinetics rather than solid polymer flame spread.
Both are documented in `data/metadata/dataset_catalog.csv` but excluded from `cache/experiments.parquet`.

## 4. NASA background and public resources

These NASA resources provide discovery, research, educational, historical-safety, or
technology-transfer context. They are not row-level evidence unless a specific investigation
record is cited above, and they do not validate FLARE-X model performance. For dataset facts,
use the PSI records, NTRS reports, and row-level registry cited in Sections 1–2.

### Combustion science and research

- NASA, [PSI Data Repository: Combustion Science search](https://psi.nasa.gov/physci/repo/search?q=combustion) — discovery search for physical-sciences investigation records and released data.
- NASA Glenn Research Center, [Combustion Science](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/) — program overview of NASA combustion research and investigations.
- NASA PSI, [PSI-62: Concurrent Flame Spread Modeling using Flamelet Generated Manifolds](https://psi.nasa.gov/physci/repo/data/investigations/PSI-62) (DOI `10.60555/e9xp-ex83`) — related model-validation research using BASS/BASS-II benchmarks. PSI's current record has no experimental table; its only downloadable archive contains investigation metadata, so it is context rather than new row-level training data.
- NASA, [A Researcher's Guide to International Space Station Combustion Science](https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/) (2015) — review of ISS combustion investigations and research opportunities.
- NASA ScienceCasts, [The Power of Studying Combustion on the ISS](https://www.youtube.com/watch?v=W1oXykoz9zg) (2018; 3 min 36 sec) — educational introduction to ISS combustion research.

### Historical safety references

- NASA Safety and Mission Assurance, [Apollo 1](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1) — mission, pre-launch fire, investigation, and lessons learned.
- NASA Safety and Mission Assurance, [Apollo 13](https://sma.nasa.gov/sma-disciplines/accllp/apollo-13) — mission, oxygen-tank failure, investigation, and lessons learned.
- NASA History, [25 Years Ago: Fire Aboard Space Station Mir](https://www.nasa.gov/history/25-years-ago-fire-aboard-space-station-mir/) — historical account of the 1997 Mir fire.

### Fire-safety technology transfer

- NASA Spinoff, [Fireman's Air Tanks](https://spinoff.nasa.gov/node/9582) (originally published 1976) — firefighter breathing equipment adapted from spacesuit technology.
- NASA Spinoff, [Fire Detector](https://spinoff.nasa.gov/node/9407) (originally published 1978) — shuttle fire-detection technology described as distinguishing combustion particles from dust.
- NASA Spinoff, [New Technology for the Fire Attire](https://spinoff.nasa.gov/node/9918) (originally published 1982) — firefighter protective clothing drawing on space-suit and spacecraft thermal-protection technology.
