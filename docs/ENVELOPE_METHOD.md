# Experimental Envelope Guard Specification (Phase 07)

> **Document Status:** Authoritative specification for domain validation, extrapolation refusal, and density warnings.

## 1. Safety Rationale

In spacecraft fire safety, a predictive system that silently extrapolates into unverified atmospheric or flow regimes
presents an unacceptable hazard. If an astronaut or safety analyst enters 40% O2 or a material never evaluated in
microgravity, the system must **refuse to predict** (`prediction: null`, `probabilities: null`) and clearly explain
why, while returning the nearest published test points.

## 2. Multi-Tier Guard Architecture

The FLARE-X envelope guard implements four defensive tiers:

### Tier 1: Strict Min/Max Refusal (Non-Negotiable)
- **Global Numerical Bounds:** Read from the current model metadata, which is
  generated from `cache/experiments.parquet` during training.
- **Categorical Material Restriction:**
  - Allowed materials are read from the current model metadata.
  - Unseen materials (e.g. Titanium, Teflon, Kapton) immediately trigger `unsupported_category` refusal.
- **Per-Material Bounding Box:** Each material has its own observed min/max
  values. A request beyond any of these ranges is refused.

### Tier 2: Joint Experimental Domain
- Within a material's numeric ranges, oxygen, pressure, and flow must also lie
  in the convex hull of that material's observed combinations. A point inside
  all three ranges but outside this hull returns `joint_extrapolation` with a
  `joint_domain` reason and the nearest source observations.
- For materials whose observations lie on a plane or line, the request must
  remain in that lower-dimensional span and its convex hull. A single observed
  point supports only that exact combination. Convex support is a necessary
  condition for inference, not proof of local experimental density.

### Tier 3: Boundary Proximity Detection
- A query is designated `boundary` if any numeric feature is within 5% of its minimum or maximum training limit, or
  if conditions fall within the near-extinction transitional zone (e.g. 16.0–17.5% O2 for PMMA).

### Tier 4: kNN Density & Sparse Region Warning
- Even within the bounding box, high-dimensional space can contain vast empty regions.
- The guard computes the average normalized Euclidean distance to the 3 nearest real training points for that material ($d_{3NN}$).
- If $d_{3NN} > 0.35$, the prediction is flagged with a `sparse_region_warning`, alerting the operator that local experimental support is thin.

---

## 3. Refusal Contract Shape

When `in_training_range` is `false`:
```json
{
  "inputs": {"oxygen_pct": 40.0, "pressure_kpa": 101.3, "flow_cm_s": 5.0, "material": "PMMA"},
  "in_training_range": false,
  "status": "extrapolation",
  "out_of_range_reasons": [
    {
      "feature": "oxygen_pct",
      "value": 40.0,
      "train_min": 15.5,
      "train_max": 34.0,
      "reason": "Oxygen concentration 40.0% is outside the published experimental envelope [15.5%, 34.0%]."
    }
  ],
  "prediction": null,
  "probabilities": null,
  "nearest_experiments": [...],
  "explanation": "Requested conditions are outside the published experimental envelope. No prediction is made."
}
```
