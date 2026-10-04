# Phase 3 — Problem Definition: FLARE-X

> **Status:** ✅ COMPLETE  
> **Challenge:** Flame in Freefall (NASA Space Apps Challenge 2026)  
> **Deliverable Alignment:** October 7 Prescreening Video (Block 2: WHY) & Technical Architecture Baseline  
> **Discipline:** Zero-Fabrication, Aerospace Engineering Rigor, Evidence-Grounded Scope

---

## 3.1 The Root Problem

The fundamental problem is not lack of data.

It is:
> **NASA has accumulated valuable microgravity-combustion evidence across many investigations, but that evidence is fragmented across experiments, datasets, reports, environmental conditions, fuel/material types, measurement methods, and scientific formats. This makes it difficult for a user to rapidly determine which experiments are relevant to a specific question, how comparable those experiments actually are, what patterns emerge across them, and how strongly the available evidence supports a safety-relevant interpretation.**

That is the problem FLARE-X exists to solve.

---

## 3.2 The Four Problem Layers

```
┌────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: DISCOVERY PROBLEM                                             │
│ Users don't know which NASA investigations, IDs, or reports matter     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ leads to
┌───────────────────────────────────▼────────────────────────────────────┐
│ LAYER 2: COMPARABILITY PROBLEM                                         │
│ Experiments differ in geometry, pressure, flow, and sample type        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ leads to
┌───────────────────────────────────▼────────────────────────────────────┐
│ LAYER 3: INTERPRETATION PROBLEM                                        │
│ Raw outcomes (extinction, spread rate) require domain reasoning        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ leads to
┌───────────────────────────────────▼────────────────────────────────────┐
│ LAYER 4: TRUST & BOUNDING PROBLEM                                      │
│ AI must remain traceable, honest about uncertainty, and bounded        │
└────────────────────────────────────────────────────────────────────────┘
```

### Layer 1 — Discovery Problem
A user may know the question: *"How does reduced oxygen affect flame behavior for a solid material under forced airflow?"*  
But not know:
- Which NASA investigation contains relevant experiments (BASS, BASS-II, SAFFIRE, DARTFire).
- Which experiment IDs matter.
- Which reports contain the results.
- Whether another investigation studied similar conditions.
- Which results are actually closest to the requested scenario.

*First problem:* **Finding the right evidence.**

### Layer 2 — Comparability Problem
Finding two experiments does not mean they are scientifically comparable. For example:
- **Experiment A:** Material: PMMA | $O_2$: 18% | Flow: 10 cm/s | Pressure: 101.3 kPa | Geometry: flat sample
- **Experiment B:** Material: PMMA | $O_2$: 18% | Flow: 25 cm/s | Pressure: 56.5 kPa | Geometry: cylindrical rod

An ordinary search engine may call both highly relevant. A scientific system must recognize: *Same material and oxygen, but significant environmental and geometric differences.*  
*Second problem:* **Understanding how comparable the evidence really is.**

### Layer 3 — Interpretation Problem
Even after retrieving an experiment, raw results don't automatically become insight. A user may see:
`Flame spread = X | Extinction occurred at Y | Temperature = Z`  
But still need to understand:
- Why did this experiment behave differently?
- Which condition most likely mattered?
- Is this observation consistent with other NASA experiments?
- Is this scenario approaching an extinction boundary?
- Does the evidence support the requested scenario strongly or weakly?

*Third problem:* **The system needs to interpret evidence rather than merely expose it.**

### Layer 4 — Trust Problem
AI creates another problem. Suppose the system says: *"This scenario has high combustion risk."* Immediately we need to know:
- Based on what? Which NASA experiments?
- What variables matched? What variables differed?
- Was the scenario actually within NASA-tested conditions?
- Did the ML model interpolate or extrapolate?
- How reliable was the prediction?
- Was an LLM generating language beyond what the evidence supports?

*Fourth problem:* **Scientific interpretation must remain traceable, bounded, and honest about uncertainty.**

---

## 3.3 The Complete Problem Chain

```
DECADES OF NASA
COMBUSTION RESEARCH
        │
        ▼
Multiple investigations
Different conditions
Different formats
Different fuels/materials
Different outputs
        │
        ▼
INFORMATION FRAGMENTATION
        │
        ├──────────────┐
        ▼              ▼
Hard to find      Hard to compare
        │              │
        └──────┬───────┘
               ▼
         Hard to interpret
               │
               ▼
   Slow / difficult evidence synthesis
               │
               ▼
 Difficult to derive transparent
     safety-relevant insight
```

FLARE-X attacks the **fragmentation $\rightarrow$ understanding** gap.

---

## 3.4 Target User Personas & Primary User Story

| User Persona | Primary Problem | What FLARE-X Provides |
| :--- | :--- | :--- |
| **Combustion researcher** | Locating / comparing relevant experiments | Experiment discovery + parameter comparison |
| **Spacecraft fire-safety researcher** | Connecting conditions to observed behavior | Evidence synthesis + boundary analysis |
| **Mission / systems engineer** | Understanding safety implications | Interpretable scenario analysis + envelope guard |
| **Data scientist / analyst** | Discovering usable experimental relationships | Structured data + models + honest CV metrics |
| **Student / scientist** | Understanding microgravity combustion research | Visual exploration + citations + explanations |

### Primary Persona
**A technical researcher or engineer trying to answer a specific microgravity fire-safety question using NASA experimental evidence.**

### Primary User Story
> *"As a researcher or engineer, I want to describe a fire-related scenario or scientific question and quickly discover the most relevant NASA microgravity-combustion experiments, compare their conditions and results, understand what the evidence suggests, see how confident that interpretation is, and trace every conclusion back to its source."*

---

## 3.5 Primary Canonical Scenario

Instead of talking abstractly, FLARE-X uses one canonical scenario through architecture, UI, video, and demo:

* **Scenario:** A researcher wants to understand how changing oxygen concentration and airflow affects combustion behavior for a polymer-like solid material in microgravity.
* **Input Query:**
  - Material: `PMMA` (cast polymer)
  - Oxygen: `18.0%`
  - Airflow: `15.0 cm/s`
  - Pressure: `101.3 kPa`
  - Core Question: *Will combustion remain sustained, and which NASA experiments provide the most relevant evidence?*
* **FLARE-X Response:**
  - Relevant NASA investigations: `BASS-II`, `SAFFIRE-I`
  - Closest experiments: `BASS2_B1` (5 cm/s, spread), `BASS2_B10` (15 cm/s, marginal), `BASS2_B12` (25 cm/s, extinction)
  - Observed behavior: Opposed-flow flame spread transitioning toward radiative extinction at low flow and blowoff at elevated flow.
  - Model analysis: `marginal_spread` / near boundary (Model CV: 79.31% grouped by report).
  - Inside tested domain: `YES` (bounded within training envelope).
  - Evidence sources: Resolvable NTRS citations (`NTRS 20210011385`, `NTRS 20160010041`).

---

## 3.6 Why the Existing Workflow Fails

```
CURRENT WORKFLOW (Fragmented & Manual)
Question → Search programs → Locate investigation → Find metadata → Open PDF reports
→ Understand variable definitions → Compare conditions manually → Find related experiments
→ Interpret scientific differences → Determine what applies.
*Problem: Scientific context is spread across too many manual, disconnected steps.*

FUTURE FLARE-X WORKFLOW (Compressed & Traceable)
Question / Scenario → FLARE-X → Relevant Evidence → Ranked Experiments
→ Scientific Comparison → Quantitative Analysis → Confidence / Limitations
→ Evidence-Backed Insight.
```

---

## 3.7 Multidimensional Information Fragmentation

1. **Experimental Fragmentation:** Separate flight programs (BASS, BASS-II, ACME, SAFFIRE, DARTFire).
2. **Parameter Fragmentation:** Divergent oxygen levels ($15\text{–}34\%$), pressures ($48\text{–}101\text{ kPa}$), flow velocities ($0\text{–}55\text{ cm/s}$), sample shapes (sheets, rods, slabs, fabrics).
3. **Outcome Fragmentation:** Divergent measurements (flame spread rate, ignition delay, extinction velocity, soot fraction, radiant flux).
4. **Format Fragmentation:** Data trapped in scanned PDF tables, text reports, raw CSVs, and video frames.
5. **Semantic Fragmentation:** Inconsistent column headers, unit conventions (psia vs. kPa vs. atm; in/s vs. cm/s), and measurement terminology.

---

## 3.8 Why Simple Search, Naive RAG, and Universal Models Fail

* **Why Search Fails:** Keyword search (`PMMA oxygen flame spread`) finds documents, but cannot determine scientific similarity (which test has the nearest Euclidean distance in $O_2$, flow, and pressure).
* **Why Normal RAG Fails:** A vector database retrieves text chunks, but cannot perform parameter comparison ($18\%\text{ vs. }19\% O_2$), compute regime boundaries, or check physical bounding boxes.
* **Why One Universal Model Fails:** Droplet combustion (FLEX) obeys $d^2$ evaporation physics, which is physically incompatible with solid polymer flame spread (BASS). A model merging them produces scientifically invalid results.
* **The Hidden Problem (Experimental Coverage):** Sometimes NASA has zero data for a query. Conventional AI generates an answer anyway; FLARE-X must explicitly flag **"Insufficient Evidence / Out of Domain"**.

---

## 3.9 Problem Hierarchy & Feature Prioritization

| Priority | Problem | System Requirement | Tier |
| :---: | :--- | :--- | :---: |
| **P0** | Relevant evidence is difficult to find | Intelligent Evidence Retrieval Engine | Core |
| **P0** | Experiments are difficult to compare | Parameter Normalization & Comparator | Core |
| **P0** | Findings are difficult to interpret | Domain-Bounded Scientific Interpreter | Core |
| **P0** | AI conclusions need provenance | Evidence Provenance & NTRS Linker | Core |
| **P1** | Experiments need relevance ranking | Multidimensional Relevance Ranker | Core / Differentiator |
| **P1** | Unsupported extrapolation must be detected | Experimental Envelope Guard | Differentiator |
| **P1** | Quantitative relationships are hidden | Machine Learning Regime Classifier | Differentiator |
| **P2** | Counterfactual exploration is difficult | 1D Parameter Sweep & Boundary Detector | Differentiator |
| **P2** | Research gaps are difficult to identify | Data Density / Sparse Region Warning | Differentiator |
| **P3** | Raw video/images need analysis | Multimodal Computer Vision | Stretch |
| **P3** | Interaction should be immersive | Interactive 2D/3D Flight Slice Visualizer | Experience |

---

## 3.10 Core System Principles

1. **The Prime Directive:**  
   > *"FLARE-X must never make it easier to generate a conclusion than to inspect the evidence supporting that conclusion."*
2. **Evidence before Eloquence:** Scientific correctness and data traceability over impressive LLM prose.
3. **Compare Conditions, Not Just Keywords:** True multidimensional physical similarity.
4. **Specialized Models over Universal Nonsense:** Segregate solid flame spread from liquid droplets and gaseous burners.
5. **Show Uncertainty & Refuse Unsupported Precision:** Honest grouped cross-validation metrics, majority baselines, and refusal outside empirical bounds.

---

## 3.11 Canonical Problem Statements (For All Uses)

* **Technical Formulation (For Specs & Architecture):**  
  > *"FLARE-X addresses the difficulty of transforming heterogeneous NASA microgravity-combustion experiments into fast, comparable, interpretable, and traceable scientific evidence. It is designed to help users identify the experiments most relevant to a fire-related question, compare experimental conditions and outcomes, apply appropriate quantitative analyses where supported, recognize the boundaries of available experimental evidence, and derive transparent fire-safety insights without separating conclusions from their NASA sources."*
* **Project Page Formulation (For NASA Space Apps Portal):**  
  > *"NASA has decades of microgravity-combustion evidence, but finding the right experiments, comparing their conditions, and interpreting their safety implications becomes increasingly difficult as the research grows. FLARE-X turns this distributed evidence into searchable, comparable, explainable, and traceable fire-safety intelligence."*
* **Pitch Opening Hook (October 7 Video 1):**  
  > *"NASA does not lack microgravity fire data. The challenge is turning decades of experiments into evidence humans can quickly find, compare, and trust."*
* **Official Tagline:**  
  > *"From scattered NASA combustion experiments to evidence-backed fire-safety intelligence."*

---

## 3.12 Phase 3 Acceptance Gate

- [x] **Exact Problem Formulated:** Defined as multi-layer information fragmentation and scientific synthesis gap.
- [x] **Four Layers Established:** Discovery, Comparability, Interpretation, and Trust.
- [x] **Primary User & Scenario Locked:** Technical researcher querying solid polymer flammability limits.
- [x] **Anti-Patterns Articulated:** Proven why simple search, naive RAG, and universal models fail.
- [x] **Hierarchy & Principles Locked:** P0–P3 priorities and *"Evidence before Eloquence"* rule established.
- [x] **Four Statement Variants Created:** Technical, Project Page, Pitch Hook, and Tagline.
