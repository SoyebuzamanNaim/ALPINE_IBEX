# Backend API Specification (Phase 10)

> **Document Status:** Authoritative OpenAPI / REST specification for FLARE-X backend services.
> **Base URL:** `http://localhost:8000`

## 1. Architecture & Security Invariants
- Built with FastAPI, Pydantic, and Uvicorn.
- Strict input validation on all variables (`oxygen_pct`: [0, 100], `pressure_kpa`: [0, 200], `flow_cm_s`: [0, 100], `material`: string).
- CORS enabled (`*`) to support decoupled frontend web applications.
- Zero data fabrication: all metrics, experiments, and model scores reflect persisted artifacts.

---

## 2. Endpoint Index

| Method | Path | Summary | Contract Origin |
|---|---|---|---|
| `GET` | `/health` | Service health, dataset SHA-256, model readiness | Operational |
| `POST` | `/predict` | Regime prediction with envelope guard and 3 nearest citations | **Challenge Brief §7** |
| `GET` | `/experiments` | Full microgravity training table (with filtering & pagination) | Challenge Brief §7 |
| `GET` | `/model` | Model card, CV score, confusion matrix, and training ranges | Challenge Brief §7 |
| `GET` | `/boundary` | 2-D decision boundary grid slice with overlaid flight points | Challenge Brief §9 |
| `POST` | `/counterfactual` | Single-variable perturbation with prediction and evidence deltas | Phase 08 |
| `POST` | `/sweep` | 1-D continuous sweep with regime boundary detection | Phase 08 / Brief §2 |
| `POST` | `/scenario/parse` | Natural language scenario interpreter | Phase 09 |
| `GET` | `/datasets` | Catalog of 23 audited NASA combustion investigations | Phase 02 |
| `GET` | `/sources/{id}` | Metadata and abstract for a specific NASA NTRS report | Phase 04 |

---

## 3. Detailed Specifications

### 3.1 `POST /predict` (The Core Evaluation Contract)

#### Request Body
```json
{
  "oxygen_pct": 21.0,
  "pressure_kpa": 101.3,
  "flow_cm_s": 5.0,
  "material": "PMMA"
}
```

#### In-Domain Response (`200 OK`)
```json
{
  "inputs": {
    "oxygen_pct": 21.0,
    "pressure_kpa": 101.3,
    "flow_cm_s": 5.0,
    "material": "PMMA"
  },
  "in_training_range": true,
  "out_of_range_reasons": [],
  "prediction": "spread",
  "probabilities": {
    "no_spread": 0.008,
    "marginal_spread": 0.015,
    "spread": 0.977
  },
  "model": {
    "type": "gradient_boosting",
    "n_train": 145,
    "cv_accuracy": 0.7931,
    "cv_scheme": "StratifiedGroupKFold(k=5, group=report_id)",
    "features": ["oxygen_pct", "pressure_kpa", "flow_cm_s", "material"]
  },
  "nearest_experiments": [
    {
      "experiment_id": "EXP_BASS_001",
      "report_id": "20160010041",
      "oxygen_pct": 21.0,
      "pressure_kpa": 101.3,
      "flow_cm_s": 5.0,
      "material": "PMMA",
      "sample_thickness_mm": 1.2,
      "outcome": "spread",
      "distance": 0.012,
      "source_url": "https://ntrs.nasa.gov/citations/20160010041"
    }
  ],
  "explanation": "Under microgravity conditions without natural buoyant convection, PMMA at 21.0% O2, 101.3 kPa, and 5.0 cm/s ventilation is predicted to exhibit sustained flame spread with a probability of 97.7%...",
  "status": "in_domain",
  "sparse_region_warning": false,
  "warning_message": null
}
```

#### Out-of-Domain Refusal Response (`200 OK`)
```json
{
  "inputs": {
    "oxygen_pct": 45.0,
    "pressure_kpa": 101.3,
    "flow_cm_s": 5.0,
    "material": "PMMA"
  },
  "in_training_range": false,
  "out_of_range_reasons": [
    {
      "feature": "oxygen_pct",
      "value": 45.0,
      "train_min": 15.0,
      "train_max": 34.0,
      "reason": "Oxygen concentration 45.0% is outside global training envelope [15.0%, 34.0%]."
    }
  ],
  "prediction": null,
  "probabilities": null,
  "model": { ... },
  "nearest_experiments": [ ... ],
  "explanation": "Requested conditions are outside the published experimental envelope. No prediction is made."
}
```

---

### 3.2 `GET /boundary`

Computes a 2-D slice of the flammability space holding pressure constant, returning shaded class contours and overlaying real experiments.

#### Query Parameters
- `material`: string (default: `"PMMA"`)
- `pressure_kpa`: float (default: `101.3`)
- `o2_steps`: integer (default: `25`, 10–50)
- `flow_steps`: integer (default: `25`, 10–50)

#### Response
```json
{
  "material": "PMMA",
  "fixed_pressure_kpa": 101.3,
  "oxygen_range": [15.5, 34.0],
  "flow_range": [0.0, 35.0],
  "oxygen_grid": [15.5, 16.27, ..., 34.0],
  "flow_grid": [0.0, 1.45, ..., 35.0],
  "grid_predictions": [["no_spread", "marginal_spread", ...]],
  "grid_spread_probabilities": [[0.02, 0.28, ...]],
  "real_experiments": [
    {
      "experiment_id": "EXP_BASS_001",
      "report_id": "20160010041",
      "oxygen_pct": 21.0,
      "flow_cm_s": 5.0,
      "pressure_kpa": 101.3,
      "outcome": "spread"
    }
  ]
}
```
