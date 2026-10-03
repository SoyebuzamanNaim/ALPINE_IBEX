# FLARE-X: Microgravity Combustion Flammability Explorer

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Grouped CV Accuracy](https://img.shields.io/badge/Grouped%20CV%20Accuracy-79.31%25-brightgreen.svg)](reports/PHASE_05_REPORT.md)
[![Majority Baseline](https://img.shields.io/badge/Majority%20Baseline-51.72%25-orange.svg)](reports/PHASE_05_REPORT.md)
[![Flight Tests](https://img.shields.io/badge/NASA%20Flight%20Tests-145%20Ingested-blue.svg)](cache/experiments.parquet)
[![Tests](https://img.shields.io/badge/Automated%20Tests-68%2F68%20Passing-success.svg)](tests/)

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
   - 5-Fold Grouped Stratified Cross-Validation (`StratifiedGroupKFold(k=5, group=report_id)`) achieves **79.31% accuracy** against a **51.72% majority-class baseline**.
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
git clone https://github.com/flame-in-freefall/flare-x-prototype.git
cd flare-x-prototype

# Execute single-command launcher
./scripts/run_local.sh
```

Once running:
- **Interactive Web UI:** [http://localhost:8000](http://localhost:8000)
- **Interactive REST API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check:** `curl http://localhost:8000/health`

---

## 4. Dataset Provenance & Curation

FLARE-X relies on **145 discrete, verified microgravity flight observations** extracted from published NASA Technical Reports and Physical Sciences Informatics (PSI) repositories.

| Investigation / Mission | Platform | Fuel Materials | Validated Tests | Primary Literature Citation |
|---|---|---|---|---|
| **BASS** (Burning and Suppression of Solids) | ISS Microgravity Science Glovebox | PMMA (Cast Acrylic), Cotton Fabric | 68 | NASA/TP-2015-218497 |
| **BASS-II** | ISS Microgravity Science Glovebox | PMMA, Cotton Fabric, Delrin | 42 | NASA/TM-2018-220038 |
| **DARTFire** | KC-135 Reduced Gravity / Drop Tower | Ashless Filter Paper (Cellulose) | 22 | NASA/CR-2002-211568 |
| **Exploration Atmospheres Flammability** | 5.18-Second Zero-G Facility | Nomex, Cast Acrylic (PMMA) | 13 | NASA/TM-2019-220211 |

- **Canonical Parquet Store:** [cache/experiments.parquet](cache/experiments.parquet)
- **Data Integrity SHA-256:** `d5a06d2d0cce4e2fe2207bd490df4ec1213ca6eeabc1436243eb8d49dafd0be0`
- **Comprehensive Catalog:** [data/metadata/dataset_catalog.csv](data/metadata/dataset_catalog.csv)
- **Raw Files & Hashes:** [data/metadata/source_manifest.csv](data/metadata/source_manifest.csv)
- **Complete Ingestion Documentation:** [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md)

---

## 5. Machine Learning Model Card

| Attribute | Specification |
|---|---|
| **Algorithm** | Gradient Boosting Classifier (`HistGradientBoostingClassifier` / `GradientBoostingClassifier`) |
| **Target Classes** | `spread` (75 samples), `no_spread` (49 samples), `marginal_spread` (21 samples) |
| **Input Features** | `oxygen_concentration_pct`, `forced_flow_velocity_cm_s`, `pressure_kpa`, `sample_thickness_mm`, `material_name`, `sample_width_mm` |
| **Evaluation Strategy** | 5-Fold Stratified Grouped K-Fold Cross-Validation (`groups=report_id`) |
| **Honest Grouped CV Accuracy** | **79.31%** (Mean accuracy across grouped splits) |
| **Standard Un-grouped CV** | **80.69%** (Reported for comparison; optimistic due to intra-report clustering) |
| **Majority Baseline** | **51.72%** (Always predicting majority class `spread`) |
| **Confusion Matrix (Grouped)** | `[[37, 7, 5], [4, 11, 6], [2, 6, 67]]` (Rows: `no_spread`, `marginal_spread`, `spread`) |

### Model Serialization
- Model Artifact: [models/flame_spread_gb.joblib](models/flame_spread_gb.joblib)
- Metadata & Parameters: [models/model_meta.json](models/model_meta.json)
- Validation Metrics: [models/metrics.json](models/metrics.json)

---

## 6. REST API Specification (Section 7 Contract)

### `POST /predict`
Evaluates a query scenario against the microgravity envelope and returns prediction probabilities or refusal.

#### In-Envelope Request
```json
{
  "material_name": "PMMA",
  "oxygen_concentration_pct": 21.0,
  "forced_flow_velocity_cm_s": 5.0,
  "pressure_kpa": 101.3,
  "sample_thickness_mm": 2.0
}
```

#### In-Envelope Response
```json
{
  "in_training_range": true,
  "out_of_range_reasons": [],
  "prediction": "spread",
  "probabilities": {
    "no_spread": 0.082,
    "marginal_spread": 0.125,
    "spread": 0.793
  },
  "nearest_experiments": [
    {
      "test_id": "BASS_TR_042",
      "distance": 0.041,
      "material_name": "PMMA",
      "oxygen_concentration_pct": 21.0,
      "forced_flow_velocity_cm_s": 5.2,
      "flame_spread_observed": "spread",
      "source_report_id": "NASA-TP-2015-218497"
    }
  ],
  "explanation": "Predicted flame spread (probability: 79.3%) based on 145 NASA spaceflight experiments..."
}
```

#### Out-of-Envelope Request (Extrapolation Guard Triggered)
```json
{
  "material_name": "PMMA",
  "oxygen_concentration_pct": 45.0,
  "forced_flow_velocity_cm_s": 150.0,
  "pressure_kpa": 101.3,
  "sample_thickness_mm": 2.0
}
```

#### Out-of-Envelope Response (Refusal Contract)
```json
{
  "in_training_range": false,
  "out_of_range_reasons": [
    "oxygen_concentration_pct 45.0% exceeds training maximum 34.0%",
    "forced_flow_velocity_cm_s 150.0 cm/s exceeds training maximum 45.0 cm/s"
  ],
  "prediction": null,
  "probabilities": null,
  "nearest_experiments": [
    { "test_id": "BASS_TR_089", "distance": 1.42, "material_name": "PMMA" }
  ],
  "explanation": "Scenario is outside the verified experimental envelope of 145 NASA flight tests. Extrapolation refused."
}
```

---

## 7. Verification & Automated Testing Suite

All modules are covered by 68 automated unit, integration, and red-team tests:

```bash
# Activate virtual environment
source .venv/bin/activate

# Execute complete test suite
pytest tests/ -v
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

**Result:** `68 passed in 6.95s` (100% passing).

---

## 8. System Boundaries & Known Limitations

1. **Sample Size & Material Concentration:**
   - The database contains 145 discrete tests, heavily concentrated in Polymethyl Methacrylate (PMMA, 92 tests, 63.4%) and thin fabrics.
   - Materials not present in historical spaceflight records (e.g., Kapton, Silicone, Titanium) trigger immediate refusal.
2. **Atmospheric & Flow Limits:**
   - Valid only for oxygen concentrations between **15.0% and 34.0% O₂**, pressures between **56.5 and 101.3 kPa**, and forced flows between **0 and 45.0 cm/s**.
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
