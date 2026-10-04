# Phase 12 — NASA Evidence & Provenance System: FLARE-X

> **Status:** ✅ COMPLETE  
> **Challenge:** Flame in Freefall (NASA Space Apps Challenge 2026)  
> **Core Mandate:** Provenance as first-class, machine-readable data. Every scientific claim, model prediction, and interpretation must have an unbroken, auditable lineage back to authentic NASA Physical Science Informatics (PSI) DOIs, experimental tables, run locators, and file hashes.

---

## Executive Summary & Guiding Principle

Phase 12 is where FLARE-X stops being merely “grounded in NASA data” and becomes capable of answering a harder question:
> **“Exactly which NASA experiment, file, measurement, report, model run, and reasoning step supports this conclusion?”**

That chain must survive all the way from the raw NASA source to the sentence shown in the UI. Otherwise “evidence-grounded AI” degenerates into the ancient scientific method of *“trust me, I saw it in a PDF somewhere.”*

---

## 12.1 The Two Provenance Lineages

FLARE-X treats provenance as structured data, enforcing two mandatory lineages:

### 1. Empirical Observation Lineage
```
USER RESULT ──► CLAIM ──► EVIDENCE ASSERTION ──► EXPERIMENT / RUN ──► NASA SOURCE FILE ──► NASA INVESTIGATION ──► PSI DOI
```

### 2. Model-Derived Prediction Lineage
```
MODEL CLAIM ──► MODEL RUN ──► MODEL VERSION ──► TRAINING DATA MANIFEST ──► NASA EXPERIMENTS ──► NASA SOURCES
```

---

## 12.2 Five Discrete Provenance Layers

FLARE-X strictly distinguishes five epistemic layers rather than collapsing everything into generic "citations":

| Layer | Definition | Concrete Example |
| :--- | :--- | :--- |
| **1. Source** | Raw or normalized NASA file / repository entry | NASA PSI file, NTRS report, experimental table |
| **2. Experiment** | Specific physical microgravity burn | BASS-II Test 31, FLEX Run 14, SPICE Flame 204 |
| **3. Observation** | Discrete physical measurement recorded in test | $O_2 = 18.0\%$, $u = 20\text{ cm/s}$, flame extinguished |
| **4. Derived Result** | Deterministic calculation or model inference | Gradient Boosting regime prediction, $P_{O_2}$, $d_{\text{kNN}}$ |
| **5. Interpretation** | Synthesized explanation of evidence & model | LLM summary explaining why geometry reduces comparability |

*Rule:* A model prediction is not a NASA observation. An LLM explanation is not a model result. And a model result is never permitted to quietly transform into *"NASA found that..."*.

---

## 12.3–12.7 Evidence Source Authority Hierarchy

| Level | Source Authority Tier | Acceptable Use & Epistemic Authority |
| :---: | :--- | :--- |
| **Level 1** | **Direct Experimental Evidence** | NASA experimental tables, raw sensor logs, high-speed video frames, analyzed CSVs. **Highest authority** for physical ground truth. |
| **Level 2** | **NASA Experiment Documentation** | Science Requirements Documents (SRD), engineering descriptions, metadata catalogs, PI test logs. Authority for test setup, sensors, and geometry. |
| **Level 3** | **NASA Technical Reports & Papers** | NTRS technical memorandums, AIAA/Combustion Institute conference papers, peer-reviewed journals. Authority for derived kinetics and author interpretations. |
| **Level 4** | **FLARE-X Derived Analysis** | Quantitative model predictions, nearest-neighbor scores, conformal intervals, domain envelope flags. **Must be tagged "FLARE-X-derived", never "NASA measured".** |
| **Level 5** | **AI Synthesis** | Synthesizer narrative combining Levels 1–4. **Lowest evidentiary authority.** Contributes linguistic clarity; cannot upgrade evidence certainty. |

---

## 12.8 Canonical Evidence Object Schema

```json
{
  "evidence_id": "ev_bass2_031_o2",
  "investigation": {
    "name": "BASS-II",
    "psi_id": "PSI-25",
    "doi": "10.2514/6.2014-3677"
  },
  "experiment": {
    "experiment_id": "BASS-II-EXP-031",
    "test_id": "Test-31",
    "run_id": "Run-01"
  },
  "source": {
    "source_type": "EXPERIMENTAL_TABLE",
    "file_name": "BASS-II_Test_Data_Summary.csv",
    "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "source_reference": "NASA PSI Accession 25",
    "license": "NASA Open Data / Public Domain"
  },
  "locator": {
    "page": null,
    "row": 31,
    "column": "oxygen_percent",
    "timestamp_start": null,
    "timestamp_end": null
  },
  "observation": {
    "variable": "oxygen_fraction",
    "value_original": 18.0,
    "unit_original": "%",
    "value_canonical": 0.18,
    "unit_canonical": "fraction"
  },
  "provenance": {
    "measured_or_derived": "MEASURED",
    "extraction_method": "STRUCTURED_INGESTION",
    "verification_status": "VERIFIED"
  }
}
```

---

## 12.9 Exact-Source Locators

A broad DOI by itself is insufficient. For a 140-page technical memorandum, citing only the report title is practically uninspectable. FLARE-X requires precise locators:

| Medium | Required Locator Fields |
| :--- | :--- |
| **Structured Tables** | `sheet_name`, `row_index`, `column_name` |
| **Technical Reports** | `page_number`, `section_number`, `figure_table_id` |
| **Time-Series Sensor Logs** | `channel_name`, `sample_start_idx`, `sample_end_idx`, `time_interval_sec` |
| **High-Speed Video** | `video_file_name`, `start_timestamp`, `end_timestamp`, `fps` |
| **Optical Imagery** | `image_file_name`, `frame_number`, `sensor_id` |

---

## 12.10 Raw-Source Immutability (Bronze Layer)

* Raw NASA downloads remain untouched in `data/raw/`.
* Every raw file is indexed with:
  - Original filename
  - NASA investigation ID
  - Download URL / PSI accession reference
  - File byte size
  - Cryptographic **SHA-256 hash**
  - Ingestion timestamp
* Invariant: If normalized data shows $O_2 = 0.18$, it maps deterministically to a verified byte slice in a hashed file.

---

## 12.11 Dataset Manifests

Every NASA investigation has an authoritative manifest in `data/metadata/`:
* `manifests/psi_25_bassii.json`
* `manifests/psi_69_flex.json`
* `manifests/psi_98_saffire.json`
* `manifests/psi_102_same.json`
* `manifests/psi_107_spice.json`

Manifests record dataset versions, file checksums, table schemas, parser statuses, and normalization rules.

---

## 12.12 Observation Lineage & Canonical Conversions

Original reported measurements are never overwritten:
```
airflow_original = 20.0
airflow_original_unit = "cm/s"
airflow_canonical = 0.20
airflow_canonical_unit = "m/s"
```
Unit standardization never destroys the empirical audit trail.

---

## 12.13 Derivation Records for Physical Features

When FLARE-X computes derived physical features (e.g., oxygen partial pressure):
```json
{
  "variable": "oxygen_partial_pressure",
  "status": "DERIVED",
  "formula": "oxygen_fraction * total_pressure_kpa",
  "input_evidence_ids": ["ev_o2_031", "ev_press_031"],
  "code_version": "git:a1b2c3d",
  "value": 18.234,
  "unit": "kPa"
}
```

---

## 12.14 Model Run Object Schema

Every inference is permanently serialized:
```json
{
  "model_run_id": "run_20261004_1142_bass",
  "model_id": "flame_spread_gb",
  "model_version": "1.0",
  "inputs": {
    "material": "PMMA",
    "oxygen_pct": 18.0,
    "pressure_kpa": 101.3,
    "flow_cm_s": 20.0
  },
  "input_evidence_ids": ["ev_pmma_spec", "ev_bass_flow"],
  "prediction": {
    "class": "spread",
    "calibrated_probabilities": {
      "no_spread": 0.12,
      "marginal_spread": 0.21,
      "spread": 0.67
    }
  },
  "domain": {
    "status": "INSIDE"
  },
  "model_card": "models/model_meta.json",
  "training_manifest": "data/metadata/source_manifest.csv",
  "code_commit": "git:d395abc",
  "timestamp": "2026-10-04T23:40:00Z"
}
```

---

## 12.15 Claim Object Schema (Claim-Level Provenance)

Every factual or analytical sentence generated for display is encapsulated in a Claim Object:
```json
{
  "claim_id": "clm_089",
  "text": "The model predicts sustained flame propagation under 18% oxygen and 20 cm/s opposed flow.",
  "claim_type": "MODEL_INFERENCE",
  "support": {
    "evidence_ids": ["ev_bass2_031_o2", "ev_bass2_031_flow"],
    "model_run_ids": ["run_20261004_1142_bass"]
  },
  "domain_status": "INSIDE",
  "strength": "MODERATE",
  "audit_status": "APPROVED"
}
```

---

## 12.16 Four Claim Types

1. **`DIRECT_OBSERVATION`**: What occurred in an empirical flight test (*"BASS-II Test 31 sustained flame propagation across a 10 cm PMMA slab"*).
2. **`MODEL_INFERENCE`**: Output of an evaluated machine learning model (*"FLARE-X predicts an extinction-leaning regime with 67% probability"*).
3. **`SYNTHESIZED_INTERPRETATION`**: Synthesis linking multiple experiments (*"Retrieved tests collectively suggest that opposed airflow below 10 cm/s accelerates extinction"*).
4. **`LIMITATION`**: Stated bounds or mismatches (*"Historical flight tests used flat slabs, whereas the query specifies a cylindrical rod"*).

---

## 12.17 Claim Language Governance Law

| Claim Type | Permitted Phrasing | Strictly Prohibited Phrasing |
| :--- | :--- | :--- |
| **Direct Observation** | *"NASA Experiment X recorded..."* | *"The model measured..."* |
| **Model Output** | *"FLARE-X predicts..."* | *"NASA predicts..."* or *"NASA found that the flame will..."* |
| **Synthesis** | *"Taken together, retrieved evidence suggests..."* | *"NASA has proven that..."* |
| **Limitation** | *"Direct applicability is limited by geometry differences..."* | Vague silence on hardware discrepancies |

---

## 12.18 Scientific Knowledge & Provenance Graph

```
[NASA PSI-25] ──CONTAINS──► [BASS-II Test 31] ──USES_MATERIAL──► [PMMA]
      │                              │
  SOURCE_OF                      OBSERVED
      │                              │
      ▼                              ▼
[Evidence ev_031]              [Sustained Propagation]
      │                              │
      └──────────► SUPPORTS ◄────────┘
                      │
                      ▼
               [Claim clm_089]
                      ▲
                      │
                 SUPPORTS_BY
                      │
          [Model Run run_1142_bass] ◄──INSTANCE_OF── [BASS-RG v1]
```

---

## 12.19 The "Why Should I Trust This?" Interaction

For every query result, clicking **"Why should I trust this?"** exposes:
* **Result Classification:** `MODEL_INFERENCE`
* **Model Pipeline:** `flame_spread_gb` (Trained on 145 spaceflight burns)
* **Domain Support:** `INSIDE` ($D_k = 0.082 < Q_{90}$)
* **Supporting NASA Evidence:** 8 verified flight tests
* **Top Matching Test:** BASS-II Test 31 (PMMA, $18.0\% O_2$, $20.0\text{ cm/s}$ flow)
* **Primary Source:** NASA PSI-25 (`doi:10.2514/6.2014-3677`)
* **Known Limitation:** Opposed flow geometry matches; sample thickness ($1.2\text{ mm}$ vs $2.0\text{ mm}$) differs.

---

## 12.20 Provenance Badges (UI Micro-Labels)

Every displayed claim carries an explicit visual tag:
* 🔵 `NASA OBSERVATION` (Empirical flight measurement)
* 🟣 `MODEL INFERENCE` (FLARE-X quantitative model prediction)
* 🟡 `AI SYNTHESIS` (Reasoned interpretation across multiple tests)
* ⚪ `LIMITATION` (Hardware, geometry, or scale caveat)

---

## 12.21–12.26 Evidence Strength Evaluation Hierarchy

| Evidence Strength | Empirical Criteria | Mandatory UI Language |
| :--- | :--- | :--- |
| **`STRONG`** | Direct NASA flight tests; multiple independent runs; exact material match; in-domain; zero unresolved contradictions. | *"Strong NASA flight evidence coverage"* |
| **`MODERATE`** | Relevant flight tests exist; minor parameter differences; in-domain; consistent outcomes. | *"Moderate flight evidence support"* |
| **`LIMITED`** | Nearest experiments differ substantially in flow/scale; single flight burn; boundary condition. | *"Limited evidence support (Prominent limitations apply)"* |
| **`INSUFFICIENT`** | Zero compatible tests; out-of-domain; unresolved direct contradictions; missing parameters. | *"Insufficient NASA evidence for a reliable conclusion"* |

---

## 12.27–12.28 Source Duplication Law: Independent Experiments $\neq$ Document Count

* Ten published conference papers analyzing the **same BASS-II flight burn** represent **1 physical experiment**, not 10 independent pieces of evidence.
* Evidence counting operates strictly at the level of distinct physical burns:
  $$\text{Evidence Count} = |\{ \text{test\_id}_1, \dots, \text{test\_id}_N \}|$$

---

## 12.29–12.32 Contradictory Evidence & Resolution Workflow

When two NASA flight tests under similar conditions produce opposing outcomes:

```
                  CONTRADICTION DETECTED
                            │
                            ▼
          Compare: Material, O₂, Flow, Geometry
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
[CONTEXTUAL DIFFERENCE]           [DIRECT CONFLICT]
Flow or sample scale differs      Near-identical inputs, opposing outcome
              │                           │
              └─────────────┬─────────────┘
                            ▼
           PRESERVE BOTH OBSERVATIONS IN UI
       "Evidence is mixed: Test A sustained (thick sample),
        while Test B extinguished (thin sample)."
```
*Prohibition:* Never perform arithmetic averaging on conflicting physical outcomes.

### Contradiction Taxonomies:
* `DIRECT_CONFLICT`: Identical hardware & atmosphere, opposing outcome.
* `CONTEXTUAL_DIFFERENCE`: Outcomes differ due to secondary variables (sample thickness, duct confinement).
* `MEASUREMENT_DIFFERENCE`: Optical vs. thermocouple measurement disagreement.
* `UNRESOLVED`: Disagreement cannot be explained by published records.

---

## 12.33–12.34 Source Completeness & Extraction Verification

* **Completeness:** `COMPLETE` (metadata + numerical values + outcomes + raw locator) vs. `PARTIAL` vs. `MINIMAL`.
* **Verification Status:**
  - `DIRECT_STRUCTURED`: Parsed from official NASA PSI CSV tables.
  - `VERIFIED_DOCUMENT_EXTRACTION`: Textually extracted and verified against PDF source.
  - `AUTO_EXTRACTED_UNVERIFIED`: Not eligible for training quantitative models.

---

## 12.35–12.39 Multi-Modal Provenance Specifications

* **Document RAG:** Chunks store `document_id`, `page`, `section_header`, `text_span`.
* **Scientific Tables:** Stored with headers, column units, row keys, and parent page.
* **Optical Imagery & Video:** Stored with `video_file`, `start_time`, `end_time`, and algorithm version if computer vision derived.

---

## 12.40 Complete Evidence Package Schema

```json
{
  "result_id": "res_20261004_001",
  "claims": ["clm_089", "clm_090"],
  "primary_evidence": ["ev_bass2_031_o2"],
  "supporting_evidence": ["ev_saffire_002_scale"],
  "model_runs": ["run_20261004_1142_bass"],
  "domain_status": "INSIDE",
  "contradictions": [],
  "limitations": ["Geometry mismatch: Rod vs Flat Sheet"],
  "evidence_strength": "MODERATE"
}
```

---

## 12.43–12.46 Evidence Auditor Provenance Enforcement

The Evidence Auditor scans every claim before rendering:
1. **Citation Mismatch Gate:** If a claim asserts causality (*"Airflow caused extinction"*) but cited record only measures airflow velocity $\longrightarrow$ `CITATION_MISMATCH` $\longrightarrow$ **REVISE**.
2. **Unsupported Number Gate:** If draft cites a numerical flame length or spread rate not in empirical records or model runs $\longrightarrow$ **BLOCKED**.
3. **Family Mismatch Gate:** If solid scenario evidence contains SPICE gas flames $\longrightarrow$ `FAMILY_EVIDENCE_MISMATCH` $\longrightarrow$ **REVISE**.

---

## 12.49 The Four-Signal Confidence Triad + Strength

Never collapse uncertainty into a single deceptive number. The UI surfaces:
* **Model Confidence:** $67\%$ (Calibrated classifier probability)
* **Evidence Similarity:** `HIGH` (Matching material and flow)
* **Experimental Support:** `INSIDE` (Within empirical flight bounds)
* **Evidence Strength:** `MODERATE` (3 verified flight burns)

---

## 12.62–12.63 Model vs. Evidence Disagreement Handling

If the quantitative model predicts `spread`, but the closest historical NASA flight test extinguished:
* NASA empirical observation **takes absolute precedence** as ground truth.
* UI renders an explicit **Model–Evidence Disagreement Card**:
  > *"Model predicts sustained propagation, but nearest BASS-II flight burn extinguished. Confidence downgraded to LIMITED."*

---

## 12.67–12.69 Video 1 Pitch Narration (25–30 Seconds)

> *"Every FLARE-X result carries a provenance chain. NASA observations are linked to their investigation, experiment, source file, and DOI; model predictions are linked to the exact model version and NASA training data; and AI interpretations are only permitted to reference retrieved evidence.*
> 
> *A final Evidence Auditor checks claim-by-claim support, exposing contradictions, limitations, and the clear difference between direct NASA observations and FLARE-X model inference."*

---

## 12.71 Phase 12 Locked Decisions Matrix

| Decision | Status | Rationale |
| :--- | :---: | :--- |
| **Provenance as First-Class Data** | ✅ Locked | Machine-readable lineage from UI to DOI |
| **Claim-Level Provenance** | ✅ Locked | Every sentence carries a `ClaimObject` |
| **Exact Source Locators** | ✅ Locked | Row, column, page, and video timestamp |
| **Raw File SHA-256 Checksums** | ✅ Locked | Byte-level Bronze layer immutability |
| **Dataset Manifests** | ✅ Locked | Versioned source tracking |
| **Observation vs Model Distinction** | ✅ Locked | Prohibits labeling models as "NASA measurements" |
| **Silent Contradiction Averaging** | ❌ Banned | Both opposing outcomes must be displayed |
| **Citation Mismatch Detection** | ✅ Locked | Evidence Auditor validates claim entailment |
| **Independent Experiment Counting** | ✅ Locked | Counts burns, not duplicate papers |
| **Why Should I Trust This? UI** | ✅ Locked | 1-click drilldown from claim to NASA DOI |

---

## ✅ Phase 12 Status: COMPLETE

The NASA Evidence & Provenance System is formally codified and locked.
