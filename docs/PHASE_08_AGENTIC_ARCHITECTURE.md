# Phase 8 — Agentic Architecture: FLARE-X

> **Status:** ✅ COMPLETE  
> **Challenge:** Flame in Freefall (NASA Space Apps Challenge 2026)  
> **System Architecture:** 1 Orchestrator + 7 Bounded Agents + Deterministic Scientific Services  
> **Core Principle:** Bounded Objectives, Structured Inputs, Tool Access, Verification Gates, and Typed Outputs  
> **Deliverable:** Exact responsibilities, inputs, tools, state, outputs, handoffs, failure behavior, and orchestration flow.

---

## 8.1 Final Architecture Decision

FLARE-X will use:
> **1 Orchestrator + 7 Bounded Agents + Deterministic Scientific Services**

The agents reason about what should happen next. The deterministic services execute tasks that require absolute precision:
- Database filtering
- Numerical similarity
- ML inference
- Unit conversion
- Experimental-envelope checking
- Citation and DOI lookup

*We do not let an LLM calculate scientific values that Python or database code can calculate deterministically.*

---

## 8.2 Final Agent Set & Responsibilities

| Component | Architecture Role | Primary Responsibility |
| :--- | :--- | :--- |
| **Orchestrator** | State-Machine Coordinator | Controls end-to-end workflow, branches, timeouts, and verification gates. |
| **Agent 1: Scenario Interpreter** | Natural Language & Input Agent | Converts user intent into a scientifically structured scenario object. |
| **Agent 2: Evidence Scout** | Hybrid Retrieval Agent | Finds relevant candidate NASA experiments across structured and semantic stores. |
| **Agent 3: Scientific Ranker** | Physics-Weighted Ranker | Prioritizes candidate experiments using parameter proximity and family compatibility. |
| **Agent 4: Model Router** | Dispatch & Model Manager | Selects the correct analytical model or decides if modeling is not applicable. |
| **Agent 5: Counterfactual Planner**| Scenario Perturbation Agent | Designs controlled comparison scenarios (e.g. oxygen/flow sweeps). |
| **Agent 6: Scientific Synthesizer**| Bounded Explanation Agent | Interprets ranked evidence, model results, and domain coverage into a coherent narrative. |
| **Agent 7: Evidence Auditor** | Pre-Display Verification Gate | Verifies that every number, claim, and citation is justified by NASA sources before rendering. |
| **Envelope Guard** | Deterministic Scientific Service | Validates parameters against empirical training envelopes (`INSIDE`, `NEAR_BOUNDARY`, `OUTSIDE`). |

---

## 8.3 End-to-End Orchestration Architecture

```
                         USER
                           │
                           ▼
                    ORCHESTRATOR
                           │
                           ▼
                1. Scenario Interpreter
                           │
                           ▼
                  Structured Scenario
                           │
                           ▼
                    2. Evidence Scout
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
      Structured NASA Search      Semantic Retrieval
             │                           │
             └─────────────┬─────────────┘
                           ▼
                  Candidate Evidence
                           │
                           ▼
                3. Scientific Ranker
                           │
                           ▼
                  Ranked Experiments
                           │
                     ┌─────┴─────┐
                     ▼           ▼
             4. Model Router   Envelope Guard
                     │           │
                     ▼           │
              Quantitative Model │
                     │           │
                     └─────┬─────┘
                           ▼
                 Scientific Results
                           │
                           ▼
            5. Counterfactual Planner
                    (when requested)
                           │
                           ▼
               Counterfactual Results
                           │
                           ▼
              6. Scientific Synthesizer
                           │
                           ▼
                Draft Interpretation
                           │
                           ▼
                 7. Evidence Auditor
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
              APPROVE              REJECT
                 │                   │
                 ▼                   ▼
             USER RESULT       revise / downgrade
```

---

## 8.4 The Shared State Object

Every agent reads and writes to one strictly typed, shared state object:

```json
{
  "query_id": "flx_2026_0981a",
  "user_question": "What happens to PMMA at 18% O2 under 15 cm/s ventilation?",
  "scenario": {
    "fuel_phase": "SOLID",
    "material": "PMMA",
    "oxygen_fraction": 0.18,
    "airflow_m_s": 0.15,
    "pressure_kpa": 101.3,
    "phenomenon": "FLAME_SPREAD"
  },
  "intent": { "question_type": "ANALYZE", "requested_family": "solid" },
  "candidate_experiments": [],
  "ranked_experiments": [],
  "selected_family": "solid",
  "selected_model": "BASS_REGIME_V1",
  "model_result": null,
  "domain_status": null,
  "counterfactuals": [],
  "evidence": [],
  "interpretation": null,
  "audit": { "status": "PENDING", "warnings": [] }
}
```

*This prevents agents from quietly creating parallel or inconsistent execution contexts.*

---

## 8.5 Agent Specifications & Guardrails

### 1. Scenario Interpreter
* **Mission:** Converts natural language into a structured scenario dictionary.
* **Tools:** Combustion ontology, unit parser ($\text{cm/s} \rightarrow \text{m/s}$), material synonym crosswalk, NASA terminology dictionary.
* **Verification:** Validates units and material phase. If a user states *"low oxygen"*, it stores `oxygen = qualitative_low, exact_value = unknown` rather than guessing a number.
* **Failure Behavior:** If mandatory physics are absent, sets `status: SCENARIO_PARTIAL`. If outside combustion physics entirely (e.g. nuclear fire), sets `UNSUPPORTED_DOMAIN`.

### 2. Evidence Scout
* **Mission:** Builds the candidate evidence pool via hybrid search across structured NASA databases ($O_2$, pressure, flow, geometry) and semantic text stores (NTRS reports, PSI abstracts).
* **Tools:** PostgreSQL/Parquet store, vector embeddings, PSI metadata index, DOI resolver.
* **Verification:** Every returned candidate must have an authentic NASA source, investigation key, experiment ID, and retrieval reason.
* **Failure Behavior:** If no close test exists, flags `EVIDENCE_COVERAGE = LOW` and returns the closest available tests with delta warnings.

### 3. Scientific Ranker
* **Mission:** Prioritizes retrieved evidence using physical similarity and experiment-family compatibility.
* **Scoring Formula:**
  $$\text{Relevance} = \text{Family Compatibility} + \text{Phenomenon Match} + \text{Material Match} + \text{Parameter Proximity} + \text{Geometry Match} + \text{Semantic Score}$$
* **Hard Filters:** Severe penalties applied to physical mismatches (e.g. gaseous SPICE methane penalized for solid PMMA queries).
* **Verification:** Normalized numerical distances, missing variables not treated as zero, semantic score cannot override severe physical mismatches.

### 4. Model Router
* **Mission:** Decides which specialized model to execute or determines `NO_MODEL_APPLICABLE`.
* **Routing Logic:**
  - Solid fuels + flame spread $\rightarrow$ `BASS_REGIME_V1`
  - Liquid droplets + extinction $\rightarrow$ `FLEX_EXTINCTION_V1`
  - Gaseous flames + flame length $\rightarrow$ `SPICE_FLAME_LENGTH_V1`
  - Spacecraft-scale context $\rightarrow$ `SAFFIRE_EVIDENCE_ONLY`
  - Smoke / aerosols $\rightarrow$ `SAME_SMOKE_MODULE`
* **Crucial Rule:** Model execution is performed by **deterministic Python code** (`model.predict()`), never by LLM prompting.

### 5. Experimental Envelope Guard (Deterministic Service)
* **Mission:** Evaluates parameter coverage against verified NASA flight test bounds.
* **Statuses:** `INSIDE`, `NEAR_BOUNDARY`, `PARTIAL_SUPPORT`, `OUTSIDE`, `UNKNOWN`.
* **Behavior:** If a parameter is out-of-bounds (e.g. $11\%\text{ O}_2$ when tests start at $15\%$), outputs `OUTSIDE`, suppresses model certainty, and alerts the user.

### 6. Counterfactual Planner
* **Mission:** Constructs scientifically controlled comparison scenarios (e.g., baseline $21\%\text{ O}_2$ vs. counterfactual $17\%\text{ O}_2$ holding flow and material fixed).
* **Verification:** Disallows unsupported causal claims; frames output as model and observation delta, not proof of causality.

### 7. Scientific Synthesizer & Evidence Auditor (The Dual Gate)
* **Scientific Synthesizer (LLM):** Produces structured interpretation (Finding, Supporting Evidence, Differences, Model Result, Confidence, Limitations). Every sentence is tagged internally (`DIRECT_EVIDENCE`, `MODEL_INFERENCE`, `SYNTHESIZED_INTERPRETATION`, `LIMITATION`). Restricted strictly to facts present in the state object.
* **Evidence Auditor (Deterministic Gate):** Intercepts draft before display. Validates provenance, checks numerical values against ground truth, confirms citations exist in `source_manifest.csv`, and blocks uncalibrated claims (e.g., *"92% safe"*). Outputs `APPROVED`, `APPROVED_WITH_WARNING`, `REVISE`, or `BLOCKED`.

---

## 8.6 Orchestrator State Machine & Branching

```
START ──► PARSE ──► RETRIEVE ──► RANK ──► ROUTE ──► CHECK_DOMAIN ──► MODEL
                                                                        │
RETURN ◄── AUDIT (Pass) ◄── SYNTHESIZE ◄── [COUNTERFACTUAL?] ◄─────────┘
             │ (Fail)
             ▼
           REVISE (Max 2 retries) ──► DETERMINISTIC FALLBACK
```

* **Search-Only Branch:** `Interpreter` $\rightarrow$ `Scout` $\rightarrow$ `Ranker` $\rightarrow$ `Synthesizer` $\rightarrow$ `Auditor` (Skips Model Router).
* **Prediction Branch:** Executes full pipeline including `EnvelopeGuard` and `ModelRouter`.
* **Counterfactual Branch:** Runs baseline, triggers `CounterfactualPlanner`, executes secondary pass, and synthesizes comparison.

---

## 8.7 Tool Permission & Principle of Least Privilege

| Component | Structured DB | Vector DB | Model Registry | Envelope Guard | Code Calculator | Generative LLM |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Scenario Interpreter** | — | — | — | — | ✓ | ✓ |
| **Evidence Scout** | ✓ | ✓ | — | — | — | ✓ |
| **Scientific Ranker** | ✓ | ✓ | — | — | ✓ | Optional |
| **Model Router** | ✓ | — | ✓ | ✓ (metadata) | — | ✓ |
| **Counterfactual Planner** | ✓ | — | ✓ | ✓ | ✓ | ✓ |
| **Scientific Synthesizer**| Retrieved only | Retrieved only | Results only | Result only | — | ✓ |
| **Evidence Auditor** | ✓ | ✓ | ✓ (meta) | ✓ | ✓ | ✓ |

---

## 8.8 Confidence Architecture (Tri-Partite Confidence)

FLARE-X rejects a single "AI confidence" number. Instead, it computes and exposes three independent metrics:
1. **Model Confidence:** Calibrated prediction probability (e.g. `81%` Gradient Boosting probability).
2. **Evidence Similarity:** Weighted physical closeness of retrieved flight experiments (`HIGH`, `MODERATE`, `LOW`).
3. **Domain Support:** Bounding box coverage status (`INSIDE`, `NEAR_BOUNDARY`, `OUTSIDE`).

---

## 8.9 Video 1 Script Lock: The Agentic Pitch (October 7)

For the October 7 prescreening pitch, we summarize the agentic workflow with technical authority:

> *"FLARE-X uses a bounded agentic workflow rather than a single chatbot. One agent interprets the fire scenario, another retrieves NASA evidence, a scientific ranker prioritizes comparable experiments, and a model router selects the appropriate quantitative model for solid, liquid, or gaseous combustion.*
> 
> *A deterministic envelope guard checks whether the scenario is supported by NASA-tested conditions, while a final evidence auditor verifies that every scientific claim is traceable to data or model output before it reaches the user."*

---

## 8.10 Phase 8 Acceptance Gate

- [x] **Orchestrator Architecture Formalized:** Explicit state machine and branching flows defined.
- [x] **Seven Agents Specified:** Responsibilities, tools, state, handoffs, verification, and failure behavior locked.
- [x] **Envelope Guard Separated:** Formally designated as a deterministic scientific service.
- [x] **Shared State Object Defined:** Controlled JSON schema preventing parallel hallucinated contexts.
- [x] **Anti-Hallucination Audit Gate Established:** Evidence Auditor regex verification and fallback protocol locked.
- [x] **Least-Privilege Tool Access Enforced:** Explicit tool permissions table assigned per agent.
- [x] **Tri-Partite Confidence Architecture Defined:** Model confidence, evidence similarity, and domain support separated.
- [x] **Video Pitch Script Locked:** Concise, defensible 30-second technical narrative ready for prescreening.

---

## ✅ Phase 8 Status: COMPLETE

The multi-agent architecture and deterministic scientific services are formally locked.

We now proceed to **Phase 9: Quantitative ML Architecture**.
