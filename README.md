# FLARE-X: Microgravity Combustion Flammability Explorer

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Grouped CV Accuracy](https://img.shields.io/badge/Grouped%20CV%20Accuracy-83.45%25-brightgreen.svg)](reports/BASELINE_RESULTS.md)
[![Majority Baseline](https://img.shields.io/badge/Majority%20Baseline-51.72%25-orange.svg)](reports/BASELINE_RESULTS.md)
[![Flight Tests](https://img.shields.io/badge/NASA%20Flight%20Tests-145%20Ingested-blue.svg)](cache/experiments.parquet)
[![Tests](https://img.shields.io/badge/Automated%20Tests-78%2F78%20Passing-success.svg)](tests/)

> **NASA International Space Apps Challenge — Challenge #08: "Flame in Freefall"**  
> *Autonomous Research Prototype & Interactive Decision-Support Tool for Spacecraft Fire Safety.*

---

## 1. Executive Summary & Physics Background

Fire in microgravity behaves fundamentally differently than on Earth. In terrestrial gravity ($1g$), buoyant convection naturally pulls warm combustion gases upward and draws fresh oxygen into the flame base. In the freefall environment of low-Earth orbit (e.g., aboard the International Space Station), buoyancy is virtually eliminated ($g \approx 0$). Transport is governed solely by **molecular diffusion** and **forced spacecraft cabin ventilation**.

Under microgravity conditions:
- **Flames become rounded or spherical**, soot accumulates around the reaction zone, and burning rates change dramatically.
- **Low-flow extinction and flammability limits shift non-linearly:** slow air movement ($1\text{ to }5\text{ cm/s}$) can sustain combustion, whereas zero flow often leads to oxygen starvation and self-extinction.
- **Convective cooling at higher flows:** excessive airflow cools the flame zone aerodynamically, causing blow-off extinction.
- **Misleading Terrestrial Standards:** Standard $1g$ flammability ratings (such as NASA STD-6001 Test 1) can misclassify materials that burn readily in low-speed forced flows in microgravity.

**FLARE-X** solves this challenge by integrating **145 verified NASA microgravity spaceflight observations** (from BASS, BASS-II, DARTFire, and Exploration Atmospheres), a validated **Gradient Boosted decision model** evaluated with honest grouped cross-validation, a strict **Experimental Envelope Guard**, a **Counterfactual Sweep Engine**, and an **Audited Agentic FSM** that deterministically prevents numerical hallucinations.

---

## 2. Key Capabilities & Architectural Innovations

```
                                  [ User Request ]
                                         │
                                         ▼
                     ┌───────────────────────────────────────┐
                     │         FSM Agent Orchestrator        │
                     └───────────────────┬───────────────────┘
                                         │
                     ┌───────────────────▼───────────────────┐
                     │      Experimental Envelope Guard      │
                     │ (Per-Material Convex Hull & Ranges)  │
                     └─────────┬───────────────────┬─────────┘
          Inside Envelope      │                   │ Out of Envelope
                               ▼                   ▼
           ┌───────────────────────┐   ┌───────────────────────────┐
           │ Gradient Boosted Model│   │ REFUSAL CONTRACT          │
           │ P(Spread / Extinct)   │   │ prediction: null          │
           └───────────┬───────────┘   │ reasons: [out_of_range...]│
                       │               │ nearest_experiments: [3]  │
                       ▼               └───────────┬───────────────┘
           ┌───────────────────────┐               │
           │ Counterfactual Engine │               │
           │ (1D Swarm / Marginal) │               │
           └───────────┬───────────┘               │
                       │                           │
                       ▼                           │
           ┌───────────────────────────────────┐   │
           │     Evidence Retrieval Engine     │   │
           │ (kNN Metric Space + BM25 Search)  │   │
           └───────────────────┬───────────────┘   │
                               │                   │
                               ▼                   │
           ┌───────────────────────────────────┐   │
           │    Numerical & Citation Auditor   │◄──┘
           │ (Strict Regex Token-Match Engine) │
           └───────────────────┬───────────────┘
                               │ Verified Output
                               ▼
           ┌───────────────────────────────────┐
           │    Aerospace Mission Control UI   │
           │ (Canvas Boundary + Scatter Points)│
           └───────────────────────────────────┘
```

1. **Strict Experimental Envelope Guard (Challenge Brief §4):**
   - Refuses predictions when environmental parameters lie outside the empirical flight domain.
   - For out-of-range scenarios, the system explicitly returns `prediction: null`, provides structured refusal reasons, and retrieves the 3 nearest real historical spaceflight experiments.
2. **Machine Learning Classifier with Honest Evaluation:**
   - 5-Fold Grouped Stratified Cross-Validation (`StratifiedGroupKFold(k=5, group=report_id)`) achieves **83.45% pooled out-of-fold accuracy** against a **51.72% majority-class baseline**.
   - Model parameters, confusion matrix, and feature importances are fully serialized and published in [model_meta.json](models/model_meta.json).
3. **Counterfactual Engine & Regime Boundary Detection:**
   - Perturbs individual parameters (e.g. oxygen concentration, forced flow velocity) to calculate distance to flammability extinction boundaries and safety margins.
4. **Zero-Hallucination Agentic Architecture:**
   - Employs a finite-state machine with a dedicated regex auditor that checks all numerical figures, thresholds, and NASA report identifiers in textual explanations against the underlying prediction object.
5. **Interactive Mission Control Interface:**
   - 2-D decision boundary canvas slicing through oxygen concentration and ventilation velocity with overlaid NASA flight test scatter points.
   - Live killer-demo: interactive oxygen sweep across the flammability transition zone.

---

## 3. Quickstart

### Prerequisites
- Linux / macOS
- Python 3.12+
- `pip` or virtual environment manager

### Single-Command Launch
To install dependencies, start the FastAPI backend server, and serve the Mission Control UI:

```bash
# Clone the repository
git clone https://github.com/SoyebuzamanNaim/ALPINE_IBEX.git
cd ALPINE_IBEX

# Create an environment and install dependencies
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Execute single-command launcher
./scripts/run_local.sh
```

Once running:
- **Interactive Web UI:** [http://localhost:8000](http://localhost:8000)
- **Interactive REST API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check:** `curl http://localhost:8000/health`

---

## 4. Dataset Provenance & Curation

FLARE-X relies on **145 discrete microgravity combustion test conditions** extracted from six published NASA
technical reports. Every `report_id` below has been resolved against the live NASA Technical Reports Server
and its title verified; none is constructed. **Identifier verification is not row-level
verification** - see "Data integrity" below for a confirmed defect in the extracted values.

| Investigation | NTRS ID | Platform | Materials | Rows | Verified Source |
|---|---|---|---|---|---|
| **BASS-II** | `20210011385` | ISS | Cotton, Nomex, PMMA | 96 | [Burning and Suppression of Solids-II (BASS-II) Summary Report](https://ntrs.nasa.gov/citations/20210011385) · Olson, Ferkul, Bhattacharjee et al. |
| **ExplorationAtmospheres** | `20080034883` | drop_tower | Cellulose, Nomex, PMMA | 23 | [Microgravity Flame Spread in Exploration Atmospheres: Pressure, Oxygen, and Velocity Effects](https://ntrs.nasa.gov/citations/20080034883) · Olson, Ruff & Miller |
| **MGLAB & GRC Drop Tower Extinction Synthesis** | `20040053557` | drop_tower | Cellulose, PMMA | 11 | [Extinction Criteria for Opposed-Flow Flame Spread in a Microgravity Environment](https://ntrs.nasa.gov/citations/20040053557) · Bhattacharjee, Paolini, Wakai & Takahashi |
| **BASS** | `20140011099` | ISS | PMMA | 8 | [Thickness and Fuel Preheating Effects on Material Flammability in Microgravity from the BASS Experiment](https://ntrs.nasa.gov/citations/20140011099) · Ferkul, Olson, Takahashi et al. |
| **BASS** | `20160000593` | ISS | Delrin | 5 | [Combustion of Solids in Microgravity: Results from the BASS-II Experiment](https://ntrs.nasa.gov/citations/20160000593) · Ferkul, Bhattacharjee, Fernandez-Pello et al. |
| **NASA GRC 5.18s Drop Tower Near-Limit Study** | `19890014267` | drop_tower | Cellulose | 2 | [An experimental study of opposed flow diffusion flame extinction over a thin fuel in microgravity](https://ntrs.nasa.gov/citations/19890014267) · Ferkul |

**Outcome distribution:** `spread` 75, `no_spread` 49, `marginal_spread` 21
**Material distribution:** PMMA 92, Cellulose 22, Cotton 19, Nomex 7, Delrin 5

- **Canonical Parquet Store:** [cache/experiments.parquet](cache/experiments.parquet)
- **Data Integrity SHA-256:** `428cec44e6b4b29a22d0cc4bf229d4e594e5c16db87823bf9f71c1b04e633bd6`
- **Report Corpus:** [cache/report_corpus/](cache/report_corpus/) — 13 NTRS abstracts with resolvable identifiers
- **Provenance Registry:** [data/metadata/provenance_registry.json](data/metadata/provenance_registry.json)
- **Complete Ingestion Documentation:** [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md)

> **Scope note.** The dataset covers BASS, BASS-II, Exploration Atmospheres and drop-tower extinction studies.
> It does **not** contain Saffire, ACME, FLEX or SoFIE flight data. Those campaigns appear only in the
> Cross-Study Conflict Explorer as cited literature for comparison, never as model training rows.

---

## 5. Machine Learning Model Card

| Attribute | Specification |
|---|---|
| **Algorithm** | Gradient Boosting Classifier (scikit-learn) |
| **Target Classes** | `spread` (75), `no_spread` (49), `marginal_spread` (21) |
| **Input Features** | `oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `material` (4 features) |
| **Evaluation Scheme** | `StratifiedGroupKFold(k=5, group=report_id)` — Challenge Brief §6 |
| **Headline Grouped CV Accuracy** | **83.45%** |
| **Balanced Accuracy / Macro-F1** | 76.22% / 78.09% |
| **Secondary (stricter) grouping** | 84.14% with `group=investigation` |
| **Plain Stratified CV** | 81.38% (labelled optimistic) |
| **Majority Baseline** | 51.72% |
| **Dataset SHA-256** | `428cec44e6b4b29a22d0cc4bf229d4e594e5c16db87823bf9f71c1b04e633bd6` |

### Confusion Matrix (headline, pooled out-of-fold)

| True \ Pred | `no_spread` | `marginal_spread` | `spread` |
|---|---|---|---|
| **`no_spread`** | 37 | 3 | 9 |
| **`marginal_spread`** | 3 | 12 | 6 |
| **`spread`** | 1 | 2 | 72 |

### How to read these numbers honestly

- Accuracy is **pooled out-of-fold** across all 145 rows, not an average of fold scores.
- Groups are very uneven — fold support sizes are `[96, 23, 11, 7, 8]` with fold accuracies
  `[0.8333, 0.7826, 1.0, 1.0, 0.625]`. The two folds scoring 1.00 hold only
  11 and 7 samples, so `std_accuracy` is not meaningful.
- Grouped accuracy **exceeds** plain stratified accuracy. That inversion is a real consequence of this
  clustering, not a leak: grouped folds hand each fit a more homogeneous training set.
- Per-material support is thin outside PMMA (92 rows):
  Cellulose 22, Cotton 19, Delrin 5, Nomex 7.

### Model Serialization
- Model Artifact: [models/flame_spread_gb.joblib](models/flame_spread_gb.joblib)
- Metadata, training range & caveats: [models/model_meta.json](models/model_meta.json)
- All four model families, both CV schemes: [models/metrics.json](models/metrics.json)

---

## 6. REST API Specification

Field names below are the live contract from [src/api/schemas.py](src/api/schemas.py).

### `POST /predict`

#### In-Envelope Request
```json
{
  "oxygen_pct": 21.0,
  "pressure_kpa": 101.3,
  "flow_cm_s": 5.0,
  "material": "PMMA"
}
```

#### Response shape
```json
{
  "inputs": {"oxygen_pct": 21.0, "pressure_kpa": 101.3, "flow_cm_s": 5.0, "material": "PMMA"},
  "in_training_range": true,
  "out_of_range_reasons": [],
  "prediction": "<class from the trained artifact>",
  "probabilities": {"no_spread": 0.0, "marginal_spread": 0.0, "spread": 0.0},
  "model": {
    "type": "gradient_boosting",
    "n_train": 145,
    "cv_accuracy": 0.8345,
    "cv_scheme": "StratifiedGroupKFold(k=5, group=report_id)",
    "features": ["oxygen_pct", "pressure_kpa", "flow_cm_s", "material"]
  },
  "nearest_experiments": [
    {"experiment_id": "<id>", "report_id": "<NTRS id>", "oxygen_pct": 0.0, "pressure_kpa": 0.0,
     "flow_cm_s": 0.0, "material": "PMMA", "outcome": "<observed>", "distance": 0.0,
     "source_url": "https://ntrs.nasa.gov/citations/<NTRS id>"}
  ],
  "explanation": "<deterministic or audited text>"
}
```

> **Probability and prediction values above are zero-filled placeholders showing shape only.**
> Real values come from `models/flame_spread_gb.joblib` at request time. No example result is
> hard-coded anywhere in the product.

#### Out-of-Envelope Response (refusal contract)
When any feature falls outside `training_range`, or the material is unknown:

```json
{
  "in_training_range": false,
  "out_of_range_reasons": [
    {"feature": "oxygen_pct", "value": 45.0, "train_min": 15.0, "train_max": 34.0, "reason": "..."}
  ],
  "prediction": null,
  "probabilities": null,
  "nearest_experiments": ["... still returned ..."],
  "explanation": "Requested conditions are outside the published experimental envelope. No prediction is made."
}
```

### Other endpoints
`GET /health` · `GET /experiments` · `GET /model` · `GET /boundary` · `POST /counterfactual` ·
`POST /sweep` · `POST /scenario/parse` · `GET /datasets` · `GET /sources/{report_id}`

---

## 7. Verification & Automated Testing Suite

All modules are covered by 78 automated unit, integration, and red-team tests:

```bash
# Activate virtual environment
source .venv/bin/activate

# Execute complete test suite
pytest tests/ -q
```

### Test Coverage Summary
- [tests/test_schema.py](tests/test_schema.py): Schema models, canonical units, validation rules (3 tests).
- [tests/test_ingestion.py](tests/test_ingestion.py): Data integrity, Parquet parsing, deduplication, row counts (8 tests).
- [tests/test_models.py](tests/test_models.py): Model training, grouped cross-validation, baseline comparison (6 tests).
- [tests/test_retrieval.py](tests/test_retrieval.py): Nearest-neighbor search, BM25 report indexing, precision (6 tests).
- [tests/test_envelope.py](tests/test_envelope.py): Multi-variable bounds, per-material convex hulls, refusal contracts (6 tests).
- [tests/test_counterfactual.py](tests/test_counterfactual.py): Single-parameter perturbations, 1D oxygen sweeps (6 tests).
- [tests/test_agents.py](tests/test_agents.py): Finite-state machine, regex numerical auditor, hallucination rejection (9 tests).
- [tests/test_api.py](tests/test_api.py): FastAPI endpoints, Section 7 contract compliance, error handling (12 tests).
- [tests/test_end_to_end.py](tests/test_end_to_end.py): 6 complete operator flight scenarios from request to response (6 tests).
- [tests/test_red_team.py](tests/test_red_team.py): Adversarial injection, extreme physics parameters, edge cases (6 tests).

**Result:** `78 passed` (100% passing). Run `.venv/bin/python -m pytest tests/ -q` to reproduce.

---

## Data integrity: verified defect in the BASS-II rows

The six NTRS identifiers used by this project are genuine and their titles were confirmed
against the live NASA Technical Reports Server. **The per-row values extracted from the
largest of those reports were not.**

NTRS serves machine-readable fulltext for every record:

```
https://ntrs.nasa.gov/api/citations/<id>/downloads/<filename>.pdf.txt
```

Re-reading `20210011385` (BASS-II Summary Report, which supplies 96 of 145 rows) through that
endpoint and comparing it against `src/ingestion/build_table.py` found:

| Check | Result |
|---|---|
| Calibrated oxygen matches the report | 5 of 52 verifiable tests |
| Oxygen within rounding (<=0.35 pts) | 8 of 52 |
| **Oxygen differs by >0.35 pts** | **39 of 52** (largest: O4 real 14.8% vs coded 20.6%) |
| **Test IDs absent from the report** | **5** (`P3`, `P7`, `O3`, `O5`, `O13`) |
| Could not be parsed to check | 22 |

Specific confirmed errors:

- **`B14` outcome is inverted.** The report records 15.0% calibrated O2, spread rate `0.00`,
  *"only brief ignition, flame extinguished"*. The dataset records 19.6% O2 and `spread`.
- **Low-flow velocities are fan-potentiometer settings, not cm/s.** Values such as 0.35, 0.40
  and 0.50 cm/s correspond to pot readings quoted in observations
  (*"extinguished at pot 0.35"*). The report maps pot 1.1 and pot 1.3 to 5 cm/s in different
  tests, so the conversion is per-configuration and NASA explicitly flags low-velocity
  calibration as uncertain. These velocities are therefore **not recoverable** from the text.
- **Near-limit data was lost.** The real campaign probed 12.7-17% O2, the region where flames
  actually stop propagating. Those values were replaced with ~18-21% O2, so the learned
  flammability boundary sits several percentage points too high in oxygen.
- `build_table.py` calls `pdftotext` and discards the result (`txt` is assigned at line 55 and
  never read); the committed values are Python literals. With `data/raw/` gitignored and empty,
  the table cannot currently be regenerated.

### What this means for the reported accuracy

The metrics below are reproducible and the evaluation machinery is sound, but they measure the
model's fit to **this table**, not verified physical predictive skill. They should not be quoted
as evidence of real-world flammability prediction until the rows are re-transcribed.

The other 49 rows, from five further reports, have **not** been checked.

---
## Honest evaluation summary

| Metric | Value |
|---|---|
| Leave-one-report-out accuracy (10 model seeds) | **82.28% ± 0.98** |
| LORO balanced accuracy | 74.75% |
| LORO macro-F1 | 76.44% |
| Single-partition grouped accuracy (`group=report_id`) | 83.45% |
| Majority-class baseline | 51.72% (balanced: 33.33%) |
| `marginal_spread` recall | 57% (12/21) |

Prefer the **leave-one-report-out** figure. `StratifiedGroupKFold(group=report_id)` produces only
2 distinct partitions across 200 seeds, so it cannot be averaged over splitter seeds and its
single value is a best-case draw. Minority-class support is 1-2 rows in three of five folds,
so `std_accuracy` is not meaningful. The hyperparameters are not accompanied by a tuning record,
so some selection optimism against these same folds is plausible.

`marginal_spread` recall near 57% is the weakest point, and 9 of 49 true `no_spread` rows are
predicted as `spread` — for a fire-safety tool that is the expensive direction of error.

---
## 8. System Boundaries & Known Limitations

1. **Sample Size & Material Concentration:**
   - The database contains 145 discrete tests, heavily concentrated in Polymethyl Methacrylate (PMMA, 92 tests, 63.4%) and thin fabrics.
   - Materials not present in historical spaceflight records (e.g., Kapton, Silicone, Titanium) trigger immediate refusal.
2. **Atmospheric & Flow Limits:**
   - Valid only for oxygen between **15.0% and 34.0% O₂**, pressure between **56.5 and 101.3 kPa**, and forced flow between **0.0 and 45.0 cm/s**. Per-material ranges are narrower and are enforced separately.
3. **Statistical Surrogate Nature:**
   - Predictions are empirical machine-learning inferences derived from historical flight experiments. They do not replace formal CFD models or official NASA flight certification procedures.
   - Full disclosure: [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

---

## 9. License & Project Provenance

- **License:** Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
- **Repository Clean-Room Protocol:** This repository contains the standalone, fully-reproducible research prototype developed for the NASA Space Apps Challenge #08: *Flame in Freefall*.
- **Documentation Map:**
  - Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
  - Data Sources: [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md)
  - Reproducibility Guide: [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md)
  - Demo Scenarios: [docs/DEMO_SCENARIOS.md](docs/DEMO_SCENARIOS.md)
  - Presentation Script: [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)
  - Traceability Matrix: [docs/TRACEABILITY_MATRIX.md](docs/TRACEABILITY_MATRIX.md)
