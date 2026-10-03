# Agent Interface Contracts (Phase 09)

> **Document Status:** Authoritative JSON schema specifications for each specialized agent.

## 1. Scenario Interpreter Contract

### Input
- `str` (natural language query) OR `dict` (structured JSON payload)

### Output
```json
{
  "parsed_scenario": {
    "oxygen_pct": 21.0,
    "pressure_kpa": 101.3,
    "flow_cm_s": 5.0,
    "material": "PMMA"
  },
  "is_valid": true,
  "ambiguities": [],
  "source_type": "natural_language"
}
```

---

## 2. Envelope Guard Contract

### Input
- `oxygen_pct`: float
- `pressure_kpa`: float
- `flow_cm_s`: float
- `material`: str

### Output (In-Domain)
```json
{
  "in_training_range": true,
  "status": "in_domain",
  "out_of_range_reasons": [],
  "sparse_region_warning": false,
  "knn_mean_distance": 0.0841,
  "nearest_experiments": [...],
  "warning_message": null,
  "explanation": null
}
```

### Output (Out-of-Domain Refusal)
```json
{
  "in_training_range": false,
  "status": "extrapolation",
  "out_of_range_reasons": [
    {
      "feature": "oxygen_pct",
      "value": 45.0,
      "train_min": 15.0,
      "train_max": 34.0,
      "reason": "Oxygen concentration 45.0% is outside global training envelope [15.0%, 34.0%]."
    }
  ],
  "nearest_experiments": [...],
  "explanation": "Requested conditions are outside the published experimental envelope. No prediction is made."
}
```

---

## 3. Model Router Contract

### Input
- `oxygen_pct`: float, `pressure_kpa`: float, `flow_cm_s`: float, `material`: str

### Output
```json
{
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
  }
}
```

---

## 4. Evidence Retriever Contract

### Input
- `oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `material`, `k`: int

### Output
```json
{
  "query": {"oxygen_pct": 21.0, "pressure_kpa": 101.3, "flow_cm_s": 5.0, "material": "PMMA"},
  "nearest_experiments": [
    {
      "experiment_id": "EXP_BASS_001",
      "report_id": "NASA/TM-2016-219077",
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
  "supporting_passages": [...]
}
```

---

## 5. Evidence Auditor Contract

### Input
- `explanation_text`: str
- `prediction_obj`: dict

### Output
```json
{
  "is_valid": true,
  "hallucinated_numbers": [],
  "invalid_citations": [],
  "reasons": "Explanation strictly grounded in prediction object."
}
```

---

## 6. End-to-End Orchestrated Response Contract

Matches Section 7 API contract:
```json
{
  "inputs": {
    "oxygen_pct": 21.0,
    "pressure_kpa": 101.3,
    "flow_cm_s": 5.0,
    "material": "PMMA"
  },
  "in_training_range": true,
  "status": "in_domain",
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
  "nearest_experiments": [...],
  "explanation": "...",
  "audit_passed": true,
  "state_history": ["INIT", "INTERPRETING", "ENVELOPE_CHECK", "PREDICTING", "RETRIEVING", "COMPOSING", "AUDITING", "FINALIZED"]
}
```
