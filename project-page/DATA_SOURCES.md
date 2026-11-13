# FLARE-X Data Sources

Primary NASA data foundation planned for FLARE-X:

- **NASA Physical Sciences Informatics (PSI)** — https://psi.nasa.gov/physci/repo
- **BASS-II — PSI-25** — https://psi.nasa.gov/physci/repo/data/investigations/PSI-25
- **FLEX — PSI-69** — https://psi.nasa.gov/physci/repo/data/investigations/PSI-69
- **SAFFIRE-I — PSI-98** — https://psi.nasa.gov/physci/repo/data/investigations/PSI-98
- **SAME — PSI-102** — https://psi.nasa.gov/physci/repo/data/investigations/PSI-102
- **SPICE — PSI-107** — https://psi.nasa.gov/physci/repo/data/investigations/PSI-107

## Planned roles

- **BASS-II:** solid-material combustion evidence; possible propagation/extinction modelling if labels support validation.
- **FLEX:** droplet extinction classification and boundary exploration.
- **SPICE:** primary quantitative flame-length regression candidate.
- **SAFFIRE:** large-scale spacecraft-fire context and evidence comparison.
- **SAME:** smoke/aerosol evidence and later smoke-intelligence analysis.

Final implementation should preserve investigation identifiers, experiment/test identifiers, source files, original units, canonical units, DOI/source attribution and dataset/version provenance.

## NASA background and safety references

The following sources add scientific, historical, and technology-transfer context. They are
not source records for the curated experiment rows and do not validate FLARE-X predictions.
The PSI search is a discovery catalog; row-level evidence is cited to the specific PSI records
and NASA Technical Reports Server (NTRS) reports in [`docs/DATA_SOURCES.md`](../docs/DATA_SOURCES.md).

### Combustion science

- NASA, [PSI Data Repository: combustion science search](https://psi.nasa.gov/physci/repo/search?q=combustion) — discovery page for physical-sciences investigation records and data.
- NASA Glenn Research Center, [Combustion Science](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/) — overview of NASA microgravity combustion research and investigations.
- NASA, [A Researcher's Guide to International Space Station Combustion Science](https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/) (2015) — research guide covering ISS combustion investigations and research opportunities.
- NASA ScienceCasts, [The Power of Studying Combustion on the ISS](https://www.youtube.com/watch?v=W1oXykoz9zg) (2018; 3 min 36 sec) — educational video introduction to combustion research aboard the ISS.

### Mission and fire-safety history

- NASA Safety and Mission Assurance, [Apollo 1](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1) — crewed mission, pre-launch cabin fire, investigation, and lessons learned.
- NASA Safety and Mission Assurance, [Apollo 13](https://sma.nasa.gov/sma-disciplines/accllp/apollo-13) — mission history, oxygen-tank failure, investigation, and lessons learned.
- NASA History, [25 Years Ago: Fire Aboard Space Station Mir](https://www.nasa.gov/history/25-years-ago-fire-aboard-space-station-mir/) — account of the 1997 fire during the Mir program.

### Fire-safety technology transfer

- NASA Spinoff, [Fireman's Air Tanks](https://spinoff.nasa.gov/node/9582) (originally published 1976) — firefighter breathing equipment adapted from spacesuit technology.
- NASA Spinoff, [Fire Detector](https://spinoff.nasa.gov/node/9407) (originally published 1978) — shuttle smoke-detection technology described as distinguishing combustion particles from dust.
- NASA Spinoff, [New Technology for the Fire Attire](https://spinoff.nasa.gov/node/9918) (originally published 1982) — firefighter protective clothing using materials and design concepts developed for space applications.
