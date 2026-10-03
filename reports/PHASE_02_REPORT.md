# Phase 02 Report — NASA Data Discovery

## 1. Objective
Systematically identify and audit microgravity combustion datasets across NASA Physical Sciences Informatics (PSI)
and NASA Technical Reports Server (NTRS), verify raw availability, and establish a shortlist of usable data for the
flammability explorer prototype.

## 2. Methodology & NASA Endpoints Verified
1. **NASA Physical Sciences Informatics (PSI):**
   - Verified live API: `https://psi.nasa.gov/geode-py/ws/repo/search?data_source=psi&size=150`
   - Retrieved and cached 133 total physical science investigations, identifying 26 combustion investigations.
   - Cached raw response in `data/raw/psi/psi_investigations.json` with SHA256 checksum recorded in `source_manifest.csv`.
2. **NASA Technical Reports Server (NTRS):**
   - Verified live API: `https://ntrs.nasa.gov/api/citations/`
   - Retrieved citation metadata and public PDFs for 13 essential microgravity combustion reports (BASS, BASS-II,
     DARTFire, Exploration Atmospheres, SIBAL, SoFIE).
   - Recorded SHA256 hashes and download sizes for all 27 citation and PDF artifacts in `data/metadata/source_manifest.csv`.

## 3. Key Findings & Shortlist Rationale
- **Core Modeling Dataset Shortlist (Solid Fuel Flame Spread & Extinction):**
  - **BASS (PSI-26)** and **BASS-II (PSI-25)**: Evaluated PMMA rods, PMMA sheets, cotton-fiberglass blend fabrics, and Delrin.
    Varied ambient O2 (15% to 21% via N2 dilution), pressure (~101 kPa), and concurrent/opposed flow velocities (0–55 cm/s).
    Provides exact numeric parameters and verified outcome classes (`no_spread`, `marginal_spread`, `spread`).
  - **SAFFIRE (PSI-98, PSI-99, PSI-100)**: Large-scale flame spread in exploration atmospheres (reduced pressure, elevated O2).
  - **DARTFire / SIBAL Sounding Rocket & Drop Tower Data**: Low-velocity opposed-flow flame extinction over thin solids.
- **Catalogued but Excluded from Core Flame-Spread Model:**
  - **Droplet Combustion (FLEX / FLEX-2, PSI-69/68)**: Excluded because liquid droplet diameter and vaporization dynamics
    cannot be merged into solid surface flame-spread models without scientific compromise.
  - **Gaseous Diffusion Flames (SPICE, SLICE, ACME, PSI-107/106/20/21/22/23)**: Excluded because gaseous burner nozzle flow
    and coflow geometry are not comparable with solid fuel flammability.
  - **Smoke Aerosol Detection (SAME, SAME-R, DAFT, PSI-102/101/47)**: Excluded from flame-spread prediction because they measure
    smoke detector response curves rather than ignition/extinction limits.

## 4. Generated Artifacts
- `data/metadata/dataset_catalog.csv`: 23 audited investigations with exact NASA titles, PSI IDs, URLs, and scientific variables.
- `data/metadata/source_manifest.csv`: 28 raw files with SHA256 hashes and timestamps.
- `docs/NASA_DATASET_AUDIT.md`: Complete audit and scientific justification.
