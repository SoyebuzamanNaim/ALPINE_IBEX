# Phase 6 — Scientific Questions & ML Targets

> **Status:** ✅ COMPLETE  
> **Challenge:** Flame in Freefall (NASA Space Apps Challenge 2026)  
> **Primary Scope:** Specialized Scientific Models, Evidence Retrieval, and Relevance Ranking  
> **Discipline:** Zero-Fabrication, Grouped Cross-Validation Discipline, Anti-Overfitting Protocol  
> **Core Principle:** Specialized Scientific Models over One Universal Fire Model

---

## 6.1 Four Kinds of Intelligence Inside FLARE-X

We stop treating everything as "prediction." FLARE-X requires four distinct analytical functions:

| Function | Core Question | Primary Implementation |
| :--- | :--- | :--- |
| **Retrieval** | Which NASA experiments are relevant? | Hybrid Search (Structured parameters + Semantic NTRS vector search) |
| **Ranking** | Which of those experiments are most relevant? | Scientific Relevance Ranker (Multidimensional physical distance + family penalties) |
| **Prediction / Estimation** | What measurable behavior is supported by a compatible dataset? | Specialized ML Models (BASS-II Classifier, SPICE Regressor, FLEX Boundary Model) |
| **Interpretation** | What does that evidence imply, and how strong is it? | Bounded LLM Synthesizer (Evidence-grounded explanation, zero hallucination) |

*The LLM handles mostly the fourth; structured algorithms and ML handle the first three.*

---

## 6.2 Core Scientific Questions

* **Q1 — Evidence Discovery:** Given a fire-related scenario, which NASA experiments are scientifically relevant?
* **Q2 — Experimental Similarity:** How closely do NASA-tested conditions match the user's requested conditions? *(Drives ranking)*.
* **Q3 — Extinction (FLEX):** Under experimentally supported liquid-fuel conditions, is a droplet flame likely to sustain combustion or extinguish?
* **Q4 — Flame Behavior (SPICE):** How do fuel, burner size, co-flow velocity, and fuel flow relate to flame length and smoke-point behavior?
* **Q5 — Solid-Material Flame Behavior (BASS-II):** Under particular oxygen, airflow, material, and geometry conditions, what solid-fuel combustion regime was observed?
* **Q6 — Spacecraft-Scale Context (SAFFIRE):** Which large-scale SAFFIRE experiments provide real spacecraft-fire evidence similar to a given solid-fuel scenario? *(Context/validation task, not a large supervised ML problem)*.
* **Q7 — Smoke Behavior (SAME):** What smoke-generation or aerosol evidence exists for a material and combustion condition?

---

## 6.3 Core ML Philosophy & Qualification Criteria

Every predictive target must pass four mandatory criteria:
1. NASA actually measured the target.
2. There are enough independent observations ($N$).
3. The inputs have physical relevance to that target.
4. We can validate the model without data leakage.

*If an idea fails any one of those, it does not become a core model.*

---

## 6.4 Model A — NASA Experiment Relevance Ranker (Core)

This is perhaps the most challenge-relevant AI component, directly addressing NASA's explicit request to **rank findings**.

* **Input Vector:**
  - *User scenario:* Fuel/material, fuel phase, oxygen, pressure, airflow, flow direction, geometry, phenomenon of interest, query text.
  - *Candidate NASA experiment:* Investigation, fuel/material, oxygen, pressure, flow, geometry, measured phenomena, experiment description.
* **Output:** Scientific relevance score and human-readable rationale:
  - Material match, oxygen proximity, airflow proximity, geometry compatibility, combustion-family compatibility, phenomenon match, semantic relevance.
* **Hybrid Formulation:**
  $$\text{Relevance} = \text{Structured Scientific Similarity} + \text{Semantic Relevance} + \text{Family Compatibility} + \text{Data-Coverage Quality}$$
* **Example:** User asks about *PMMA flame spread at 18% $O_2$ under forced airflow*. A SPICE methane flame could numerically have a similar flow speed, but the ranker penalizes fuel phase (gas $\ne$ solid) and phenomenon (smoke point $\ne$ flame spread). BASS-II and SAFFIRE rise to the top.

---

## 6.5 Model B — FLEX Extinction Classifier (Core / Flagship)

* **Scientific Question:** Under a given NASA-supported droplet combustion condition, does the flame sustain burning or reach extinction?
* **Inputs:** Fuel identity, initial droplet diameter ($d_0$), oxygen mole fraction, ambient pressure, diluent identity, suppressant identity, suppressant concentration, flow condition.
* **Primary Target:**
  $$\texttt{extinction\_status} \in \{ \texttt{SUSTAINED / BURNED\_TO\_COMPLETION},\ \texttt{EXTINGUISHED} \}$$
  *(Optional 3-class extension: `NO_IGNITION`, `EXTINCTION`, `BURNED_TO_COMPLETION`).*
* **Secondary Targets (Differentiators):**
  - Burning rate constant $K$ ($\text{mm}^2/\text{s}$) via $d^2$-law.
  - Extinction droplet diameter $d_{\text{ext}}$ ($\text{mm}$).
* **Flagship Visualization:** **Extinction Boundary Explorer**—plots sustained burning vs. radiative extinction regions with real NASA test points overlaid.
* **Status:** Classification (**CORE**), Burning-rate regression (**Differentiator**), Universal safety score (**REJECTED**).

---

## 6.6 Model C — SPICE Flame-Length Regression (Core / High-N)

SPICE provides **526 flames** across several fuels, 3 burner diameters ($0.41, 0.76, 1.6\text{ mm}$), and co-flow velocities from $5.4\text{ to }65\text{ cm/s}$.

* **Scientific Question:** Given fuel and controlled flow conditions, what luminous flame behavior should we expect within the experimentally observed SPICE domain?
* **Inputs:** Fuel identity, burner diameter ($d_{\text{burner}}$), co-flow velocity ($u_{\text{coflow}}$), fuel flow rate ($Q_{\text{fuel}}$).
* **Primary Target (Regression):** Visible flame length / height ($L_{\text{flame}}$ in mm).
* **Secondary Target (Classification):** Smoke-point regime $\in \{ \texttt{BELOW\_SMOKE\_POINT},\ \texttt{AT/ABOVE\_SMOKE\_POINT} \}$.
* **Strategic Importance:** SPICE gives us a large, statistically sound dataset ($N=526$) to demonstrate unmistakable, robust machine learning without pretending that 12 burns constitute "Big Data".
* **Status:** Flame-length regression (**CORE**), Smoke-point classification (**CORE / DIFFERENTIATOR**), Generic danger prediction (**REJECTED**).

---

## 6.7 Model D — BASS-II Solid-Fire Regime Model (Core / High Safety Value)

* **Scientific Question:** For a solid fuel/material under specified microgravity oxygen, flow, and geometry conditions, what experimentally observed combustion regime is most plausible? *(Predicts regime, NOT a risk score).*
* **Inputs:** Material, material family, sample geometry, sample thickness, dimensions, oxygen concentration, airflow velocity, airflow direction, ignition configuration.
* **Primary Target (3-Class Regime):**
  $$\texttt{outcome} \in \{ \texttt{no\_spread},\ \texttt{marginal\_spread},\ \texttt{spread} \}$$
* **Secondary Target (Regression):** Flame spread rate $V_f$ ($\text{mm/s}$) for propagating tests.
* **Additional Scientific Feature:** **Flammability Boundary Estimation** ($O_2$ vs. airflow velocity for specific polymers like PMMA).
* **Status:** Regime classification (**CORE**), Flame spread regression (**High-Value Differentiator**), Flammability boundary (**High-Value Differentiator**), Universal rating (**REJECTED**).

---

## 6.8 Model E — SAFFIRE Evidence Matcher (Core Evidence / Context)

We deliberately resist the urge to train an overfitted supervised classifier on SAFFIRE's small number of flight burns ($N < 10$).

* **Role:** **Spacecraft-Scale Reality & Context Anchor.**
* **Primary Task (Similarity Matching):** Identifies the closest spacecraft-scale test, comparing materials, dimensions, airflow, and observed fire behavior.
* **Secondary Task (Sensor Time-Series Analysis):** Tracks $T(t), O_2(t), CO_2(t), P(t)$ to detect ignition, growth, peak activity, and decay.
* **Stretch Task (Computer Vision):** Optical flame-front tracking and spread-rate calculation from raw imagery.
* **Status:** Similarity matching (**CORE Evidence**), Sensor time-series (**Differentiator**), CV flame tracking (**Stretch**), Supervised ML on $<10$ burns (**REJECTED**).

---

## 6.9 Model F — SAME Smoke Intelligence (Supporting Module)

* **Scientific Question:** How do material, airflow, generation rate, and aging relate to observed smoke/aerosol characteristics?
* **Core Role:** Retrieval, comparison, and visualization linking solid material pyrolysis to smoke particle size and detector response.
* **Status:** Smoke evidence retrieval (**CORE Supporting**), Comparative visualization (**Differentiator**), Particle-size regression (**Conditional**), Generic smoke danger score (**REJECTED**).

---

## 6.10 Cross-Dataset Engine Features

1. **Experimental Similarity Engine:** Computes weighted physical distances across compatible experiment families and generates readable similarity rationales.
2. **Scientific Literature / Report Retrieval (RAG):** Semantic retrieval across NTRS technical reports and PSI documents, providing grounded context for numerical predictions.
3. **Evidence Synthesis:** Synthesizes common observations, disagreements, parameter differences, and evidence strength across retrieved tests.
4. **Research Gap Detection:** Flags sparse or empty regions in the multidimensional parameter space (e.g. *"PMMA at 16% O2 and high airflow: LOW EVIDENCE COVERAGE"*).

---

## 6.11 Rejecting the Single "Risk Score"

FLARE-X explicitly rejects arbitrary composite scores like `Fire Risk = 83/100`. Instead, our result card provides transparent, verifiable dimensions:

```
┌────────────────────────────────────────────────────────────────────────┐
│ FLARE-X PHYSICAL RESULT CARD                                           │
├────────────────────────────────────────────────────────────────────────┤
│ COMBUSTION REGIME:    Sustained Propagation Likely (in tested family)  │
│ MODEL CONFIDENCE:     0.82 (Calibrated Gradient Boosting Probability)  │
│ EXPERIMENTAL MATCH:   High Similarity to BASS2_B10 & BASS2_B11         │
│ DOMAIN STATUS:        Inside Observed NASA Parameter Envelope          │
│ NASA EVIDENCE:        8 Relevant Flight Experiments (NTRS 20210011385) │
│ LIMITATION:           Sample thickness differs (0.1 mm vs 1.0 mm)      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 6.12 Core Scientific Computational Architecture

```
                                USER QUERY
                                    │
                                    ▼
                             Scenario Parser
                                    │
                                    ▼
                              Model Router
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
   Solid Query                Droplet Query                 Gas Query
   (BASS-II)                     (FLEX)                      (SPICE)
        │                           │                           │
        ▼                           ▼                           ▼
Regime/Spread Model         Extinction Model            Flame Length Model
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    ▼
                             Evidence Ranker
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
                 SAFFIRE                          SAME
             Mission Context                 Smoke Context
                    │                               │
                    └───────────────┬───────────────┘
                                    ▼
                            Evidence Synthesis
                                    │
                                    ▼
                         Confidence + Provenance
```

---

## 6.13 Flagship Demonstrations: Gas, Liquid, Solid

* **Demo A (GAS):** Change co-flow velocity and observe predicted SPICE flame length ($N=526$) with nearby flight flames.
* **Demo B (LIQUID):** Change oxygen/pressure and observe the FLEX extinction boundary map.
* **Demo C (SOLID — Main Story):** Enter an exploration atmosphere scenario ($32\%\text{ O}_2, 56.5\text{ kPa}$) and retrieve/rank BASS-II and SAFFIRE evidence with 2D decision boundary slices.

---

## 6.14 Anti-Leakage Protocol & Explainability

* **Anti-Leakage Guarantee:** Validation splits must occur at the independent experiment/flight-test level (`StratifiedGroupKFold` by `report_id`), never randomly across frames or repeated runs.
* **Bounded Explainability:** Tabular feature importance (Permutation / SHAP) is reported as *model contribution*, never as unproven causal physics.
* **Bounded LLM Role:** The LLM is permitted to summarize evidence and explain differences; it is **strictly forbidden** from inventing probabilities, numerical measurements, or flammability limits.

---

## 6.15 Master Model-Target Specification Table

| System Component | Input Vector | Output / Target | ML Task Type | Priority |
| :--- | :--- | :--- | :--- | :---: |
| **Scientific Ranker** | Scenario + candidate metadata | Relevance score + explanation | Ranking / Distance | **CORE** |
| **FLEX Extinction Model** | Fuel, $O_2$, pressure, $d_0$, suppressant | Extinction vs. sustained regime | Binary Classification | **CORE** |
| **SPICE Flame Model** | Fuel, burner dia, coflow, fuel flow | Flame length / height ($mm$) | Continuous Regression | **CORE** |
| **BASS-II Regime Model** | Material, $O_2$, pressure, airflow | Flame spread regime (`no_spread`, `marginal`, `spread`) | 3-Class Classification | **CORE** |
| **BASS-II Spread Model** | Material, $O_2$, airflow, geometry | Flame spread rate $V_f$ ($\text{mm/s}$) | Regression | **Differentiator** |
| **SPICE Smoke-Point Model** | Fuel, flow, coflow, burner dia | Smoke-point regime transition | Classification | **High** |
| **SAFFIRE Context Engine**| Scenario conditions | Closest large-scale spacecraft test | Similarity Retrieval | **CORE Evidence** |
| **SAME Smoke Engine** | Material, airflow, pyrolysis temp | Smoke aerosol context / particle size | Retrieval / Regression | **Supporting** |
| **Document Engine (RAG)** | Natural language question | Verified NASA text citations | Semantic Retrieval | **CORE** |
| **Evidence Synthesizer** | Ranked evidence + predictions | Traceable narrative explanation | Bounded LLM | **CORE** |
| **Envelope Guard** | 4-D input vector | In-bounds / Out-of-bounds flag | Bounding Box Rule | **CORE Safeguard** |

---

## 6.16 Video 1 Script Lock: The Machine Learning Strategy

For the October 7 prescreening video, we state our quantitative strategy with complete scientific defensibility:

> *"Because NASA's combustion investigations span fundamentally different physical systems, FLARE-X uses structured experimental data to build specialized predictive and comparative models rather than forcing heterogeneous experiments into a single model. FLEX supports droplet extinction analysis, SPICE provides flame-behavior modeling across 526 controlled flames, and BASS-II provides solid-material flame-spread and extinction evidence. SAFFIRE and SAME contribute critical spacecraft-scale and smoke-detection context—delivering rigorous AI grounded entirely in verified physics."*

---

## 6.17 Phase 6 Acceptance Gate

- [x] **Four Intelligence Functions Defined:** Retrieval, Ranking, Prediction/Estimation, and Interpretation.
- [x] **Seven Scientific Questions Formulated:** Grounded in BASS-II, FLEX, SPICE, SAFFIRE, and SAME.
- [x] **Specialized Models Specified:** Solid spread classification, droplet extinction mapping, and gas flame length regression.
- [x] **Fraudulent AI Claims Explicitly Barred:** Banned universal risk scores, deep learning on $<10$ burns, and frame-level data leakage.
- [x] **Anti-Leakage CV Scheme Locked:** Enforced `StratifiedGroupKFold` grouped by `report_id`.
- [x] **Bounded LLM Safeguards Enforced:** LLM restricted to evidence synthesis; barred from generating numbers or probabilities.
- [x] **Three Flagship Demos Selected:** Gas (SPICE), Liquid (FLEX), Solid (BASS-II/SAFFIRE).

---

## ✅ Phase 6 Status: COMPLETE

The scientific questions and ML target specifications are formally defined and verified.

We now proceed to **Phase 7: FLARE-X Product Definition**.
