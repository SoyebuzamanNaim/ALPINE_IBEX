# Space Apps 2026 submission kit

This is a prepared narrative and demonstration plan, not a claim of competition eligibility,
NASA approval, completed submission, or a guaranteed award.

## Challenge fit

The official [Flame in Freefall challenge](https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/?tab=details)
asks for an interactive dashboard that summarizes, ranks and interprets microgravity combustion
findings for human exploration. Its indexed public summary was checked on November 13, 2026.
The full Details page could not be retrieved reliably during this preparation; confirm the
complete statement and the current participant guides before submitting. Do not substitute an
older year's rules.

| Challenge job | Implemented behavior | Where to show it |
|---|---|---|
| Find NASA findings | Search indexed report titles, abstracts and keywords; inspect curated observations | Evidence desk, report search and experiment archive |
| Summarize | Deterministic summaries retain the source observation, conditions and inference limits | Selected evidence and downloadable JSON bundle |
| Rank | Numerical similarity across oxygen, pressure and airflow, with an explicit material penalty; report search uses BM25 lexical relevance | Ranked observation cards and report results |
| Interpret | Expose geometry, direction, missing ignition context, recorded differences and unresolved questions | Evidence desk and Compare studies |
| Make research accessible | Scenario presets and text parsing, keyboard navigation, responsive views, original citation links | Desktop and phone demonstration |
| Identify next questions | Count indexed observations in oxygen–flow bins; label proposed experiments as team proposals | Coverage map |

The AI/ML component is a guarded linear-SVM research classifier. Retrieval, parsing,
comparison and summaries use numerical, lexical or deterministic methods. There is no
generative model, semantic claim validator, autonomous scientific researcher, or
superintelligence implementation. Describe the implemented methods accurately.

## Short description

FLARE-X turns scattered NASA microgravity combustion observations into a traceable research
workspace. Enter a scenario, inspect similar recorded tests, see which conditions differ,
read the original observations and citations, and explore what the indexed dataset does
and does not cover.

## Project description draft

Spacecraft-fire research spans different materials, geometries, atmospheres and ignition
procedures. A similar oxygen concentration does not make two tests interchangeable.
Researchers and students need a way to inspect those differences alongside the finding.

FLARE-X indexes 200 curated observations from seven NASA report groups. It joins NASA PSI
test conditions with report observations and preserves source references. The evidence desk
shows the nearest records, the ranking method, the reported observation and what cannot be
concluded. Report search helps users locate indexed abstracts. The comparison view reports
recorded differences without inventing causes or a scientific reliability score. The
coverage map describes the current dataset and labels follow-up studies as team proposals.

An optional research classifier and a separately scoped published PMMA reference allow
further exploration. They remain distinct from observations. The classifier has no
independent validation, and neither an observation nor a model estimate establishes safety.
Evidence retrieval remains available if the optional model cannot load. Users can download
their scenario and cited evidence for further source review.

## NASA data actually used

- [NASA PSI-25 BASS-II](https://psi.nasa.gov/physci/repo/data/investigations/PSI-25),
  DOI `10.60555/4qc4-de67`: calibrated initial test conditions. Outcomes were curated from
  [NTRS 20210011385](https://ntrs.nasa.gov/citations/20210011385), not supplied as PSI labels.
- Saffire report groups [20170008805](https://ntrs.nasa.gov/citations/20170008805),
  [20210011521](https://ntrs.nasa.gov/citations/20210011521) and
  [20240002981](https://ntrs.nasa.gov/citations/20240002981): selected flight observations.
- Other indexed observations: [BASS 20140011099](https://ntrs.nasa.gov/citations/20140011099),
  [exploration atmospheres 20080034883](https://ntrs.nasa.gov/citations/20080034883), and
  [drop-tower extinction 19890014267](https://ntrs.nasa.gov/citations/19890014267).

The [source inventory](DATA_SOURCES.md), [labeling protocol](LABELING_PROTOCOL.md) and
[data schema](DATA_SCHEMA.md) explain provenance and curation limits. Other corpus reports
and contextual links are not automatically additional labeled experiments or independent
model validation.

## Suggested two-minute demonstration

This duration is a team proposal, not a verified official video limit.

| Time | Screen/action | Explain |
|---|---|---|
| 0:00–0:15 | Open the public URL in a fresh browser | “We help people inspect NASA combustion evidence and its limits.” |
| 0:15–0:40 | Enter `PMMA at 19% oxygen, 101.3 kPa, 5 cm/s` | Show the recorded observation, input differences and source citation. |
| 0:40–0:55 | Expand “Why this record matches”; trace a citation | “This ranks proximity, not scientific reliability. Geometry and ignition context still matter.” |
| 0:55–1:10 | Search `PMMA extinction`; download the evidence | Show real indexed report results and a portable cited scenario bundle. |
| 1:10–1:25 | Compare BASS-II and Saffire | Show recorded differences and missing context. Do not claim to explain their physical causes. |
| 1:25–1:45 | Open the coverage map | “An empty bin means no matching indexed observations. These experiments are our proposals.” |
| 1:45–2:00 | Return to the evidence and its limits | State the intended research use and the need for source review. Keep model accuracy out of the pitch. |

Use the conflicting PMMA scenario `18% oxygen, 101.3 kPa, 3 cm/s` as an optional backup
demonstration of model abstention. The published PMMA curve describes established-flame
extinction under its specified scope; its post-burn oxygen basis differs from the scenario's
initial oxygen. Do not call the displayed offset a safety margin.

## Validity and next work

The table is dominated by BASS-II, includes interpreted labels and repeated conditions from
individual burns, and is not an exhaustive literature review. The legacy `outcome_interpreted`
flag does not consistently describe narrative curation. Displayed labels require source review.
See the [limitations](LIMITATIONS.md).

The model's exploratory selection score is 84.0% against an 81.5% majority baseline, with
40.3% balanced accuracy, eight of 35 no-spread observations detected and no marginal-spread
recall. The full search procedure scored 25.5% in nested report validation. These are
research evaluation results, not a safety-performance claim. See the [model card](MODEL_CARDS.md).

Next scientific work is independent review of label assignments, explicit ignition-history
and oxygen-basis metadata, more independently verified minority outcomes, and external
validation. User studies should evaluate whether people can find and interpret cited records;
no measured time saving or operational benefit is currently claimed.

## Items requiring the team

- **Public demo:** deploy FastAPI, configure Pages if used, and run `npm run test:demo` against
  the exact URL. A static Pages deployment alone is insufficient. See [deployment](DEPLOYMENT.md).
- **Official team/project page:** supply the registered team URL and complete its actual form.
  No account submission has been performed by this repository preparation.
- **Recording:** record and upload the real working demonstration; verify the current format,
  duration, accessibility and sharing requirements in the official submission guide.
- **Credits and disclosure:** name actual contributors and tools used. Disclose this repository's
  pre-existing work and identify work completed during the hackathon; confirm eligibility with
  the current rules and your Local Lead.
- **Final review:** confirm the complete 2026 challenge statement, local event deadline and current
  participant guides. The [2026 event page](https://www.spaceappschallenge.org/2026/) lists project
  submission from November 14 at 09:00 through November 15 at 23:59 local time; verify the applicable
  registered-event timezone.

The [2026 Ajmer event page](https://www.spaceappschallenge.org/2026/local-events/ajmer/)
describes Impact, Creativity, Validity, Relevance and Presentation as judging criteria. Use
them to organize the pitch, while checking the current global guide for authoritative rules.
