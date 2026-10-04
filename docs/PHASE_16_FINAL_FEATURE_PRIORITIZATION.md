# Phase 16 — Final Feature Prioritization: FLARE-X

> **Status:** ✅ COMPLETE  
> **Challenge:** Flame in Freefall (NASA Space Apps Challenge 2026)  
> **Core Mandate:** Strict, disciplined feature prioritization governing hackathon development and prescreening scope. Enforces a 4-tier hierarchy (P0 Core, P1 Differentiators, P2 Polish, P3 Stretch) and an explicit CUT list. Eliminates feature creep: nothing is built merely because it sounds impressive.

---

## Executive Summary & Guiding Principle

We have officially reached the point where FLARE-X has enough possible features to become either a strong scientific product or a magnificent pile of half-working tabs.

Phase 16 fixes that. The rule from here forward is:
> **Nothing gets built because it sounds impressive. Every feature must justify itself through challenge alignment, scientific value, demo impact, and implementation risk.**

---

## 16.1 The Four-Tier Priority System + CUT List

| Priority Tier | Definition | Operational Rule |
| :--- | :--- | :--- |
| **P0 — Core** | The scientific backbone; FLARE-X is not a valid product without it. | **Non-negotiable.** Must be built and verified first before anything else. |
| **P1 — Differentiator** | What makes FLARE-X memorable, scientifically superior, and winning. | Built immediately after P0; forms our flagship pitch story. |
| **P2 — Polish** | Professional refinement that elevates user experience. | Built only if P0 and P1 are fully tested and stable. |
| **P3 — Stretch** | High-effort or high-risk features. | **Explicitly frozen** until all prior tiers are hardened. |
| **CUT** | Features banned from development during this competition. | **Zero engineering time wasted.** |

---

## 16.2 The Absolute P0 Definition (The Core Journey)

The final working FLARE-X prototype must reliably execute this end-to-end scientific flow:

```
                         USER SCENARIO
                              │
                              ▼
                  Structured Interpretation
                              │
                              ▼
                    Relevant NASA Evidence
                              │
                              ▼
                     Scientific Ranking
                              │
                              ▼
                    Experiment Comparison
                              │
                              ▼
              Compatible Quantitative Analysis
                              │
                              ▼
                 EXPERIMENTAL ENVELOPE GUARD
                              │
                              ▼
                 Evidence-Backed Explanation
                              │
                              ▼
                        NASA Provenance
```

*The Invariant:* If that flow works reliably, we have a winning product. If that flow fails, having voice control and an animated 3D flame galaxy will not save us.

---

## 16.3 P0 — Non-Negotiable Core Features

| Feature | Justification & NASA Challenge Alignment |
| :--- | :--- |
| **Structured Scenario Input** | User must define a physical combustion question ($O_2, u, P$, material) |
| **Natural Language Scenario Parsing** | Makes system accessible to flight controllers and researchers |
| **NASA Experiment Database** | Foundational ingested database (BASS-II, SPICE, SAFFIRE) |
| **Hybrid Evidence Retrieval** | Directly addresses NASA's mandate to *find* relevant research |
| **Scientific Relevance Ranking** | Directly satisfies NASA's mandate to *rank* microgravity findings |
| **Experiment Comparison View** | Directly satisfies NASA's mandate to *compare* flight test results |
| **At Least One Real Quantitative Model** | Proves substantive, non-hallucinated machine learning capability |
| **Experimental Envelope Guard** | Flagship safety differentiator; actively prevents extrapolation |
| **NASA Evidence Cards** | Renders flight test conditions, outcomes, and citations cleanly |
| **Provenance & DOI Source Links** | Guarantees scientific traceability back to NASA PSI / NTRS |
| **Evidence-Grounded Interpretation** | Converts raw experimental metrics into readable scientific insight |
| **Basic Evidence Auditor** | Deterministic gate rejecting unsupported claims or invented numbers |
| **One End-to-End Demo Scenario** | Rock-solid, reproducible walkthrough for judges and video |
| **Model Validation Metrics** | Aerospace credibility (baselines, grouped CV, confusion/residual charts) |

---

## 16.4 P0 Quantitative Model Decision: SPICE-FL

To guarantee that FLARE-X delivers a validated, mathematically defensible ML engine:
* **The Guaranteed Deliverable:** **`SPICE-FL` (Gaseous Diffusion Flame Length Regression)**
* **Why SPICE First:**
  - **526 discrete flight flames** from NASA PSI-107.
  - Clean continuous target: visible flame length ($L_{\text{flame}}$, mm).
  - Statistically robust sample size ($N=526$) eliminates small-data skepticism.
  - Straightforward validation ($R^2$, MAE in mm, prediction intervals).
  - Highly demonstrable: fuel flow and coflow velocity directly dictate flame geometry.

---

## 16.5 Product Narrative vs. Quantitative ML Proof

We decouple the storytelling narrative from the statistical proof engine:

```
[PRODUCT / DEMO NARRATIVE]                 [QUANTITATIVE ML PROOF]
       BASS-II + SAFFIRE                           SPICE-FL
Solid Spacecraft-Material Flammability      526-Flame Quantitative Regression
• Spacecraft cabin fire risk                • High statistical power
• Real flight burns & video                 • Continuous numerical target
• Evidence retrieval & comparison           • Baseline lift & prediction intervals
```

*Rule:* We do **not** force a weak, under-sampled BASS model into production just because solid fire is the headline narrative. If BASS labels are clean, we deploy `flame_spread_gb`; if noisy, BASS operates as an evidence-ranking and comparison system.

---

## 16.6 P0 NASA Dataset Ingestion Priority

1. **BASS-II (Priority 1):** Solid fire evidence, flagship PMMA scenario, opposed/concurrent flame spread.
2. **SPICE (Priority 2):** Primary quantitative machine learning engine (526 gaseous flames).
3. **SAFFIRE (Priority 3):** Spacecraft-scale flight context and radiometer time series.
4. **FLEX (Priority 4):** Droplet extinction data (ingested as soon as P0 pipeline is stable).
*(SAME smoke/aerosol records are deferred to stretch).*

---

## 16.7 P0 Scenario Lab Inputs

We do not burden users with an exhaustive 38-field aerospace questionnaire. For the flagship solid scenario:
* Material (`PMMA`, `Nomex`, `Cellulose`, `Delrin`)
* Oxygen concentration ($\%$)
* Airflow velocity ($\text{cm/s}$)
* Flow direction (`opposed` vs. `concurrent`)
* Sample geometry (`flat slab` vs. `cylindrical rod`)
* Target phenomenon (`flame spread` vs. `extinction`)

---

## 16.8–16.10 P0 Retrieval, Ranking, and Comparison

* **Retrieval Output:** Every retrieved flight run exposes investigation, test ID, material, $O_2$, flow, geometry, observed outcome, and DOI.
* **Transparent Hybrid Ranking:** Combines physical compatibility, material match, oxygen proximity, airflow proximity, geometry match, and semantic similarity. Displays explicit *"Why this ranked #1"* explanations.
* **Comparison View:** Three-way comparison grid:
  $$\text{User Scenario} \quad \text{vs.} \quad \text{NASA Flight Burn A} \quad \text{vs.} \quad \text{NASA Flight Burn B}$$

---

## 16.11–16.13 P0 Envelope Guard, Provenance, and Auditor

* **Guard Floor:** Evaluates family compatibility, categorical support, hard $[x_{\min}, x_{\max}]$ limits, and $k$-NN neighbor distance, outputting `INSIDE`, `NEAR_BOUNDARY`, `PARTIAL_SUPPORT`, or `OUTSIDE`.
* **Provenance Floor:** Every result links to its NASA investigation, PSI accession ID, test identifier, and persistent DOI.
* **Auditor Floor:** Deterministic checks verifying that every displayed number maps to NASA records or model metadata, blocking claims if out-of-domain.

---

## 16.14 P1 — Competitive Differentiators (Winning Tier)

Once P0 is validated, these features take FLARE-X from *competent* to *winning*:

| Feature | Why P1 |
| :--- | :--- |
| **Counterfactual Intelligence** | Strongest interactive differentiator; dynamic scenario comparison |
| **Experimental Support Map** | Signature visual; 2D slice showing exactly where NASA data lives |
| **FLEX Extinction Classifier** | Second quantitative model family; droplet flammability boundaries |
| **BASS Regime Model** | Solid flammability classifier (deployed if labels are clean) |
| **Evidence-Aware Counterfactual Slider** | Slider dynamically updates both predictions and NASA evidence |
| **Claim-Level Provenance** | Unprecedented scientific traceability from sentence to table row |
| **Model–Evidence Disagreement Badges** | Surfaces conflicts when model disagrees with nearest flight burn |
| **Calibrated Confidence Display** | Reliability diagrams and Brier scores; eliminates fake certainty |
| **Lightweight Knowledge Graph** | Cross-investigation links connecting BASS to SAFFIRE scale |
| **"Why Should I Trust This?" Panel** | 1-click transparency drilldown for judges and flight safety engineers |

---

## 16.15 P1 Sequential Build Order

1. **P1.1 — Counterfactual Slider:** Creates the most compelling, immediate demonstration of intelligence.
2. **P1.2 — Experimental Support Map:** Users visually see the "You Are Here" position relative to flight data.
3. **P1.3 — FLEX Extinction Model:** Adds our second quantitative experiment family.
4. **P1.4 — Claim-Level Provenance:** Deepens epistemic trust from document down to row/time coordinates.
5. **P1.5 — BASS-II Model:** Deployed conditionally based on label audit.
6. **P1.6 — Lightweight Knowledge Graph:** Relational entity/relationship tables connecting investigations.

---

## 16.16 The Flagship P1 Demo Journey (The 90-Second Winner)

```
1. Open PMMA solid scenario at 21% O₂, 20 cm/s opposed flow
   ├── 8 relevant BASS-II burns appear
   ├── SAFFIRE large-scale context surfaced
   └── Model predicts steady spread (P = 0.78) | Envelope: INSIDE
2. Drag Oxygen Slider downward: 21% ──► 20% ──► 19% ──► 18% ──► 17%
   ├── Model probability drops to 0.44 (marginal spread)
   ├── Nearest NASA experiments shift dynamically (Tests 42 & 51 highlight)
   ├── Star moves into amber boundary zone: NEAR_BOUNDARY
   └── Flammability tipping point visually detected
3. Drag Oxygen Slider to 12% (Untested microgravity territory)
   ├── Star enters gray cross-hatched region: OUTSIDE
   ├── System REFUSES authoritative prediction
   └── Surfaces Nearest Flight Evidence: "Lowest tested O₂ is 15.0%. Burns extinguished."
4. Click "Why?"
   └── 1-click provenance tree renders back to NASA PSI-25 DOI
```

---

## 16.19 P1 Lightweight Knowledge Graph (No Premature Neo4j)

* **Anti-Pattern Warning:** We do **not** begin hackathon implementation by configuring a Neo4j cluster. That is how several hours disappear into Docker network debugging.
* **Pragmatic Implementation:** Implemented in PostgreSQL via `kg_entities` and `kg_relationships` tables.

---

## 16.20 P2 — Product Polish (Experience Elevators)

Built only after P0 and P1 are frozen and verified:
* Interactive Knowledge Graph Explorer (focused subgraphs)
* Smooth UI micro-animations and slider transitions
* Technical vs. Flight Controller explanation mode toggles
* Dedicated Model Validation Dashboard (actual vs. predicted, ROC curves)
* Exportable FLARE-X Evidence Dossier (PDF / JSON / BibTeX)
* Multi-parameter filter facets (chamber volume, nozzle geometry)
* Detailed SHAP waterfall explainability views
* Mobile-responsive viewport optimizations

---

## 16.23 P3 — Explicitly Frozen Stretch Features

These features are **forbidden** from consuming core development hours:
* ❌ SAFFIRE Computer Vision & Video Flame Front Tracking
* ❌ BASS-II High-Speed Video Optical Segmentation
* ❌ 3D WebGL Particle Flame Simulators
* ❌ Voice Assistant & Audio Ingestion
* ❌ Autonomous Multimodal Agent Swarms
* ❌ SAME Predictive Smoke Sensor Regression
* ❌ Automated Research-Gap Heatmap Generation
* ❌ Partial-Gravity Extrapolation (Lunar / Martian $g$)
* ❌ Full Vehicle Digital-Twin CFD Coupling

---

## 16.26 The Explicit CUT List (Banned Ideas)

| Banned Feature Concept | Why Cut |
| :--- | :--- |
| **Universal Fire-Risk Score (0–100)** | Unscientific; physical regimes are non-commensurable. |
| **Universal Monolithic Combustion Model** | Violates physical reality ($d^2$ droplets $\neq$ solid slabs $\neq$ gas jets). |
| **Operational Astronaut Emergency Orders** | Unsafe; hackathon software must not issue live tactical egress commands. |
| **"Optimal Spacecraft Design" Optimizer** | Insufficient NASA data to model vehicle structural optimization. |
| **Autonomous Fire Suppression Commands** | Out of scope; FLARE-X is a decision-support and analysis tool. |
| **Fake Real-Time Sensor Telemetry** | Fabricating telemetry streams insults scientific credibility. |
| **Social / Community Sharing Feeds** | Nobody comes to an aerospace fire safety challenge for social networking. |

---

## 16.27 Objective Feature Prioritization Matrix

Scored on a 1–5 scale (Higher Risk = Worse):

| Candidate Feature | Challenge Alignment | Scientific Value | Demo Impact | Novelty | Risk | Final Tier |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **NASA Evidence Retrieval** | 5 | 5 | 4 | 2 | 2 | **P0** |
| **Scientific Relevance Ranking** | 5 | 5 | 4 | 4 | 2 | **P0** |
| **Experiment Comparison View** | 5 | 5 | 4 | 3 | 2 | **P0** |
| **SPICE Flame Length Model** | 4 | 5 | 4 | 3 | 2 | **P0** |
| **Experimental Envelope Guard** | 5 | 5 | 5 | 5 | 3 | **P0** |
| **NASA Provenance & DOIs** | 5 | 5 | 4 | 4 | 2 | **P0** |
| **Counterfactual Intelligence** | 4 | 5 | 5 | 5 | 3 | **P1** |
| **Experimental Support Map** | 4 | 5 | 5 | 4 | 3 | **P1** |
| **FLEX Extinction Model** | 4 | 5 | 5 | 3 | 3 | **P1** |
| **BASS Regime Model** | 5 | 5 | 5 | 3 | 4 | **P1 (Cond)** |
| **Lightweight Knowledge Graph** | 4 | 4 | 4 | 3 | 4 | **P1 / P2** |
| **SAFFIRE Computer Vision** | 3 | 4 | 5 | 4 | 5 | **P3** |
| **Voice Scientific Assistant** | 2 | 1 | 3 | 1 | 3 | **P3** |
| **3D WebGL Flame Galaxy** | 2 | 2 | 5 | 3 | 5 | **P3** |

---

## 16.28 The 16-Step Dependency Build Sequence

```
1. NASA Data Ingestion (Hashed Bronze Layer)
   ↓
2. Normalized Silver Experiment Schema
   ↓
3. Hybrid Evidence Retrieval Engine
   ↓
4. Physics-Informed Scientific Ranker
   ↓
5. Multi-Experiment Comparison View
   ↓
6. SPICE-FL Quantitative Regression Pipeline
   ↓
7. Experimental Envelope Guard (Bounds + k-NN)
   ↓
8. Evidence Provenance & Citation Linking
   ↓
9. Core Frontend Scenario Lab Integration
   ↓
10. Dynamic Counterfactual Slider Engine
   ↓
11. Interactive Experimental Support Map
   ↓
12. FLEX-EX Droplet Classification Pipeline
   ↓
13. BASS-RG Solid Regime Model (Conditional)
   ↓
14. Relational Knowledge Graph Engine
   ↓
15. Diagnostic Validation Dashboard (P2)
   ↓
16. Stretch Explorations (P3)
```

---

## 16.33 Emergency Cut Order (Time-Collapse Contingency)

If implementation hours collapse during the hackathon, shed scope in this exact order:
* **Cut 1:** Voice, 3D simulation, and multimedia graphics.
* **Cut 2:** Computer vision and high-speed video tracking.
* **Cut 3:** SAME smoke sensor analysis.
* **Cut 4:** Automated research-gap heatmaps.
* **Cut 5:** Graph frontend visualizers (preserve backend relational queries).
* **Cut 6:** BASS predictive model (fall back to BASS evidence retrieval & ranking).
* **Cut 7:** FLEX secondary regression targets.

### The Unbreakable Spine (Preserve at All Costs):
1. NASA Evidence Retrieval
2. Scientific Ranking
3. Multi-Experiment Comparison
4. One Validated ML Model (SPICE-FL)
5. Experimental Envelope Guard
6. Provenance & DOI Links
7. One Polished End-to-End Demo Journey

---

## 16.34 October 7 Prescreening Scope Accuracy

For the October 7 prescreening video and documentation, scope is described with absolute honesty:
* **Core Backbone:** NASA evidence retrieval, scientific ranking, multi-experiment comparison.
* **Quantitative Machine Learning:** SPICE flame length regression (526 flames), FLEX extinction classification, BASS solid flammability modeling.
* **Flagship Differentiator:** The Experimental Envelope Guard (active refusal of extrapolation).
* **Interactive Innovation:** Evidence-aware counterfactual flammability sliders.
* **Visual Anchor:** The 2D Experimental Support Map.

---

## 16.35 Video 1 Master Pitch Narrative Lock

> **“FLARE-X first finds the NASA experiments most relevant to a fire scenario. It compares their conditions, routes supported questions to specialized quantitative models, and checks whether the requested scenario falls inside NASA-tested conditions before trusting the prediction.**
> 
> **Users can then change oxygen, airflow, or other parameters and see not only how the model changes, but how the supporting NASA evidence changes with it. Every result remains traceable to its authentic NASA source.”**

---

## 16.36 Main Pitch Jargon Embargo

Unless explicitly asked by technical judges in Q&A, strictly ban elevator-pitch mentions of:
* `LangGraph`, `Neo4j`, `Vector DB`, `PostgreSQL`, `StratifiedGroupKFold`, `SHAP`, `Gower distance`, `Conformal prediction`.
* *Rule:* Pitch what the system **solves for aerospace safety**, not the software stack.

---

## 16.37 Canonical Master Product Hierarchy

```
FLARE-X
│
├── P0: SCIENTIFIC BACKBONE (Mandatory Floor)
│   ├── Structured Scenario Parser
│   ├── NASA Evidence Ingestion & Store
│   ├── Physics-Informed Ranker
│   ├── Multi-Experiment Comparison Grid
│   ├── SPICE-FL Quantitative Model
│   ├── Experimental Envelope Guard
│   ├── Grounded Synthesizer
│   └── Provenance & DOI Links
│
├── P1: DIFFERENTIATION (Winning Tier)
│   ├── Counterfactual Intelligence Slider
│   ├── Interactive Experimental Support Map
│   ├── FLEX-EX Droplet Model
│   ├── BASS-RG Model (Conditional)
│   ├── Claim-Level Provenance Locators
│   └── Model vs. Evidence Disagreement Badges
│
├── P2: EXPERIENCE (Professional Polish)
│   ├── Contextual Graph Subgraph Views
│   ├── Model Validation Dashboard
│   ├── Basic Explainability Panels
│   ├── PDF / JSON Evidence Dossier Export
│   └── Viewport Optimizations
│
└── P3: STRETCH (Explicitly Frozen)
    ├── High-Speed Video Flame Tracking
    ├── SAME Smoke Aerosol Models
    ├── 3D Flame Simulators
    └── Automated Research Gap Discovery
```

---

## 16.38 The Protected Three (FLARE-X Identity)

If time permits only three features beyond core retrieval:
1. **Experimental Envelope Guard** (*"Do not answer beyond the evidence"*)
2. **Counterfactual Intelligence** (*"Dynamic model + evidence re-evaluation"*)
3. **Experimental Support Map** (*"Visualizing where NASA evidence lives"*)

Together, these three create the unforgettable FLARE-X identity.

---

## ✅ Phase 16 Status: COMPLETE

Final Feature Prioritization is formally codified, verified, and locked.

We now advance to **Phase 17: UI/UX Information Architecture** (translating this locked hierarchy into page layouts, screen wireframes, component component trees, interaction flows, responsive breakpoints, and judge-facing demo views).
