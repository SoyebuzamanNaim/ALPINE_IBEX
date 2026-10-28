# CHALLENGE BRIEF & BUILD SPEC — #08 "Flame in Freefall"

> **Read this before Phase 01.** It is the authoritative product spec for FLARE-X.
> Phase files 01–15 explain *how* to build. This file defines *what* is built and *how it is judged*.
> If a phase file conflicts with this brief, follow this brief and log the conflict in `reports/`.

| Field | Value |
|---|---|
| Challenge | #08 — Flame in Freefall |
| Theme | AI & microgravity fire safety |
| Difficulty | Advanced (domain) / Intermediate (build) |
| Format | 48-hour plan |
| License | Apache-2.0, public repository |

> [!IMPORTANT]
> **Where this text comes from.** Section 1 is the challenge statement. Sections 2–10 are build guidance
> (a plan, judging hints and an architecture). In `docs/REQUIREMENTS.md` (Phase 01), list Section 1 as
> **challenge requirements**. List Sections 2–10 as **adopted design decisions**. Never call guidance
> "NASA-required".

---

## 1. What the challenge asks

Use AI on decades of microgravity combustion research to produce fire-safety insight for spacecraft.

Fire behaves differently without buoyancy:
- flames become spherical,
- flames spread slowly,
- flames can survive in conditions that would put them out on Earth.

---

## 2. The build: a flammability explorer

The user sets:
- **oxygen concentration** (`oxygen_pct`, % by volume)
- **pressure** (`pressure_kpa`, kPa)
- **flow velocity** (`flow_cm_s`, cm/s, the imposed opposed/concurrent flow)
- **material** (categorical; only materials present in the training table)

A model trained on **published microgravity combustion results** predicts the **flame-spread regime**.
An **explanation layer** cites the real experiments behind each prediction, with report identifiers.

### Killer demo (must work live)

1. Material = PMMA (or whichever material has the densest data), pressure and flow fixed in range.
2. Slide oxygen from **21 % down to 17 %**.
3. The predicted class **crosses a regime boundary**.
4. The explanation names the **real experiments on each side of that boundary**, with their **report IDs** and clickable source URLs.

> [!WARNING]
> Do not force this demo. If the real data puts the boundary somewhere other than 17–21 % O₂,
> or puts no boundary there, demo the boundary the data actually supports and say why.
> Never tune data, labels or the model to make a scripted demo work.

---

## 3. Where the points are (judging)

| Opportunity | Trap |
|---|---|
| A **trained model + retrieval over real NASA reports** scores well on **Creativity** and **Relevance**. | A **chat interface over some PDFs** scores about **5 on Validity**. |

So the product must visibly show:
1. **The training data**: the actual table, browsable in the UI and committed to the repo.
2. **The features**: exactly which inputs the model uses.
3. **An honest accuracy figure**: cross-validated, with a confusion matrix and a naive baseline beside it.

---

## 4. Hard safety rule: never extrapolate silently

If the requested conditions are outside the range of the training data, the interface **must say so and refuse to predict**.

> A fire-safety tool that quietly guesses is worse than no tool, and a judge will ask.

Rules:
- `in_training_range = false` → `prediction = null`, `probabilities = null`.
- Return the explanation: *"Requested conditions are outside the published experimental envelope."* Name the offending variable(s), the requested value and the training min/max.
- Still return the nearest real experiments, so the user can see where data does exist.
- A material not in the training set counts as out of range.
- The UI must look clearly different for refusals (no probability bar, a warning state).

Minimum guard = per-feature min/max of the training data (required).
Recommended extra = per-material min/max, plus a kNN-distance "sparse region" warning (see Phase 07). Extras may add warnings. They may never loosen the min/max refusal.

---

## 5. Data

### 5.1 Sources

| Source | Use |
|---|---|
| **NTRS** (NASA Technical Reports Server, `ntrs.nasa.gov`) | Primary source. Microgravity combustion reports, including the **FLEX** and **SoFIE** experiment families. PDFs with citable IDs (`https://ntrs.nasa.gov/citations/<id>`). |
| **NASA OSDR** (Open Science Data Repository) | Spaceflight experiment records and metadata. |
| **NASA Glenn physical sciences resources** | Combustion experiment documentation and imagery. |

Also cross-check with the investigations listed in Phase 02 (BASS, BASS-II, SAFFIRE, ACME, etc.).
Every `report_id` must resolve to a real NTRS/OSDR record. Verify each URL. Never construct IDs.

### 5.2 Experiment table: `cache/experiments.parquet`

One row per published microgravity combustion test condition.

| Column | Type | Notes |
|---|---|---|
| `oxygen_pct` | float | % O₂ by volume |
| `pressure_kpa` | float | Convert from psia/atm/bar when needed; keep the original value + unit in provenance columns |
| `flow_cm_s` | float | Imposed flow velocity; record direction (opposed/concurrent) in `flow_direction` |
| `material` | category | Normalised name (e.g. `PMMA`); keep the raw name too |
| `sample_geometry` | category | e.g. thin sheet, thick slab, rod, sphere; plus thickness/diameter where reported |
| `outcome` | category | Flame-spread regime label (see 5.3) |
| `report_id` | string | NTRS/OSDR identifier |
| `source_url` | string | Resolvable URL |
| provenance cols | — | `source_page`/`table`/`figure`, `extraction_method`, `extraction_notes`, `gravity_env` (ISS, drop tower, parabolic flight, sounding rocket) |

Also commit:
- `cache/report_corpus/`: per report, the title, abstract, ID, URL and (if licensed) full text
- `docs/DATA_DICTIONARY.md` and `docs/LABELING_PROTOCOL.md`

### 5.3 Outcome classes

Default target: `no_spread` | `marginal_spread` | `spread`.
Write down the exact rule that maps each report's wording ("extinguished", "limiting oxygen", "steady spread", "flickering/near-limit"…) to a class. If the literature cannot support three classes, use fewer, and document that.
Flag any row whose label needed interpretation.

### 5.4 Pre-build (must exist before the 48-hour clock)

- [ ] Extracted experiment table (`cache/experiments.parquet`)
- [ ] Report corpus with identifiers (`cache/report_corpus/`)
- [ ] Trained model artifact committed

Data extraction is the slow part. Do it first.
Follow the competition-compliance boundary in `00_READ_ME_FIRST.md` about what may be built before the event.

---

## 6. Model: `src/compute/model.py`

- Train a **small gradient-boosting classifier** for the flame-spread regime.
  - Features: `oxygen_pct`, `pressure_kpa`, `flow_cm_s`, `material` (one-hot or native categorical).
  - Add `sample_geometry` as a feature only if the data justifies it and CV improves. Otherwise use it for filtering and display.
- Compare against a majority-class baseline and logistic regression (Phase 05 modelling order).
- **Honest cross-validation:**
  - Stratified k-fold, **grouped by `report_id`** (`StratifiedGroupKFold`), so rows from one report never sit in both train and test. This is the headline number.
  - Also report plain stratified k-fold, labelled as optimistic.
  - Report accuracy, balanced accuracy, macro-F1, per-class recall, a **confusion matrix**, and the majority-class baseline.
  - Fixed random seed. Results go in `reports/BASELINE_RESULTS.md` and `models/metrics.json`.
- **Save the artifact to the repo** (`models/flame_spread_gb.joblib`) with `models/model_meta.json`, containing:
  - `type`, `n_train`, `cv_accuracy`, `cv_scheme`, `features`, `classes`, `trained_at`, `dataset_sha256`
  - `training_range`: min and max of **every numeric feature**, plus the allowed `material` values (and per-material ranges if computed)

If the honest accuracy is weak, report it as it is. A low, honest number beats a high, leaky one.

---

## 7. API (FastAPI)

### `POST /predict`

Returns class, class probabilities, model metadata (including `n_train` and `cv_accuracy`), `in_training_range`, and the **3 nearest real experiments** by feature distance. Numeric features are scaled by training range. A material mismatch gets a large penalty.

Response shape (field names are the contract):

```json
{
  "inputs": {"oxygen_pct": 17.0, "pressure_kpa": 101.3,
             "flow_cm_s": 5.0, "material": "PMMA"},
  "in_training_range": true,
  "out_of_range_reasons": [],
  "prediction": "marginal_spread",
  "probabilities": {"no_spread": 0.28, "marginal_spread": 0.57, "spread": 0.15},
  "model": {"type": "gradient_boosting", "n_train": 184,
            "cv_accuracy": 0.79, "cv_scheme": "StratifiedGroupKFold(k=5, group=report_id)",
            "features": ["oxygen_pct", "pressure_kpa", "flow_cm_s", "material"]},
  "nearest_experiments": [
    {"report_id": "NTRS 20205008xxx", "oxygen_pct": 17.5, "pressure_kpa": 101.3,
     "flow_cm_s": 5.0, "material": "PMMA", "outcome": "marginal_spread",
     "distance": 0.04,
     "source_url": "https://ntrs.nasa.gov/citations/20205008xxx"}
  ],
  "explanation": "…"
}
```

> [!CAUTION]
> Every number above (`184`, `0.79`, `0.57`, `20205008xxx`, …) is a **format example only**.
> Real responses must come from the trained artifact and the real table. Hard-coding these values anywhere
> in code, fixtures shown in the UI, or docs presented as results is a stop condition.

When `in_training_range` is `false`:

```json
{
  "inputs": {"oxygen_pct": 40.0, "pressure_kpa": 101.3, "flow_cm_s": 5.0, "material": "PMMA"},
  "in_training_range": false,
  "out_of_range_reasons": [
    {"feature": "oxygen_pct", "value": 40.0, "train_min": "<real>", "train_max": "<real>"}
  ],
  "prediction": null,
  "probabilities": null,
  "model": {"...": "same metadata"},
  "nearest_experiments": ["… still returned …"],
  "explanation": "Requested conditions are outside the published experimental envelope. No prediction is made."
}
```

Also expose: `GET /health`, `GET /experiments` (the full training table), `GET /model` (metadata + metrics + confusion matrix), `GET /boundary` (decision-surface grid for the plot).

---

## 8. Explanation layer (LLM): bounded

The language model **writes the explanation only**. Its inputs are:
- the prediction object, and
- the retrieved report abstracts for `nearest_experiments`.

Rules:
1. It **never predicts**. It never changes or overrides the class or probabilities.
2. It **never states a number that is absent from the prediction object.** Enforce this in code: pull every number out of the generated text and reject it if any number is not in the object. Do the same for report IDs not in `nearest_experiments`.
3. It cites only `report_id`s that appear in the object.
4. If the LLM is unavailable or fails the check, fall back to a deterministic template explanation.
5. For the boundary demo, name the nearest experiments on **each side** of the class boundary along the slider axis.

Retrieval: structured nearest-neighbour search over the table first, then text retrieval over the corpus (abstracts, or full text if time allows) to pull the supporting passages.

---

## 9. Frontend

- **Sliders** for oxygen, pressure and flow. Slider limits = training range, with an explicit option to go beyond it, which then triggers the refusal state. **Material selector** (training materials only).
- **Probability bar** for the 3 classes, with model type, `n_train` and `cv_accuracy` shown beside it.
- **2-D decision-boundary plot** (default: oxygen × flow at the current pressure and material).
  - Predicted-class regions shaded. **Real experiments overlaid as points**, coloured by observed outcome.
  - The user's current point is marked, and the region outside the training range is hatched.
  - A label says which variables are held fixed (the plot is a slice).
- **Nearest-experiments panel**: report ID, conditions, observed outcome, distance, and a **clickable citation**.
- **Explanation panel**: clearly labelled "AI-written explanation, from the model output and cited reports".
- **Data & model page**: the training table, features, CV scheme, accuracy, confusion matrix and baseline.
- **Operator safety framing**: plain-language meaning for a spacecraft operator, uncertainty display, and the out-of-range warning.
- Observed data and predictions must look different. Always show units.

---

## 10. Architecture

```text
NTRS reports + OSDR records
            │ (pre-event extraction)
            ▼
   cache/experiments.parquet ──► report corpus + index
            │                          │
            ▼                          │
  src/compute/model.py                 │
  train · cross-validate · save        │
            │                          │
            ▼                          ▼
     FastAPI /predict           retrieval: nearest
            │                   real experiments
            └────────┬─────────────────┘
                     ▼
            slider interface
   prediction · probabilities · range guard
                     │
                     ▼
        explanation citing report IDs
```

Path reconciliation with the master repo layout: `cache/` and `src/compute/` are **required** paths from this brief.
They sit alongside `data/` and `src/models/`. `src/compute/model.py` may import shared code from `src/models/`, but it must be the entry point for training.

---

## 11. 48-hour plan

| Slot | Work |
|---|---|
| **Before the event** | Gather reports from NTRS + OSDR, extract the tabular dataset, commit the table, corpus and trained model artifact. |
| **Day 1 morning** | Feature engineering + baseline classifier with honest cross-validation. Report the accuracy you actually get. |
| **Day 1 afternoon** | Serve the model, build the slider interface, show the decision boundary. |
| **Day 1 evening** | Retrieval over the report corpus, so each prediction links to the nearest real experiments. **Record a demo by 18:30.** |
| **Day 2 morning** | Uncertainty display, out-of-range warning, safety framing for a spacecraft operator. |
| **Day 2 noon** | Freeze, record, submit. |

### Cut in this order (if behind schedule)

1. Classification only; drop regression.
2. Fixed presets instead of free sliders.
3. Retrieval over titles instead of full text.

Never cut: the range guard, the honest accuracy figure, or real citations.

---

## 12. Acceptance checklist (Definition of Done)

- [ ] `cache/experiments.parquet` committed; every row has a resolvable `report_id` + `source_url`
- [ ] Report corpus committed with identifiers
- [ ] `src/compute/model.py` trains, cross-validates (grouped + stratified) and saves the artifact + metadata + training range
- [ ] Confusion matrix and majority-class baseline published beside the accuracy
- [ ] `POST /predict` matches the Section 7 contract; out-of-range → `prediction: null` with reasons
- [ ] Explanation check rejects any number or report ID not in the prediction object (unit-tested)
- [ ] UI: sliders, material selector, probability bar, decision-boundary plot with real points, nearest-experiment citations
- [ ] Oxygen-sweep demo shows a real boundary with experiments cited on both sides (or an honest note that the data does not support one there)
- [ ] No hard-coded example numbers anywhere in the product
- [ ] Apache-2.0 `LICENSE` file; public repo; README with data sources, model card and limitations

## 13. Phase mapping

| Brief section | Phase file |
|---|---|
| 1–3 requirements & judging | `02_PHASE_01_REQUIREMENTS_AND_SCOPE.md` |
| 5 data sources & table | `03`, `04`, `05` (Phases 02–04) |
| 6 model | `06_PHASE_05_BASELINE_MODELS.md` |
| 8 retrieval & citations | `07_PHASE_06_RETRIEVAL_ENGINE.md` |
| 4 range guard | `08_PHASE_07_EXPERIMENTAL_ENVELOPE.md` |
| 2 oxygen-sweep demo | `09_PHASE_08_COUNTERFACTUAL_ENGINE.md` |
| 8 explanation layer | `10_PHASE_09_AGENTIC_SYSTEM.md` (Explanation Composer) |
| 7 API | `11_PHASE_10_BACKEND_API.md` |
| 9 frontend | `12_PHASE_11_FRONTEND.md` |
| 11 plan, 12 checklist | `15_PHASE_14_DEMO_AND_VIDEO_ASSETS.md`, `17_AUTONOMOUS_VALIDATION_GATE.md` |
