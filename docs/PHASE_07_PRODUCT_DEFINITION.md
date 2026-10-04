# Phase 7 — FLARE-X Product Definition

> **Status:** ✅ COMPLETE  
> **Challenge:** Flame in Freefall (NASA Space Apps Challenge 2026)  
> **Product Name:** **FLARE-X**  
> **Expansion:** Fire Laboratory Analysis, Reasoning & Evidence Explorer  
> **Product Category:** Evidence-grounded scientific decision-support and exploration platform for NASA microgravity combustion research  
> **Core Deliverable:** Freeze product scope, target users, user journey, system contracts, UI architecture, and pitch definitions.

---

## 7.1 Final Product Identity & Expansion

* **Product Name:** **FLARE-X**
* **Official Expansion:** **Fire Laboratory Analysis, Reasoning & Evidence Explorer**  
  *Why this expansion fits:*
  - **Analysis** $\rightarrow$ Specialized quantitative ML models (BASS-II, FLEX, SPICE).
  - **Reasoning** $\rightarrow$ Evidence interpretation & comparative domain reasoning.
  - **Evidence** $\rightarrow$ Traceable NASA experiment provenance (NTRS reports, PSI DOIs).
  - **Explorer** $\rightarrow$ Interactive multidimensional scenario dashboard.

---

## 7.2 Final Product Category

FLARE-X হলো:
> **An evidence-grounded scientific decision-support and exploration platform for NASA microgravity combustion research.**

*Clarifying what it is NOT:*
- Chatbot না
- শুধু ML model না
- শুধু search engine না
- শুধু dashboard না
- শুধু database না  
*বরং এই সবকিছুর coordinated scientific system।*

---

## 7.3 One-Line Product Pitch & Taglines

* **Primary One-Line Pitch (For Project Page & Presentations):**  
  > *"FLARE-X turns NASA’s scattered microgravity combustion experiments into searchable, comparable, model-assisted, and evidence-traceable fire-safety intelligence."*
* **Punchy Tagline (For Visuals & Video Title Cards):**  
  > *"From NASA fire experiments to evidence-backed spaceflight fire intelligence."*
* **Alternative Taglines:**
  - *"Search the evidence. Model the behavior. Trust the source."*
  - *"Understand the fire. Trace the evidence."*

---

## 7.4 Target User Hierarchy & Primary Persona

আমরা "everyone interested in space" target করব না।

### Primary Target User
> **A researcher or engineer who needs to answer a specific microgravity combustion or spacecraft fire-safety question using NASA experimental evidence.**

### Secondary Users
| User Group | Primary Need from FLARE-X |
| :--- | :--- |
| **Combustion researchers** | Compare flight experiments across configurations |
| **Spacecraft safety researchers** | Identify flammability limits and relevant evidence |
| **Mission / systems engineers** | Understand condition-dependent behavior under exploration atmospheres |
| **Data scientists** | Explore structured NASA microgravity combustion data |
| **Students / researchers** | Learn microgravity combustion phenomena interactively |

---

## 7.5 Core User Problem

User-এর আসল situation:
> *"আমার একটা fire-related scientific question আছে। NASA-তে relevant experiments আছে, কিন্তু কোনটা relevant, কোন condition কাছাকাছি, কী result হয়েছিল, কী model apply করা যায়, আর evidence কতটা trustworthy সেটা দ্রুত বুঝতে চাই।"*

এই single problem থেকেই পুরো product journey তৈরি হয়েছে।

---

## 7.6 Canonical User Scenario (The Core Thread)

আমাদের demo, UX, architecture, এবং video সবখানে একটা consistent scenario ব্যবহার করা হবে:

* **Scenario:** A researcher wants to understand how oxygen concentration and airflow affect the combustion behavior of a polymer-like solid material in microgravity.
* **Input Query:**
  - Material: `PMMA` (cast polymer)
  - Oxygen: `18.0%`
  - Airflow: `15.0 cm/s`
  - Pressure: `101.3 kPa` (standard test pressure)
  - Flow direction: `opposed`
  - Core Question: *Will the flame sustain or extinguish, and which NASA experiments best support the answer?*

---

## 7.7 Complete End-to-End User Journey

```
1. Ask a question / define a scenario
                ↓
2. FLARE-X structures the parameters
                ↓
3. Identifies relevant experiment family (Solid / Droplet / Gas)
                ↓
4. Searches NASA evidence (Structured + Semantic)
                ↓
5. Ranks experiments by scientific relevance (Multidimensional distance)
                ↓
6. Runs appropriate quantitative model (BASS-II / FLEX / SPICE)
                ↓
7. Checks experimental-domain coverage (Envelope Guard)
                ↓
8. Compares supporting experiments (Side-by-side delta)
                ↓
9. Generates evidence-grounded interpretation (Bounded LLM synthesis)
                ↓
10. Shows confidence, limitations, and sources (NTRS links & DOIs)
                ↓
11. User changes conditions (Oxygen / flow decrement sliders)
                ↓
12. FLARE-X performs counterfactual comparison (Extinction boundary transition)
```

---

## 7.8 Product Input Modes (Dual Input Architecture)

* **Mode A — Structured Scenario:** User manually sets Combustion Family, Material/Fuel, Oxygen, Pressure, Airflow, Flow Direction, Geometry, Suppressant, and Question Type. (Scientifically clean, demo-friendly).
* **Mode B — Natural Language:** User types: *"Find NASA experiments about PMMA burning at reduced oxygen under forced airflow."* FLARE-X parses and populates the structured parameters.
* **Why both matter:** Form alone is technical but rigid; chatbot alone is flexible but ambiguous. Combining them allows natural language entry with explicit parameter inspection and correction.

---

## 7.9 Seven Core Product Modules

| Module | Core Purpose |
| :--- | :--- |
| **1. Scenario Lab** | Define and query environmental and material conditions dynamically. |
| **2. Evidence Search** | Hybrid retrieval across structured parameters and NTRS report text. |
| **3. Scientific Ranker** | Prioritize experiments using physical similarity, family penalties, and relevance. |
| **4. Model Lab** | Run compatible quantitative models (BASS-II classifier, SPICE regressor, FLEX boundary). |
| **5. Experiment Compare**| Side-by-side parameter and outcome comparison across flight runs. |
| **6. Envelope Guard** | Enforce empirical bounds (`Inside Range`, `Limited Support`, `Outside Range`). |
| **7. Evidence Explorer**| Inspect source report IDs, page numbers, measurement methods, and DOIs. |

---

## 7.10 Product Modes

1. **Explore Mode:** Browse NASA combustion evidence by material, platform, or investigation. (Cards, filters, charts, experiment atlas).
2. **Analyze Mode:** Enter a 4-parameter scenario and run models. (Ranked experiments, model prediction, confidence, envelope status, explanation).
3. **Compare Mode:** Compare conditions (e.g. 18% $O_2$ vs. 21% $O_2$) or experiments (Experiment A vs. Experiment B) with parameter, model, and confidence deltas.

---

## 7.11 Result Card Structure & Physical Transparency

FLARE-X explicitly rejects treating probability as absolute truth. If a model predicts $P(\text{extinction}) = 0.73$, the UI states: *"Model estimates higher likelihood of extinction within tested conditions,"* not *"The fire will extinguish."*

```
┌────────────────────────────────────────────────────────────────────────┐
│ FLARE-X RESULT CARD                                                    │
├────────────────────────────────────────────────────────────────────────┤
│ COMBUSTION REGIME:      Sustained propagation likely (in tested family)│
│ MODEL CONFIDENCE:       82% (Calibrated Gradient Boosting)             │
│ EXPERIMENTAL MATCH:     High Similarity to BASS2_B10 & BASS2_B11       │
│ DOMAIN STATUS:          Inside tested range [15.0%, 34.0%]             │
│ PRIMARY NASA EVIDENCE:  BASS-II (PSI-25, NASA/TM-2017-219503)          │
│ SUPPORTING CONTEXT:     SAFFIRE-I (Large-scale burn S1)                │
│ IMPORTANT DIFFERENCE:   Sample thickness differs (0.1 mm vs 1.0 mm)    │
│ [VIEW NASA EVIDENCE]    [INSPECT MODEL METRICS]                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 7.12 Value Proposition & What FLARE-X is NOT

* **Primary Value Proposition:**  
  > *"FLARE-X reduces the friction between a fire-safety question and the NASA experimental evidence needed to answer it."*
* **Secondary Value Proposition:**  
  > *"It helps users distinguish between what NASA data support strongly, what they support weakly, and what they do not support at all."*

### Explicit Product Non-Goals
* ❌ **NOT Fire Certification Software:** Does not certify spacecraft materials or replace NASA-STD-6001B.
* ❌ **NOT Emergency Response Software:** Does not issue real-time operational emergency flight commands.
* ❌ **NOT a Universal Combustion Simulator:** Does not simulate arbitrary, ungrounded fluid dynamics.
* ❌ **NOT an Autonomous Mission Control System:** Does not replace flight safety engineers.
* ❌ **NOT a Generic Chatbot:** Does not generate unverified text without citations.

---

## 7.13 Feature Prioritization: Core vs. Differentiator vs. Stretch

```
┌────────────────────────────────────────────────────────────────────────┐
│ CORE (Must work even without LLM or ML)                                │
│ • Scenario input & NLP parser                                          │
│ • NASA evidence search & physical relevance ranking                    │
│ • Experiment side-by-side comparison                                   │
│ • Evidence provenance & resolvable NTRS links                          │
│ • Experimental Envelope Guard bounding box check                       │
│ • One or more quantitative models (BASS-II, SPICE, FLEX)               │
├────────────────────────────────────────────────────────────────────────┤
│ DIFFERENTIATOR (Scientifically Stronger)                               │
│ • Model routing across combustion families                             │
│ • Counterfactual oxygen & airflow parameter sweeps                     │
│ • Bounded explainability & numerical hallucination auditing            │
│ • Knowledge graph relations & research gap detection                   │
├────────────────────────────────────────────────────────────────────────┤
│ EXPERIENCE (Visual Excellence)                                         │
│ • Aerospace mission-control dark mode (Orbitron / JetBrains Mono)     │
│ • Interactive 2D flammability boundary slice canvas with flight points │
│ • Sigmoidal sweep curves with extinction safety margin gauge           │
├────────────────────────────────────────────────────────────────────────┤
│ STRETCH (Ambitious Extras)                                             │
│ • Computer vision flame-front tracking on raw BASS/SAFFIRE video       │
│ • Multimodal aerosol & smoke detector intelligence module              │
│ • Downloadable automated engineering safety briefings                  │
└────────────────────────────────────────────────────────────────────────┘
```

*Architectural Resilience Guarantee:* If external LLM APIs fail, the core system continues to filter, rank, run models, compare conditions, and display verified evidence using deterministic templates.

---

## 7.14 Video 1 Pitch Wording (Locked for Prescreening)

* **Official Pitch Narrative (WHAT | Block 3):**  
  > *"FLARE-X is an evidence-grounded scientific AI platform designed to turn NASA microgravity-combustion experiments into searchable and comparable fire-safety intelligence. A user can enter a spacecraft fire scenario, and FLARE-X identifies the relevant experiment family, retrieves and ranks similar NASA experiments, runs an appropriate quantitative model where supported, checks whether the scenario lies inside NASA-tested conditions, and explains the result together with confidence, limitations, and source evidence."*
* **15-Second Intro Cut:**  
  > *"FLARE-X lets users enter a microgravity fire scenario, finds and ranks the most relevant NASA experiments, runs the appropriate scientific model, and explains the result with confidence, limitations, and full evidence traceability."*
* **5-Second Title Card:**  
  > *"FLARE-X turns NASA fire experiments into explainable safety intelligence."*

---

## 7.15 Phase 7 Acceptance Gate

- [x] **Product Name & Expansion Locked:** FLARE-X (Fire Laboratory Analysis, Reasoning & Evidence Explorer).
- [x] **Category Defined:** Evidence-grounded scientific decision-support & exploration platform.
- [x] **Primary User Specified:** Technical aerospace fire-safety researcher / mission engineer.
- [x] **12-Step User Journey Mapped:** From query to counterfactual comparison.
- [x] **Seven Core Modules Formalized:** Scenario Lab, Evidence Search, Ranker, Model Lab, Compare, Envelope Guard, Explorer.
- [x] **Dual Input Modes Defined:** Structured scenario forms + conversational NLP parser.
- [x] **Product Boundaries & Non-Goals Established:** Explicit refusal of certification, emergency commands, and generic chat.
- [x] **Feature Tiering Formalized:** Core, Differentiator, Experience, Stretch.
- [x] **Video Pitch Scripts Locked:** Full pitch, 15-second intro, and 5-second title card formulations verified.

---

## ✅ Phase 7 Status: COMPLETE

The product vision, user journey, modules, and boundary guarantees are formally locked.

We now proceed to **Phase 8: Agentic Architecture & Orchestration Flow**.
