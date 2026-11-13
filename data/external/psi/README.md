# NASA Physical Sciences Informatics (PSI) source data

Machine-readable test matrices for the BASS, BASS-II, and Saffire microgravity
combustion investigations, downloaded from the NASA PSI Data Repository. The NTRS
reports remain the outcome-label source for the canonical training table.

| File | Investigation | DOI | Rows |
|---|---|---|---|
| `PSI-25_Experimental_table_BASS-II.csv` | PSI-25, Burning and Suppression of Solids - II | `10.60555/4qc4-de67` | 129 |
| `PSI-25_BASS-II_Test_Matrices.xlsx` | PSI-25, same data split by principal investigator | `10.60555/4qc4-de67` | 129 across 6 sheets |
| `PSI-25_Fan_calibration_data.xlsx` | PSI-25, fan potentiometer to velocity calibration | `10.60555/4qc4-de67` | — |
| `PSI-26_Experimental_table_BASS.csv` | PSI-26, Burning and Suppression of Solids | `10.60555/58h4-dy80` | 122 |
| `PSI-98_Experimental_table_SAFFIRE-1.csv` | PSI-98, Saffire-I | `10.60555/0t15-1z43` | 2 samples, 2 camera-reference rows |
| `PSI-99_Experimental_table_SAFFIRE-2.csv` | PSI-99, Saffire-II | `10.60555/2chp-m469` | 9 samples, 6 note/reference rows |
| `PSI-100_Experimental_table_SAFFIRE-3.csv` | PSI-100, Saffire-III | `10.60555/040q-4h36` | 2 sample conditions |

**License:** CC0-1.0 (public domain dedication), as stated on the PSI investigation pages.

## Live source check (2026-11-13)

NASA's PSI-25 landing page identifies the current investigation release as **Version 4**
(updated 2025-11-24; DOI `10.60555/4qc4-de67`). The current source CSV is named
`PSI-25_Experimental table_BASS-II.csv` on NASA's service; this repository stores the same
file as `PSI-25_Experimental_table_BASS-II.csv` (underscore in place of the filename space).
The NASA download endpoint returned **16,590 bytes** with SHA-256
`71e792bf6b5fb5ea620c5dd70fbbac05515992e12aefcf5dff47312caa48c042`, byte-identical to the
checked-in copy.

The investigation's Version 4 is the release of the PSI record; the endpoint's `version=1`
parameter identifies the downloaded file revision. Those version numbers refer to different
things.

The PSI-98, PSI-99, and PSI-100 experimental CSVs were also fetched from the same NASA
service on 2026-11-13, with `version=1` and the investigation-specific source filename:

| File | Bytes | SHA-256 |
|---|---:|---|
| `PSI-98_Experimental_table_SAFFIRE-1.csv` | 469 | `c01f29c62455f0a3b512290ab85e5687ecded326733189f002f580368402308d` |
| `PSI-99_Experimental_table_SAFFIRE-2.csv` | 1,973 | `3c24390b9ef86f3d1ebaab911a1a3cc95a8759aebf42062371370e6d4b31b8ac` |
| `PSI-100_Experimental_table_SAFFIRE-3.csv` | 239 | `4d3c717ec20dd0247db670b2784a9fd7d746788bc54a936f80693e48eb8cd117` |

## Provenance

Landing pages:
- <https://psi.nasa.gov/physci/repo/data/investigations/PSI-25>
- <https://psi.nasa.gov/physci/repo/data/investigations/PSI-26>
- <https://psi.nasa.gov/physci/repo/data/investigations/PSI-98>
- <https://psi.nasa.gov/physci/repo/data/investigations/PSI-99>
- <https://psi.nasa.gov/physci/repo/data/investigations/PSI-100>

The PSI web application is client-rendered, so the landing page is not the file download. The
CSV was fetched from NASA's repository service endpoint (URL-encoded filename shown):

```
https://psi.nasa.gov/geode-py/ws/studies/PSI-25/download?file=PSI-25_Experimental%20table_BASS-II.csv&version=1
```

For the Saffire files, substitute `PSI-98`, `PSI-99`, or `PSI-100` in the study path and
the corresponding NASA source filename (for example,
`PSI-99_Experimental%20table_SAFFIRE-2.csv`). Local filenames replace the single space
after `Experimental` with an underscore.

A listing of an investigation's files is available at:

```
https://psi.nasa.gov/geode-py/ws/repo/investigations/PSI-25
```

## Why these files matter

These files are the authoritative source for the BASS-II test conditions. In the current
canonical table, the **158 retained BASS-II rows from 76 tests match PSI-25's calibrated initial
oxygen values on `Test #` (158/158)**. The canonical table was rebuilt and verified against this
source on 2026-11-13:

- **`Calibrated initial O2 % by vol`** and **`Calibrated final O2 % by vol`** give the
  corrected oxygen concentration per test. The PSI table spans **13.6 to 22.2 %**.
- **`Air display`** is the duct velocity in cm/s; **`Fan display`** is a potentiometer
  reading. They are different quantities and must not be interchanged. NASA's separate fan
  calibration files are configuration-specific; do not infer unreported low velocities from a
  single global potentiometer conversion.
- **`PSI-25_Fan_calibration_data.xlsx`** maps `Pot -> Fan Display -> Air Display -> Fan V
  -> U cm/s`, separately per date and per flow restrictor configuration. A single global
  pot-to-velocity conversion does not exist: the same pot setting appears against different
  velocities in different tests. Extinction settings below the measured calibration range
  remain unquantified in cm/s.

## What is still not in these files

The BASS and BASS-II PSI tables have no **test outcome or observations column**. The
`Test observations and anomalies` column exists only in the narrative report,
NTRS `20210011385`, whose fulltext is at:

```
https://ntrs.nasa.gov/api/citations/20210011385/downloads/TM-20210011385.pdf.txt
```

So a faithful rebuild joins PSI conditions to NTRS observations on `Test #`.

The Saffire PSI tables do contain burn measurements, but they do not add independent
labeled experiments to the 21 Saffire records already transcribed from NTRS. The
PSI-99 table and [NTRS 20170008805 Table I](https://ntrs.nasa.gov/citations/20170008805)
both give oxygen as start-to-end ranges for samples 2-8 (`22.1 to 22.0`) and 2-9
(`22.0 to 21.9`). The canonical `oxygen_pct` uses the **initial** value (22.1 and
22.0), correcting two earlier end-value transcriptions. The sources disagree on
sample 2-1 oxygen (PSI-99 says approximately 21.5; NTRS Table I and the flight
description say approximately 22.1) and sample 2-6 flow (PSI-99 says 20 cm/s;
NTRS explicitly says 25 cm/s). Those rows retain the NTRS values, with the
discrepancies recorded here. PSI-98 and PSI-100 have other unit/header ambiguities;
their values were not substituted for NTRS measurements without reconciliation.
