# Phase 21 — Judging-Criteria Mapping: FLARE-X

> **Status:** ✅ COMPLETE  
> **Challenge:** Flame in Freefall (NASA Space Apps Challenge 2026)  
> **Core Mandate:** Strategic and structural mapping of FLARE-X directly to the official NASA Space Apps Challenge judging dimensions. Replaces subjective enthusiasm with concrete, defensible proof points mapped to the five canonical criteria: **Impact**, **Creativity**, **Validity**, **Relevance**, and **Presentation**. Establishes the scoring backbone, pitch hierarchy, Q&A defense playbooks, and demo-to-rubric traceability.

---

## Executive Summary & Judging Strategy

For 2026, official NASA Space Apps event guidance identifies the same five core judging criteria utilized across global evaluations:
**Impact, Creativity, Validity, Relevance, and Presentation** ([Space Apps Challenge Global Guidelines](https://www.spaceappschallenge.org/)).

NASA event guidance defines them broadly as:
* **Impact:** Potential scope, usability, and transformative value of the solution to society, NASA, or the target problem domain.
* **Creativity:** Novelty, innovation, and distinctiveness of the technical or architectural approach.
* **Validity:** Scientific soundness, technical feasibility, mathematical rigour, and empirical defensibility.
* **Relevance:** Direct responsiveness, completeness, and alignment with the specific challenge prompt and NASA data.
* **Presentation:** Clarity of communication, narrative coherence, storytelling effectiveness, and accessibility.

> **Operational Weighting Protocol:**  
> Because official global guidance does not publish static percentage weights, FLARE-X treats every single criterion as **capable of disqualifying or sinking the submission if neglected**. A single vulnerability in scientific validity or presentation clarity will forfeit global award contention.

---

## 21.1 Final Judging Strategy: One Unified Scientific Story

FLARE-X does not present five disjointed arguments to plead for points across five categories. A fragmented pitch confuses judges and dilutes memorability.

Instead, **one central, compelling scientific story satisfies all five criteria simultaneously**:

> **"NASA already possesses decades of invaluable microgravity-combustion flight evidence, but that evidence remains fragmented across disparate investigations, experimental geometries, raw telemetry files, technical reports, and distinct combustion physics regimes.**  
> **FLARE-X transforms this static archive into evidence-bounded scientific intelligence: it dynamically discovers and ranks the most physically comparable spaceflight tests, executes specialized quantitative models strictly where valid, verifies whether NASA has ever tested similar physical conditions via the Experimental Envelope Guard, enables controlled counterfactual exploration, and traces every scientific conclusion back to empirical NASA flight records."**

This singular narrative maps seamlessly across every judging dimension.

---

## 21.2 Master Judging Matrix

| Criterion | What Judges Need to Believe | FLARE-X Proof & Concrete Mechanism |
| :--- | :--- | :--- |
| **Impact** | This solves a high-friction, meaningful scientific problem for space exploration. | Accelerates discovery and reuse of microgravity combustion records; eliminates weeks of manual paper cross-referencing for spacecraft fire safety research. |
| **Creativity** | This is a novel scientific architecture, not an off-the-shelf chatbot, RAG wrapper, or generic dashboard. | **Experimental Envelope Guard** (abstention & boundary detection) + **Evidence-Aware Counterfactual Swarms** + **Family-Aware Specialized Intelligence**. |
| **Validity** | The physics, data pipelines, and machine learning models are methodologically defensible. | Authentic NASA PSI spaceflight datasets, physical family segregation (no universal predictor), leak-free Grouped CV, calibrated prediction intervals, and claim-level provenance. |
| **Relevance** | This directly and comprehensively solves the "Flame in Freefall" challenge brief. | Directly ingests, structures, indexes, ranks, compares, and interprets multi-decade NASA combustion flight programs (BASS, BASS-II, FLEX, SPICE, SAFFIRE, SAME). |
| **Presentation** | The value proposition and workflow are crystal-clear and immediately graspable. | Single cohesive scenario workflow: *User Scenario $\to$ Ranked Flight Evidence $\to$ 2D Support Map $\to$ Oxygen Slider $\to$ Boundary Refusal $\to$ Primary Source DOI*. |

This matrix serves as the operational scoring backbone for all deliverables (prescreening video, slide deck, interactive demo, and project documentation).

---

## 21.3 Criterion 1 — IMPACT

### 21.3.1 The Core Impact Thesis
NASA’s official rubric emphasizes the quality, depth, and reach of potential impact. 

* **What We Refuse to Claim:**  
  *"FLARE-X will autonomously save astronauts' lives."*  
  *(Such claims are scientifically irresponsible, unprovable in a hackathon setting, and trigger immediate skepticism from aerospace judges).*
* **Our Defensible, Authoritative Claim:**  
  **FLARE-X drastically reduces the friction between a spacecraft fire-safety research question and the NASA flight evidence required to evaluate it.**

---

### 21.4 The Underlying Impact Problem
NASA has accumulated irreplaceable microgravity combustion research over decades across landmark missions:
* **BASS & BASS-II:** Solid fuel flammability, forced flow interaction, and extinction limits in the ISS CIR.
* **FLEX & FLEX-2:** Droplet combustion dynamics, radiative extinction, and cool-flame regimes.
* **SPICE & ACME:** Gaseous laminar and co-flow diffusion flames.
* **SAFFIRE (I–VI):** Real spacecraft-scale compartment material fires inside Cygnus cargo spacecraft.
* **SAME:** Spacecraft particulate and smoke aerosol properties.

However, answering a new material flammability question (e.g., *"How does PMMA behave under exploration atmospheres of 18% $O_2$ with 15 cm/s ventilation?"*) currently requires researchers to:
1. Search static document repositories (PSI and NTRS) across heterogeneous naming conventions.
2. Manually isolate physically comparable experiments from hundreds of tests.
3. Compare differing boundary conditions (sample thickness, duct geometry, forced flow velocity).
4. Evaluate whether mathematical or numerical modeling applies to that regime.
5. Manually verify how far findings can be generalized without risking catastrophic extrapolation.
6. Trace every safety-critical claim back to original raw test runs.

**FLARE-X compresses this multi-week investigative pipeline into seconds.** That is authentic, measurable scientific impact.

---

### 21.5 Impact Beneficiaries
* **Primary Users:** Combustion scientists, materials engineers, and spacecraft life-support/safety researchers investigating reduced-gravity fire dynamics using NASA archival evidence.
* **Secondary Users:** Mission systems engineers evaluating Exploration Atmospheres ($34\%\text{ O}_2, 56.5\text{ kPa}$), academic researchers, thermal safety analysts, aerospace students, and training flight controllers.
* **Excluded Users:** Active astronauts during an in-flight fire emergency. FLARE-X is a pre-mission research and decision-support architecture, not an operational, life-critical emergency avionics system.

---

### 21.6 Impact Chain
```text
NASA Archival Flight Evidence (PSI & NTRS)
           │
           ▼
Fragmented, heterogeneous across 5 combustion families & static reports
           │
           ▼
Substantial manual research overhead (weeks of document synthesis)
           │
           ▼
FLARE-X structures, indexes, and ranks experiment-level evidence
           │
           ▼
Researchers identify physically comparable tests in seconds
           │
           ▼
Envelope Guard & specialized models delineate safe inferences from unknown regimes
           │
           ▼
Higher-rigor material selection, safer exploration atmospheres & better spacecraft fire safety
```

> **Key Distinction:** FLARE-X **supports superior scientific and engineering decisions**; it does not replace human engineers or autonomously certify flight hardware.

---

### 21.7 What Proves Impact
At evaluation time, judges will not reward empty adjectives. Impact must be visibly demonstrated:
* **Visible Comparative Flow:** Side-by-side demonstration of manual PSI/PDF searching vs. FLARE-X's instant, ranked experiment extraction.
* **Usability Verification:** Time-to-identification metric for pinpointing relevant NASA flight tests matching an operational fire inquiry.

---

### 21.8 Flagship Impact Demonstration Scenario
* **Scenario Query:** *"Find the most relevant NASA evidence for PMMA flame propagation under reduced oxygen ($18\%\text{ O}_2$) and forced airflow ($20\text{ cm/s}$)."*
* **FLARE-X Response:**
  * Returns **BASS-II Tests 31, 42, and 56** with exact velocity and oxygen pairings.
  * Connects with **SAFFIRE-II** spacecraft-scale cotton/fiberglass composite fire context.
  * Exposes explicit boundary variations (sample dimensions, flow speeds, extinction observations).
  * Maps scenario placement within the known NASA experimental domain.

---

### 21.9 Impact Language Guide
* **Approved Wording:**  
  *"FLARE-X unlocks decades of closed NASA combustion archives, making flight test evidence rapidly discoverable, comparable, and actionable for next-generation spacecraft fire-safety design."*
* **Prohibited Wording:**  
  *"FLARE-X completely eliminates fire hazards in space."*

---

## 21.10 Criterion 2 — CREATIVITY

NASA criteria evaluate the novelty, originality, and sophistication of the approach. 

### Why Standard AI Pitches Fail
Our competitive audit proves that judges are fatigued by generic "AI wrappers". None of the following constitutes sufficient novelty on its own:
* A generic chatbot answering questions from PDFs.
* Standard Retrieval-Augmented Generation (RAG).
* A single off-the-shelf machine learning regressor.
* A multi-agent orchestration without domain-specific constraints.
* A static data dashboard.

FLARE-X demonstrates authentic innovation through **four core architectural creative mechanisms**:

---

### 21.11 Creativity Claim #1: Evidence-Bounded AI & The Envelope Guard
Most AI platforms generate an ungrounded answer regardless of whether data exists. FLARE-X introduces an **epistemic safety mechanism**: it evaluates whether empirical evidence exists *before* deciding whether to predict.

The **Experimental Envelope Guard** combines:
1. **Family Compatibility Check:** Ensures solid fuel queries are never evaluated by gas or droplet models.
2. **Categorical Support:** Confirms material and geometry overlap.
3. **Multi-dimensional Convex Hull & Range Checks:** Evaluates environmental variables ($O_2$, flow velocity, pressure).
4. **Local Experiment Density ($k$-NN kernel density):** Determines whether nearby spaceflight tests are abundant or sparse.

**Outputs 4 Defensible States:**
* `INSIDE`: High empirical density; quantitative model inference authorized.
* `NEAR BOUNDARY`: Marginal empirical support; prediction displayed with prominent uncertainty intervals.
* `PARTIAL SUPPORT`: Incomplete variable coverage; qualitative guidance only.
* `OUTSIDE`: No NASA flight tests exist; **quantitative prediction withheld**, abstention enforced, and nearest flight tests displayed.

---

### 21.12 Creativity Claim #2: Evidence-Aware Counterfactual Intelligence
In standard ML demos, moving a slider merely updates an isolated number.  
In FLARE-X, updating an environmental parameter (e.g., oxygen concentration from $21\%$ to $14\%$) executes a multi-stage **evidence-aware counterfactual sweep**:
1. Mathematical model executes in real-time.
2. NASA flight database is dynamically re-queried across distance metric space.
3. Relevant spaceflight tests are re-ranked based on proximity to the new physical state.
4. Experimental envelope status is recalculated.
5. Evidence strength and confidence intervals update synchronously.
6. Scientific interpretation text updates dynamically with epistemic claim badges.

---

### 21.13 Creativity Claim #3: Family-Aware Scientific Intelligence
Combustion physics cannot be collapsed into a single toy algorithm:
$$\text{Solid Fuel (BASS)} \neq \text{Droplet (FLEX)} \neq \text{Gaseous Jet (SPICE)} \neq \text{Aerosol (SAME)}$$

FLARE-X explicitly rejects a scientifically fraudulent "universal fire risk predictor". It structures NASA combustion data into a unified evidence layer while routing specific queries to specialized, family-specific quantitative engines.

---

### 21.14 Creativity Claim #4: Experiment-Centric Claim-Level Provenance
Generic AI provides vague document citations (e.g., "See NASA TP-2016-1234").  
FLARE-X implements granular, node-based provenance:
```text
Scientific Claim / Prediction
          │
          ▼
Quantitative Model Version & Training Manifest
          │
          ▼
Individual NASA Flight Test (e.g., BASS-II Test 31)
          │
          ▼
Specific Data Table, Column & Sensor Metric
          │
          ▼
NASA PSI Accession DOI & NTRS Technical Publication
```

---

### 21.15 Creativity Presentation Hierarchy
When presenting to judges, maintain focus on the three primary breakthroughs:
1. **FLARE-X determines which NASA flight tests actually apply.**
2. **FLARE-X knows when empirical evidence is too sparse to justify a prediction.**
3. **When conditions shift, FLARE-X re-evaluates both the prediction and the supporting evidence landscape.**
*(Claim-level provenance serves as the deep-dive technical anchor when judges probe integrity).*

---

### 21.16 Creativity Visual Proof: The Experimental Support Map
The 2D Support Map visually encapsulates the project's creativity:
* The judge observes historical NASA flight tests plotted as scatter points alongside an empirical support boundary.
* A user scenario appears as a distinct indicator star ($\star$).
* As oxygen is varied, the star traverses the coordinate space.
* Nearby flight tests re-rank live.
* As the star crosses the flammability threshold into unsupported space, the model halts prediction and transitions to an **Envelope Refusal Notice**.

---

## 21.17 Criterion 3 — VALIDITY

Validity evaluates scientific rigor, technical plausibility, and integrity. This is FLARE-X’s strongest dimension and our primary defense against technical interrogation.

---

### 21.18 Validity Pillar 1: Authentic NASA Spaceflight Evidence
All quantitative foundations derive directly from peer-reviewed NASA flight experiments:
* BASS & BASS-II (Space Shuttle STS-94, ISS Missions)
* FLEX & FLEX-2 (Multi-user Droplet Combustion Facility)
* SPICE (Smoke Point In Co-flow Experiment)
* SAFFIRE I–VI (Orbital Sciences Cygnus Resupply Vehicles)
* SAME (Spacecraft Fire Smoke Detection)

Every normalized record retains its physical experiment ID, flight mission, hardware platform, primary DOI, and raw sensor channels.

---

### 21.19 Validity Pillar 2: Rejection of Universal Combustion Predictors
FLARE-X enforces strict separation of physical combustion mechanisms:
* **SPICE Engine:** Gaseous flame length and laminar smoke points.
* **FLEX Engine:** Droplet extinction diameter and burning rate constants.
* **BASS-II Engine:** Solid fuel flammability boundaries, spread rates, and low-flow extinction.
* **SAFFIRE Engine:** Microgravity compartment-scale fire spread and pressure rise context.
* **SAME Engine:** Aerosol optical density and particulate distribution.

---

### 21.20 Validity Pillar 3: Honest, Grouped Model Validation
Machine learning models avoid inflated synthetic metrics:
* Evaluated against standard baseline models (Dummy Majority, Logistic Baseline).
* Evaluated strictly with **Group-Aware Validation (`StratifiedGroupKFold`)** grouped on physical NASA test/sample run.
* Report rigorous, task-specific metrics:
  * Regression (SPICE): Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), Coefficient of Determination ($R^2$).
  * Classification (BASS-II / FLEX): Balanced Accuracy, F1-Score, Brier Calibration Score.
* Documented via standardized **Model Cards** displaying training manifests, error distributions, and performance limitations.

---

### 21.21 Validity Pillar 4: Strict Leakage Prevention
FLARE-X architecture guarantees zero data leakage:
* No frames or video sequences from the same physical burn are split across train and test partitions.
* Normalization and pre-processing parameters are fitted strictly on training folds.
* No hyperparameter tuning or feature selection against held-out validation sets.

---

### 21.22 Validity Pillar 5: Multi-Factor Uncertainty Representation
FLARE-X refuses to output misleading point estimates or single synthetic "AI confidence" scores. Outputs expose:
1. **Statistical Prediction Intervals:** Parameter uncertainty ($\pm 95\%$ confidence bounds).
2. **Calibrated Class Probabilities:** Isotonic/Platt calibrated outcome probabilities.
3. **Empirical Domain Support:** `INSIDE`, `NEAR BOUNDARY`, or `OUTSIDE`.
4. **Evidence Distance Metric:** Numerical distance in normalized physical space to closest flight tests.

---

### 21.23 Validity Pillar 6: Operational Envelope Guard
A machine learning model with $95\%$ cross-validation accuracy remains fundamentally invalid when predicting outside its training distribution. The Envelope Guard prevents irresponsible extrapolation by enforcing automatic abstention.

---

### 21.24 Validity Pillar 7: Epistemic Claim Differentiation
Every sentence and UI component is tagged with strict epistemic status badges:
* `NASA OBSERVATION`: Direct, ground-truth measurement from flight telemetry.
* `MODEL INFERENCE`: Output generated by a validated quantitative machine learning model.
* `AI SYNTHESIS`: Natural-language contextual summary generated by the agentic orchestrator.
* `LIMITATION`: Explicit caveat detailing experimental mismatch, sparse density, or lack of NASA data.

---

### 21.25 Validity Pillar 8: Graceful Architectural Degradation
* If ML inference fails $\to$ Ingested NASA flight evidence and empirical tables remain fully searchable.
* If LLM orchestration fails $\to$ Algorithmic $k$-NN search and deterministic physics models function uninterrupted.
* If a scenario is out-of-domain $\to$ Prediction is withheld, but closest NASA tests and historical papers are surfaced.
* If contradictory flight records exist $\to$ System explicitly flags the empirical contradiction rather than hallucinating consensus.

---

### 21.26 The Flagship Validity Demonstration Moment
During live presentation or video evaluation, **deliberately push an input slider outside the NASA empirical flight domain**.

Show the system:
1. Flag the scenario as `OUTSIDE EXPERIMENTAL DOMAIN`.
2. Explicitly withhold the flammability prediction (`prediction: null`).
3. Display the exact reason (*"Requested flow velocity 55 cm/s exceeds NASA BASS-II flight envelope of 0–35 cm/s"*).
4. Direct the user to the closest empirical burns on record.

> **Demonstrating that the system knows when NOT to predict establishes higher technical validity than boasting high accuracy on a toy dataset.**

---

### 21.27 Technical Inspection Arsenal
Behind the intuitive UI, technical judges have one-click access to:
* Complete Model Cards (architectures, loss functions, hyperparameters).
* Cross-validation confusion matrices and residual plots.
* Full training manifest lists referencing specific NASA flight tests.
* Complete API schema documentation.

---

## 21.28 Criterion 4 — RELEVANCE

Relevance measures responsiveness to the Space Apps challenge prompt, challenge completeness, and usability.

### 21.29 Challenge-to-Product Traceability Mapping
Challenge #08 ("Flame in Freefall") requires teams to address fundamental microgravity fire dynamics using NASA datasets.

| Challenge Need | FLARE-X Subsystem | Direct Operational Capability |
| :--- | :--- | :--- |
| **Find microgravity research** | Evidence Scout | Semantic and parameter-filtered retrieval across PSI and NTRS databases. |
| **Rank relevant tests** | Scientific Ranker | Ranks spaceflight tests by physical parameter similarity and material equivalence. |
| **Compare experiments** | Comparison Workspace | Side-by-side delta table comparing test conditions, fuel geometries, and outcomes. |
| **Summarize evidence** | Scientific Synthesizer | Evidence-bounded summarization anchored strictly to cited test accessions. |
| **Interpret physical results** | Quantitative Engine | Evaluates flame length, extinction thresholds, and smoke emission characteristics. |
| **Apply AI meaningfully** | Bounded Orchestrator | Finite-State Machine controlling parsing, validation, and zero-hallucination verification. |
| **Unify NASA investigations** | Unified Evidence Schema | Normalizes heterogeneous records from BASS-II, FLEX, SPICE, SAFFIRE, and SAME. |
| **Support spacecraft fire safety** | Exploration Atmosphere Module | Models flammability shifts under Artemis habitat atmospheres ($34\%\text{ O}_2$). |
| **Ensure scientific integrity** | Envelope Guard & Provenance | Prevents extrapolation and provides direct NASA DOI resolution. |

---

### 21.30 Distinct Advantage Over Document Chatbots
Document chatbots simply extract text strings from PDFs. They cannot determine if a $10\text{ mm}$ PMMA sphere is physically comparable to a $6.35\text{ mm}$ cylinder, calculate flammability boundary distances, or enforce boundary abstention.

---

### 21.31 Distinct Advantage Over Pure Machine Learning Models
An isolated script predicting flame length solves one narrow calculation. FLARE-X surrounds specialized quantitative models with discovery, ranking, parameter matching, envelope safety boundaries, and claim-level verification.

---

### 21.32 Distinct Advantage Over Static Data Dashboards
A static dashboard requires the researcher to manually locate relevant data points. FLARE-X takes the user's specific operational scenario, searches multi-dimensional parameter space, executes compatible models, and checks empirical domain bounds dynamically.

---

### 21.33 Mitigating Relevance Scope-Creep
Every proposed capability must answer a single question:  
*"Does this directly help a user find, rank, compare, summarize, or interpret NASA combustion flight evidence?"*  
Non-essential features (e.g., generic chatbots, complex 3D rendering engines, decorative animations) are omitted to protect the core scientific value proposition.

---

### 21.34 The Flagship Relevance Workflow
The Analyze workspace demonstrates complete challenge fulfillment in one continuous screen flow:
$$\text{Natural Scenario Input} \longrightarrow \text{Ranked NASA Flight Tests} \longrightarrow \text{Side-by-Side Comparison} \longrightarrow \text{Physical Model Result} \longrightarrow \text{Bounded Synthesis} \longrightarrow \text{Direct NASA DOI}$$

---

## 21.35 Criterion 5 — PRESENTATION

Presentation evaluates how effectively and cleanly the team communicates the project's vision, problem, and value within strict time constraints.

---

### 21.36 The Universal Presentation Rule
The presentation must follow one continuous, unbroken narrative:
```text
NASA has decades of microgravity flight data
                    │
                    ▼
Finding and comparing relevant evidence is fragmented and difficult
                    │
                    ▼
FLARE-X structures the user's research inquiry
                    │
                    ▼
Retrieves and ranks the true matching spaceflight burns
                    │
                    ▼
Maps the scenario against the empirical flight envelope
                    │
                    ▼
Allows interactive counterfactual exploration
                    │
                    ▼
Refuses to predict when data is absent
                    │
                    ▼
Traces every insight directly back to NASA flight telemetry
```

---

### 21.37 The Pitch Hook
* **Recommended Opening:**  
  *"NASA has accumulated over twenty years of combustion flight experiments aboard the Space Shuttle, the ISS, and Cygnus spacecraft. The challenge is not a lack of data. The challenge is knowing which historical spaceflight test actually applies to the specific fire scenario you are designing for."*
* **Prohibited Opening:**  
  *"Hello judges, we built an AI-powered platform using advanced machine learning..."*

---

### 21.38 The Memorable Thesis Statement
> **"FLARE-X knows when not to predict."**  
*(Six words that communicate AI responsibility, scientific validity, innovation, and trust).*

---

### 21.39 240-Second Prescreening Video Alignment
The 4-minute prescreening presentation maps directly to the five judging criteria:

| Segment | Duration | Primary Criteria Targeted | Operational Script Focus |
| :--- | :---: | :--- | :--- |
| **WHO** | 0:00–0:45 (45s) | **Presentation + Credibility** | Team introduction, roles, challenge orientation, and mission thesis. |
| **WHY** | 0:45–1:45 (60s) | **Impact + Relevance** | Physics of microgravity fire; fragmentation of BASS, FLEX, SPICE, and SAFFIRE data across static archives. |
| **WHAT** | 1:45–2:45 (60s) | **Creativity + Relevance** | Ingesting scenario, ranking NASA tests, 2D Support Map, Envelope Guard, and specialized models. |
| **SO WHAT / NEXT** | 2:45–4:00 (75s) | **Validity + Impact + Feasibility** | Moving oxygen slider, crossing boundary, automated model abstention, claim-level provenance, and open-source validation. |

---

### 21.40 WHO Segment (0:00–0:45)
* Establish team identity, institutional affiliation, and multidisciplinary roles.
* Introduce the core mission: bridging the gap between raw NASA microgravity flight archives and actionable spacecraft fire-safety analysis.

### 21.41 WHY Segment (0:45–1:45)
* Visual: Multi-investigation dispersal map showing BASS-II, FLEX, SPICE, SAFFIRE, and SAME records in isolated silos.
* Core narrative: Spacecraft life-support systems are adopting exploration atmospheres ($34\%\text{ O}_2$). Understanding anomalous material flammability requires navigating dozens of isolated technical papers and disparate flight experiments. FLARE-X solves this evidence retrieval bottleneck.

### 21.42 WHAT Segment (1:45–2:45)
* Demonstrate the Analyze workspace.
* Show the 2D Support Map and Envelope Guard in action.
* Key narration: *"Unlike generic LLMs that hallucinate flammability numbers, FLARE-X routes queries to specialized physical models and verifies empirical flight boundaries before generating inferences."*

### 21.43 SO WHAT / NEXT Segment (2:45–4:00)
* Execute the counterfactual oxygen sweep across flammability extinction limits.
* Drag input into unsupported territory: demonstrate **Envelope Guard Refusal**.
* Open the Slide-Over Provenance Inspector, tracing the claim to a NASA PSI accession and DOI.
* Concluding statement: *"Our objective is not to replace combustion scientists. It is to make NASA's accumulated flight knowledge faster to find, safer to interpret, and defensible to reuse."*

---

## 21.44 Master Judging Proof Stack

| Criterion | Strategic Claim | Tangible Visible Proof in Demo |
| :--- | :--- | :--- |
| **Impact** | Makes multi-decade NASA flight records instantly accessible and reusable. | Live query transforming natural text into ranked, structured NASA spaceflight burns. |
| **Creativity** | Evidence-bounded intelligence with active domain boundary awareness. | Interactive 2D Support Map showing user point, NASA test points, and automated abstention. |
| **Validity** | Defensible data science, leak-free validation, and honest uncertainty bounds. | Model Cards, Grouped CV benchmarks, calibrated confidence intervals, and DOI links. |
| **Relevance** | Comprehensive alignment with the "Flame in Freefall" challenge brief. | Unified schema indexing BASS-II, FLEX, SPICE, SAFFIRE, and SAME flight programs. |
| **Presentation** | Concise, compelling, and free of hype. | Single, continuous user journey flowing naturally from inquiry to verified source. |

---

## 21.45 Internal Scoring Readiness Target

| Criterion | Readiness Assessment | Verification Deliverable |
| :--- | :---: | :--- |
| **Impact** | **5 / 5** | Measurable workflow reduction; solves real aerospace research friction. |
| **Creativity** | **5 / 5** | Envelope Guard, Counterfactual Swarms, and multi-family physical routing. |
| **Validity** | **5 / 5** | Strict Grouped CV, baseline benchmarks, domain guard, and claim provenance. |
| **Relevance** | **5 / 5** | Full integration of NASA flight datasets matching all challenge requirements. |
| **Presentation** | **5 / 5** | Clear 4-minute narrative structure, high-contrast aerospace UI, zero jargon fluff. |

---

## 21.46 Common Failure Modes & Proactive Mitigations

### Potential Impact Pitfalls
* *Pitfall:* Presenting a feature-heavy dashboard without demonstrating a concrete workflow improvement.
* *Mitigation:* Focus on the exact time-to-evidence acceleration achieved when investigating material flammability in exploration atmospheres.

### Potential Creativity Pitfalls
* *Pitfall:* Judges mistaking the platform for a standard RAG document chatbot.
* *Mitigation:* Immediately demonstrate the Experimental Support Map, multi-family model routing, and the active abstention mechanism.

### Potential Validity Pitfalls
* *Pitfall:* Technical judges challenging model accuracy claims, data splits, or physical assumptions.
* *Mitigation:* Show explicit Model Cards with `StratifiedGroupKFold` splits, majority baseline comparisons, calibrated confidence intervals, and Envelope Guard boundaries.

### Potential Relevance Pitfalls
* *Pitfall:* Getting distracted by decorative 3D animations or generic chatbot features.
* *Mitigation:* Strictly adhere to the core challenge mandate: finding, ranking, comparing, and interpreting microgravity combustion evidence.

### Potential Presentation Pitfalls
* *Pitfall:* Information overload, excessive technical jargon, or chaotic multi-window demos.
* *Mitigation:* Follow one prefilled flagship scenario from initial question to empirical NASA DOI verification in under two minutes.

---

## 21.47 Master Q&A Defense Playbook

### Q1: "Why not just use ChatGPT or Claude over the NASA PDFs?"
> **Answer:**  
> *"Document retrieval models identify text keywords, but they lack physical comprehension. They cannot verify whether two flight tests share identical ventilation velocities, determine if a solid fuel model applies to a gaseous jet, or calculate physical flammability limits. Most critically, general LLMs extrapolate dangerously when data is missing. FLARE-X enforces physical family routing, checks empirical boundary support, and withholds predictions when NASA data is absent."*

---

### Q2: "Why not simply search NASA Physical Sciences Informatics (PSI) directly?"
> **Answer:**  
> *"NASA PSI is the authoritative data repository, and FLARE-X builds upon it rather than replacing it. However, PSI is a static file catalog. Answering a specific fire safety question requires manually cross-referencing dozens of spreadsheets, flight logs, and technical reports across different missions. FLARE-X adds an intelligence layer: parameter matching, ranking, domain boundary validation, and provenance synthesis across investigations."*

---

### Q3: "How do you ensure users can trust machine learning predictions?"
> **Answer:**  
> *"We never present raw model outputs in isolation. Every quantitative model is validated via Grouped Cross-Validation to eliminate test leakage, benchmarked against baseline models, and restricted strictly to its empirical training domain by the Envelope Guard. Furthermore, the UI explicitly separates NASA empirical observations from model inferences and surfaces multi-dimensional prediction intervals."*

---

### Q4: "What occurs when a user queries conditions NASA has never tested?"
> **Answer:**  
> *"FLARE-X refuses to output a quantitative prediction. The Experimental Envelope Guard intercepts the query, flags the scenario as `OUTSIDE EXPERIMENTAL DOMAIN`, displays the missing variable ranges, and surfaces the closest historical NASA flight experiments on record."*

---

### Q5: "What is the core technical innovation of FLARE-X?"
> **Answer:**  
> *"The innovation is the evidence-bounded scientific architecture: combining physical combustion family routing, multi-dimensional boundary validation via the Envelope Guard, real-time counterfactual evidence re-ranking, and node-level provenance connecting every claim to an authoritative NASA flight record."*

---

### Q6: "Does this replace spacecraft fire-safety engineers or flight controllers?"
> **Answer:**  
> *"Absolutely not. FLARE-X is a decision-support and research acceleration platform designed for materials scientists and mission architects. It surfaces evidence, highlights uncertainty, and accelerates analysis, but operational fire safety decisions remain strictly with certified human engineers."*

---

### Q7: "Why deploy multiple specialized models instead of a single foundation model?"
> **Answer:**  
> *"Because microgravity combustion physics varies fundamentally across physical regimes: solid fuel surface spread in BASS-II obeys different governing equations than liquid droplet extinction in FLEX or gaseous jet diffusion in SPICE. A single universal model would be scientifically unsound. FLARE-X unifies records at the data schema level while deploying specialized models matched to specific physical phenomena."*

---

### Q8: "What if your machine learning accuracy isn't state-of-the-art?"
> **Answer:**  
> *"FLARE-X’s value proposition does not depend on claiming an unprecedented ML benchmark. Our quantitative models demonstrate statistically significant improvements over standard baselines under honest grouped evaluation. More importantly, FLARE-X provides immense utility through structured evidence retrieval, parameter comparison, and provenance tracing even when a predictive model is withheld."*

---

### Q9: "Why focus strictly on NASA datasets?"
> **Answer:**  
> *"The Space Apps challenge specifically challenges teams to utilize NASA's open science archives. NASA PSI represents over twenty years of unique spaceflight combustion research that cannot be replicated in terrestrial laboratories. FLARE-X maximizes the return on NASA's scientific investment by making this archive systematically searchable and actionable."*

---

## 21.48 Criterion-Specific One-Liners (Team Rehearsal)

* **Impact:** *"FLARE-X drastically compresses the timeline from a spacecraft fire safety question to actionable NASA flight evidence."*
* **Creativity:** *"FLARE-X combines family-aware scientific intelligence with an epistemic envelope guard that knows when NASA data is too sparse to justify a prediction."*
* **Validity:** *"Every quantitative output is bound by leak-free grouped validation, calibrated prediction intervals, and traceable NASA flight records."*
* **Relevance:** *"FLARE-X directly ingests, structures, ranks, compares, and interprets NASA combustion flight data in complete alignment with the challenge brief."*
* **Presentation:** *"A single, intuitive workflow guides the user from scenario inquiry to ranked flight data, flammability boundaries, and verified NASA DOIs."*

---

## 21.49 Master Narrative Summary

> **NASA has accumulated decades of microgravity combustion flight experiments, but answering a modern spacecraft fire-safety question still requires manually navigating heterogeneous archives and technical reports. FLARE-X transforms this static catalog into evidence-bounded scientific intelligence. It interprets the user's operational scenario, retrieves and ranks relevant NASA flight burns, routes queries to specialized physical models, and checks whether environmental conditions lie within NASA's empirical flight envelope.**  
> **Researchers can interactively vary oxygen concentrations or ventilation flows to observe real-time flammability shifts. When data runs out, FLARE-X halts prediction, and every scientific conclusion remains traceable to peer-reviewed NASA observations.**

---

## 21.50 Phase 21 Acceptance Checklist

| Requirement | Implementation Verification | Status |
| :--- | :--- | :---: |
| **Official 2026 Criteria Confirmed** | Impact, Creativity, Validity, Relevance, and Presentation codified. | ✅ |
| **Impact Mapping** | Friction reduction, research use-cases, and beneficiaries defined. | ✅ |
| **Creativity Mapping** | Envelope Guard, Counterfactual Swarms, and family routing formalized. | ✅ |
| **Validity Mapping** | Grouped CV, leakage controls, uncertainty bounds, and model cards detailed. | ✅ |
| **Relevance Mapping** | Direct challenge-to-product functional traceability matrix completed. | ✅ |
| **Presentation Mapping** | 240-second prescreening video and slide narrative aligned with rubric. | ✅ |
| **Master Judging Matrix** | Core scoring backbone established. | ✅ |
| **Q&A Defense Playbook** | 9 high-probability judge inquiries and authoritative responses locked. | ✅ |
| **Judging Risks & Mitigations** | Comprehensive pitfall mitigation matrix established. | ✅ |
| **Rehearsal Talking Points** | Criterion-specific one-liners codified for team pitch rehearsals. | ✅ |
| **Master Judging Narrative** | Unified, non-hyped elevator pitch finalized. | ✅ |

---

## ✅ Phase 21 Status: COMPLETE

The complete **Judging-Criteria Mapping** for FLARE-X is formally ratified, locked, and recorded.

*Next Phase:* **Phase 22 — Limitations & Scientific Ethics** (formalizing epistemic boundaries, explicit claims restrictions, uncertainty disclosure protocols, dataset bias documentation, and technical documentation limitations).
