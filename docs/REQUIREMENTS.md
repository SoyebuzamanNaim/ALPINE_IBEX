# FLARE-X — Requirements

> Status: research/demo prototype (pre-hackathon). See `NON_GOALS.md` and the competition-compliance
> note in the README. Nothing in this repository is a NASA product or NASA-endorsed.

## Sources consulted

| Source | What was used | Verification status |
|---|---|---|
| `Prompt/22_CHALLENGE_BRIEF_FLAME_IN_FREEFALL.md` | Authoritative product spec for this prototype | Read in full |
| NASA Space Apps 2026 challenge listing "Flame in Freefall: AI-Powered Fire Safety Insights from Microgravity Combustion Data" (spaceappschallenge.org) | Challenge summary | **Partially verified**: the challenge page is client-rendered and could not be fetched as text by the build agent (the direct slug returned 404 to a static fetch). The summary below was cross-checked against search-engine snippets of the official page. Re-verify by hand before submission. |

## A. Challenge requirements (Brief §1 — the challenge statement)

| ID | Requirement |
|---|---|
| CR-1 | Use AI on decades of microgravity combustion research. |
| CR-2 | Produce fire-safety insight for spacecraft. |
| CR-3 | Respect that fire behaves differently without buoyancy (spherical flames, slow spread, survival in conditions that would extinguish them on Earth). |

Search-snippet summary of the official listing (not authoritative, recorded for traceability):
"develop an interactive, AI-powered dashboard that summarizes, ranks and interprets existing
microgravity combustion experimental data to provide actionable fire-safety insights".

## B. Adopted design decisions (Brief §2–10 — guidance, NOT NASA-required)

| ID | Decision | Brief § |
|---|---|---|
| DD-1 | Flammability explorer: inputs `oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `material` | 2 |
| DD-2 | Target = flame-spread regime class, model trained on published microgravity results | 2, 5.3 |
| DD-3 | Explanation layer cites real experiments with report IDs and resolvable URLs | 2, 8 |
| DD-4 | Oxygen-sweep demo — only if the data supports a boundary; never forced | 2 |
| DD-5 | Training table browsable in UI and committed (`cache/experiments.parquet`) | 3, 5.2 |
| DD-6 | Honest accuracy: StratifiedGroupKFold by `report_id` headline, plus optimistic plain stratified CV, confusion matrix, majority baseline | 3, 6 |
| DD-7 | Hard range guard: out-of-range → `prediction=null`, `probabilities=null`, reasons, still return nearest experiments | 4 |
| DD-8 | Every `report_id` resolves to a real NTRS/OSDR record; never construct IDs | 5.1 |
| DD-9 | Small gradient-boosting classifier; compared against majority + logistic regression (+ RF per Phase 05) | 6 |
| DD-10 | Artifact `models/flame_spread_gb.joblib` + `models/model_meta.json` with `training_range` | 6 |
| DD-11 | FastAPI `/predict`, `/health`, `/experiments`, `/model`, `/boundary` | 7 |
| DD-12 | Bounded explanation layer; code check rejects numbers / IDs absent from the prediction object; deterministic fallback | 8 |
| DD-13 | Frontend: sliders, material selector, probability bar, decision-boundary slice plot with real points, nearest-experiment citations, data & model page, operator framing | 9 |
| DD-14 | Required paths `cache/` and `src/compute/model.py` | 10 |
| DD-15 | Apache-2.0 licence, README with data sources, model card, limitations | 12 |

## C. Assumptions

| ID | Assumption | Risk if wrong |
|---|---|---|
| A-1 | Enough published microgravity test conditions with O₂ / pressure / flow / material / outcome exist in public NTRS PDFs to train a small classifier. | Small `n_train`; model may be weak. Mitigation: report honestly, reduce classes. |
| A-2 | Published flammability-boundary data (flame / no-flame at given O₂ and flow) can be mapped to regime classes with a written rule. | Labels need interpretation → flagged per row. |
| A-3 | NTRS public-distribution PDFs may be cached locally for research use; full text redistribution is not assumed (corpus stores metadata + abstract, full text only kept locally). | Licensing; mitigated by storing abstracts/metadata only in the committed corpus. |
| A-4 | No LLM API key is configured; the deterministic template explanation is the default path. | None — the template path is required by Brief §8.4 anyway. |

## D. Proposed innovations (ours, not required)

- Per-material envelope and kNN-distance "sparse region" warning layered on top of the min/max refusal.
- Counterfactual sweep endpoint that reports the first class change along an axis and the experiments on either side.
- Bounded agent state machine (Phase 09) wrapping the same deterministic core.

## E. Target users

1. Combustion researchers — want to see where published data exists and what it says.
2. Spacecraft fire-safety researchers — want flammability-boundary context for material/atmosphere choices.
3. Mission / safety analysts — want a plain-language, uncertainty-aware reading, and a hard "no data here" signal.
4. Students / research users — want a browsable, cited dataset.

## F. Primary prototype scenario

A user selects a material present in the table, holds pressure and flow inside the data range, and sweeps
oxygen. The tool shows the predicted regime + probabilities, the 3 nearest real tests with NTRS citations,
the decision-boundary slice with the real test points, and refuses when the request leaves the envelope.
