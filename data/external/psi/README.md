# NASA Physical Sciences Informatics (PSI) source data

Authoritative, machine-readable test matrices for the BASS and BASS-II microgravity
combustion investigations, downloaded from the NASA PSI Data Repository.

| File | Investigation | DOI | Rows |
|---|---|---|---|
| `PSI-25_Experimental_table_BASS-II.csv` | PSI-25, Burning and Suppression of Solids - II | `10.60555/4qc4-de67` | 129 |
| `PSI-25_BASS-II_Test_Matrices.xlsx` | PSI-25, same data split by principal investigator | `10.60555/4qc4-de67` | 129 across 6 sheets |
| `PSI-25_Fan_calibration_data.xlsx` | PSI-25, fan potentiometer to velocity calibration | `10.60555/4qc4-de67` | — |
| `PSI-26_Experimental_table_BASS.csv` | PSI-26, Burning and Suppression of Solids | — | — |

**License:** CC0-1.0 (public domain dedication), as stated on the PSI investigation pages.

## Provenance

Landing pages:
- <https://psi.nasa.gov/physci/repo/data/investigations/PSI-25>
- <https://psi.nasa.gov/physci/repo/data/investigations/PSI-26>

The PSI web application is client-rendered, so plain HTTP requests to the landing pages
return an empty shell. The files themselves come from the repository's own service endpoint:

```
https://psi.nasa.gov/geode-py/ws/studies/PSI-25/download?file=<filename>&version=1
```

A listing of an investigation's files is available at:

```
https://psi.nasa.gov/geode-py/ws/repo/investigations/PSI-25
```

## Why these files matter

`cache/experiments.parquet` currently carries oxygen values that do not match this source
(see the data integrity section of the root README). These files are the authoritative
replacement:

- **`Calibrated initial O2 % by vol`** and **`Calibrated final O2 % by vol`** give the
  corrected oxygen concentration per test. The PSI table spans **13.6 to 22.2 %**.
- **`Air display`** is the duct velocity in cm/s; **`Fan display`** is a potentiometer
  reading. Confusing the two corrupted the flow column in the current table.
- **`PSI-25_Fan_calibration_data.xlsx`** maps `Pot -> Fan Display -> Air Display -> Fan V
  -> U cm/s`, separately per date and per flow restrictor configuration. This is what makes
  the low-flow extinction velocities recoverable; a single global pot-to-velocity conversion
  does not exist, which is why the same pot setting appears against different velocities in
  different tests.

## What is still not in these files

None of the PSI structured files carry a **test outcome or observations column**. The
`Test observations and anomalies` column exists only in the narrative report,
NTRS `20210011385`, whose fulltext is at:

```
https://ntrs.nasa.gov/api/citations/20210011385/downloads/TM-20210011385.pdf.txt
```

So a faithful rebuild joins PSI conditions to NTRS observations on `Test #`.
