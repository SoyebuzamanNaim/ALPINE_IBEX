# Phase 17 — UI/UX Information Architecture: FLARE-X

> **Status:** ✅ COMPLETE  
> **Challenge:** Flame in Freefall (NASA Space Apps Challenge 2026)  
> **Core Mandate:** Translates the locked scientific and feature specifications into an intuitive, accessible, and aerospace-grade interface. Designed around the user's scientific question rather than internal AI infrastructure. Guarantees that a judge understands the tool in 10 seconds, runs a scenario in 30 seconds, and navigates authentic NASA evidence without friction.

---

## Executive Summary & Engineering Philosophy

Now FLARE-X stops being a very sophisticated backend diagram and becomes something a human can actually use without first earning a PhD in our architecture.

The UX goal is simple:
> **A judge should understand what FLARE-X does within about 10 seconds, run a meaningful analysis within about 30 seconds, and inspect the supporting NASA evidence without getting lost in research-software purgatory.**

---

## 17.1 Core UX Principle: Question First, Technology Second

FLARE-X is designed around the user's **scientific question**, not our backend modules.

```
BAD NAVIGATION (Internal Tech Jargon):
[Agents]  [Vector Store]  [Model Registry]  [Knowledge Graph]  [RAG Pipeline]
(Confuses aerospace engineers and judges alike)

FLARE-X CANONICAL NAVIGATION (Scientific Task Flow):
[Mission Control]  [Analyze Scenario]  [Explore Evidence]  [Compare]  [Validation & Sources]
(Directly answers the researcher's mission objective)
```

---

## 17.2 Final Primary Navigation Architecture

Five primary destinations define the global system shell:

| Navigation Item | Primary Function | Primary User Goal |
| :--- | :--- | :--- |
| **Mission Control** | Overview, active scenario cards, system health, entry point | Orient the user and launch prefilled demonstration scenarios |
| **Analyze** | Scenario input, interpretation, modeling, envelope, counterfactuals | Investigate a specific microgravity combustion atmosphere |
| **Explore** | Faceted repository browser across experiments, materials, documents | Query NASA flight data tables by parameter and investigation |
| **Compare** | Structured cross-comparison (Exp vs. Exp, Scenario vs. Exp) | Analyze physical differences, scaling gaps, and outcomes |
| **Evidence** | Provenance viewer, model validation cards, source manifests, DOIs | Inspect scientific credibility, training manifests, and error bounds |

---

## 17.3 Master Sitemap

```text
FLARE-X
│
├── Mission Control
│   ├── Quick Analyze Input
│   ├── NASA Evidence Snapshot (5 Families)
│   ├── Featured Pre-Filled Scenario (PMMA Flight Baseline)
│   └── System Capability Pipeline Status
│
├── Analyze (Flagship Screen)
│   ├── Scenario Input (Natural Language + Manual Sliders)
│   ├── Scenario Interpretation & Verification Panel
│   ├── Top Analysis Summary (Regime, Confidence, Domain)
│   ├── Experimental Support Map (2D Interactive Scatter)
│   ├── Domain Guard Status Card (INSIDE / BOUNDARY / OUTSIDE)
│   ├── Quantitative Model Result Card (Calibrated Probabilities)
│   ├── Ranked NASA Flight Evidence (Top-K Matches)
│   ├── "Why Should I Trust This?" Drawer
│   ├── Limitations & Contradictions Panel
│   └── Counterfactual Flammability Explorer
│
├── Explore
│   ├── Investigation Catalogs (BASS-II, FLEX, SPICE, SAFFIRE, SAME)
│   ├── Filterable Experiment Table (145+ Ingested Runs)
│   ├── Material & Fuel Taxonomies
│   ├── Physical Phenomenon Directories
│   └── NASA Technical Literature Archive
│
├── Compare
│   ├── Experiment ↔ Experiment (Opposing flight burns)
│   ├── Scenario ↔ Experiment (User query vs. flight ground truth)
│   └── Scenario ↔ Scenario (Dual atmospheric comparisons)
│
└── Evidence & Provenance
    ├── Claim-Level Lineage Explorer
    ├── Model Registry & Interactive Model Cards
    ├── Quantitative Validation Dashboard (Grouped CV Metrics)
    └── Official NASA PSI Accession & DOI Resolvers
```

---

## 17.4 Primary Screen Hierarchy: The Analyze Experience

The **Analyze** screen is the heart of FLARE-X. Its layout mirrors the physical scientific reasoning process:

$$\text{Scenario Definition} \longrightarrow \text{Core Result} \longrightarrow \text{Domain Validity} \longrightarrow \text{NASA Evidence} \longrightarrow \text{Limitations} \longrightarrow \text{Counterfactual Exploration}$$

---

## 17.5 Mission Control (Landing & Overview)

* **Hero Title:** `FLARE-X: NASA Microgravity Fire Intelligence`
* **Sub-Header:** *From NASA combustion experiments to evidence-backed fire-safety intelligence.*
* **Primary Calls-to-Action:**
  - `[Analyze Scenario]` (Direct entry into interactive lab)
  - `[Explore NASA Evidence]` (Direct entry into PSI catalog)
* **NASA Evidence Snapshot:** Displays real coverage metrics: 5 Investigations indexed (Solid, Droplet, Gas, Spacecraft, Smoke), 145+ discrete flight tests, 526 gas flames.
* **Featured Scenario Card:** One-click prefill: *"PMMA Acrylic in 18% Oxygen and 20 cm/s Opposed Flow"* $\to$ Launches instant analysis.
* **Prohibition:** Mission Control is **not** a KPI cemetery. Fluff like *"AI Power 98%"* or *"Knowledge Nodes 12,439"* is strictly banned.

---

## 17.7–17.10 Scenario Input & Interpretation UX

### Dual Input Mechanism:
1. **Natural Language Primary:** A prominent prompt input:
   > *“Describe the microgravity fire scenario you want to investigate...”*  
   > *(e.g., "Will a solid PMMA sample keep burning if cabin oxygen drops to 18% under 20 cm/s ventilation?")*
2. **Structured Controls:** Physical sliders and selectors adapting to combustion family.

### The Scenario Interpretation Step (Anti-Hallucination Gate):
Before executing heavy ML or database lookups, the system displays its parsed understanding:
```
┌─────────────────────────────────────────────────────────────┐
│ FLARE-X INTERPRETED YOUR SCENARIO AS:                       │
│ • Combustion Family:   SOLID FUEL (BASS-II / SAFFIRE)       │
│ • Material:            PMMA (Polymethyl methacrylate)       │
│ • Oxygen Level:        18.0% [Editable]                     │
│ • Forced Flow:         20.0 cm/s [Editable]                 │
│ • Target Phenomenon:   FLAME SPREAD & EXTINCTION            │
│                                                             │
│ [Modify Values]                            [Confirm & Run]  │
└─────────────────────────────────────────────────────────────┘
```
*Rule:* If the user enters *"low oxygen"*, the system does not silently invent $17.0\%$. It displays `Qualitative: Reduced | Exact Value: Unspecified` and prompts for precision.

---

## 17.11 Reasoning Trace UI (Loading State)

During analysis execution, the system renders transparent progress stages rather than an opaque spinning wheel:
```text
✓ Scenario interpreted and validated
✓ Routed to Solid Combustion Family (BASS-II / SAFFIRE)
✓ NASA PSI-25 database queried
✓ 14 matching flight experiments retrieved
✓ Hybrid scientific ranking complete (Top-3 isolated)
✓ Experimental Envelope Guard evaluated (Status: INSIDE)
✓ Evidence Auditor claim-verification passed
```

---

## 17.12–17.13 Top Result Summary & Epistemic Badging

The primary result appears above the fold in a high-contrast Mission Control card:
```
┌─────────────────────────────────────────────────────────────┐
│ RESULT: SUSTAINED PROPAGATION LEANING                       │
│ Status Badge: 🟢 IN-DOMAIN  |  Evidence Strength: MODERATE  │
├─────────────────────────────────────────────────────────────┤
│ Headline Summary:                                           │
│ The selected conditions match BASS-II solid flight burns.   │
│ Model estimates a 67% probability of sustained burning.     │
│ Opposed airflow is sufficient to overcome radiative cooling.│
├─────────────────────────────────────────────────────────────┤
│ [Why Should I Trust This?]                 [View Evidence]  │
└─────────────────────────────────────────────────────────────┘
```

### Visual Epistemic Badges:
* 🔵 `NASA OBSERVATION` (Direct empirical measurement from flight log)
* 🟣 `MODEL INFERENCE` (Quantitative prediction from trained ML pipeline)
* 🟡 `AI SYNTHESIS` (Multi-experiment reasoned interpretation)
* ⚪ `LIMITATION` (Geometric, scale, or aerodynamic caveat)

---

## 17.14–17.15 Interactive Experimental Support Map

Located in the center workspace:
* **Axes:** $Y = \text{Oxygen Concentration } (\%)$, $X = \text{Opposed Airflow Velocity } (\text{cm/s})$.
* **Elements:**
  - $\bullet$ Solid circular dots: Historical NASA spaceflight burns.
  - $\star$ Bright star: Active user scenario ("You Are Here").
  - Background zones: Dense green support, amber boundary zone, gray cross-hatched unsupported region.
* **Point Interactions:**
  - Hovering a NASA dot exposes test ID, material, $O_2$, flow, observed outcome, and a link to view raw PSI data.
  - Hovering the user star exposes domain status, nearest neighbor distance $D_k$, and local data density.

---

## 17.16 Domain Guard Status Card

Rendered adjacent to the Support Map:
* **`INSIDE`:**
  > 🟢 **INSIDE NASA-SUPPORTED DOMAIN**  
  > *Material (PMMA), oxygen (18%), and flow (20 cm/s) match dense flight clusters. Predictions displayed with full confidence.*
* **`NEAR_BOUNDARY`:**
  > 🟡 **NEAR EMPIRICAL BOUNDARY**  
  > *Oxygen concentration approaches the 16.5% microgravity extinction cliff. Predictions displayed with boundary caution.*
* **`OUTSIDE`:**
  > 🔴 **OUTSIDE NASA EXPERIMENTAL ENVELOPE**  
  > *Oxygen concentration (11.5%) is below minimum flight-tested limits (15.0%). Quantitative model suppressed. Nearest flight evidence shown below.*

---

## 17.18–17.20 Ranked Evidence Section & "Why This Experiment?" Drawer

Displays the top-3 physically comparable NASA flight burns:

```
┌─────────────────────────────────────────────────────────────┐
│ #1 BASS-II Test 31 (HIGH SCIENTIFIC RELEVANCE)              │
│ Outcome: Sustained Flame Propagation                        │
│ Conditions: PMMA flat slab | O2 = 18.0% | Flow = 20.0 cm/s  │
│ Relevance Factors: Exact material, matching O2, matching flow│
│ [Why this experiment?]                    [Inspect Source]  │
└─────────────────────────────────────────────────────────────┘
```

Clicking **"Why this experiment?"** slides open an inspector showing exact parameter deltas:
$$\Delta O_2 = 0.0\%, \quad \Delta u = 0.0\text{ cm/s}, \quad \text{Material Match: 100%}, \quad \text{Geometry Match: Different (Rod vs Slab)}$$

---

## 17.21 The "Why Should I Trust This?" Panel

A dedicated slide-over drawer providing total audit transparency:
* **Epistemic Type:** `MODEL_INFERENCE`
* **Underlying Algorithm:** `flame_spread_gb` (Gradient Boosted Decision Trees)
* **Model Validation:** $79.31\%$ honest grouped CV accuracy (vs. $51.72\%$ baseline)
* **Empirical Support:** 8 relevant BASS-II flight burns ($D_k = 0.082 < Q_{90}$)
* **Primary Citation:** NASA PSI-25 (`doi:10.2514/6.2014-3677`)
* **Known Limitations:** Flat sheet flight data applied to cylindrical geometry query.

---

## 17.22 Limitations Card (Zero Concealment)

FLARE-X forbids burying limitations in obscure tooltips. A dedicated card highlights:
* *Geometry Discrepancy:* Historical flight runs utilized flat acrylic slabs; query specifies cylindrical rods.
* *Scale Consideration:* Benchtop duct tests do not incorporate large spacecraft cabin recirculating eddy currents (referenced via SAFFIRE-I).

---

## 17.23–17.25 Counterfactual Explorer UX

Positioned directly beneath baseline findings:
* **Interactive Control:** Precision slider for oxygen concentration:
  $$15.0\% \quad \longleftarrow \quad [=== \bullet ===] \quad \longrightarrow \quad 24.0\%$$
* **Side-by-Side Live Comparison:**

| Parameter / Metric | Baseline Scenario | Counterfactual State | Delta |
| :--- | :---: | :---: | :---: |
| **Oxygen Concentration** | $21.0\%$ | $18.0\%$ | $-3.0\%$ |
| **Predicted Flammability** | `spread` ($P = 0.78$) | `marginal_spread` ($P = 0.44$) | $\Delta P = -0.34$ |
| **Domain Status** | 🟢 `INSIDE` | 🟡 `NEAR_BOUNDARY` | Approaching cliff |
| **Relevant NASA Tests** | 8 experiments | 5 experiments | 2 newly relevant |

* **Regime Tipping Indicator:** When slider crosses $17.5\% O_2$, a banner highlights:
  > *"Predicted regime transition detected: model transitions from steady spread to marginal flammability."*

---

## 17.26–17.27 Dedicated Compare Screen

Provides side-by-side multi-parameter evaluation across three modes:
1. **Experiment $\leftrightarrow$ Experiment:** Compare two historical NASA burns (e.g., BASS-II Test 12 vs. Test 31).
2. **Scenario $\leftrightarrow$ Experiment:** Compare user query against a published NASA flight run.
3. **Scenario $\leftrightarrow$ Scenario:** Compare two proposed atmospheric operating envelopes.

---

## 17.28–17.31 Explore Repository Screen

Faceted search across NASA combustion data:
* **Filters:** Investigation (`BASS-II`, `FLEX`, `SPICE`, `SAFFIRE`), Fuel Phase (`Solid`, `Liquid`, `Gas`), Oxygen range, Pressure range, Airflow range.
* **Default View:** Interactive sortable data table.
* **Experiment Detail View:** Contains flight telemetry plots, test metadata, raw CSV downloads, and a prominent **`[Use as Scenario]`** CTA that copies test conditions directly into the Analyze lab.

---

## 17.32–17.34 Evidence & Provenance Center

* **Model Cards View:** Technical specifications, hyperparameters, training manifests, and confusion matrices for SPICE-FL and BASS-RG.
* **Provenance Explorer:** Interactive node-link chain tracing a claim from UI text down to row/column/time coordinates in NASA source files.

---

## 17.37–17.41 Explicit Edge Case UX & Empty States

| System Condition | User Interface Treatment |
| :--- | :--- |
| **Zero Direct Matches** | Never renders *"No results"*. Renders nearest available flight runs with parameter deltas. |
| **Missing Model Features** | Renders *"Quantitative model skipped (Pressure missing)"*. Continues evidence retrieval gracefully. |
| **Outside-Domain Query** | Renders prominent red banner: *"Outside NASA Experimental Envelope. Prediction withheld."* Surfaces nearest burns. |
| **Conflicting Evidence** | Renders *"Mixed NASA Evidence"* badge. Displays both opposing flight outcomes side-by-side with geometry explanations. |

---

## 17.42–17.43 Desktop Workspace Layout (Three-Column Wireframe)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ [FLARE-X]   Mission Control    Analyze    Explore    Compare    Evidence   │
├────────────────────┬──────────────────────────────────┬─────────────────────┤
│ SCENARIO LAB       │ MAIN WORKSPACE                   │ EVIDENCE INSPECTOR  │
│                    │                                  │                     │
│ Material: [PMMA ▼] │ [RESULT: Sustained Leaning]      │ Domain: INSIDE      │
│ Oxygen:   [18.0 %] │ Badge: IN-DOMAIN                 │ Strength: MODERATE  │
│ Airflow:  [20 cm/s]│                                  │ Sources: PSI-25     │
│ Flow Dir: [Opposed]│ ┌──────────────────────────────┐ │                     │
│ Geometry: [Slab  ▼]│ │ EXPERIMENTAL SUPPORT MAP     │ │ Top Matching Tests: │
│                    │ │   ●    ●    ★ (You Are Here) │ │ 1. BASS-II Test 31  │
│ [Run Analysis]     │ │ ●    ●         ●             │ │ 2. BASS-II Test 42  │
│                    │ └──────────────────────────────┘ │ 3. SAFFIRE-I Burn 2 │
│ ────────────────── │                                  │                     │
│ REASONING TRACE    │ COUNTERFACTUAL EXPLORER          │ [Why should I       │
│ ✓ Family: Solid    │ Oxygen: [─────●─────] 21% -> 18% │  trust this?]       │
│ ✓ Ingested: BASS   │ Delta: -0.34 probability spread  │                     │
│ ✓ Guard: Passed    │ Regime: Spread -> Marginal       │ [View Model Card]   │
└────────────────────┴──────────────────────────────────┴─────────────────────┘
```

---

## 17.44–17.46 Mobile & Responsive Architecture

* **Layout Adaptation:** Gracefully collapses into a single-column progressive disclosure flow:
  $$\text{Scenario Controls} \longrightarrow \text{Primary Result} \longrightarrow \text{Domain Badge} \longrightarrow \text{Support Map} \longrightarrow \text{Evidence Cards} \longrightarrow \text{Counterfactual}$$
* **Sticky Bottom Controller:** During counterfactual exploration on mobile, a sticky bottom sheet houses the active oxygen slider and dynamic domain status badge.

---

## 17.47–17.48 Accessibility & Design Standards (WCAG 2.1 AA)

* **Status Indicators Never Rely on Color Alone:**
  - `✓ INSIDE` (Checkmark icon $+$ High-contrast green border)
  - `△ NEAR BOUNDARY` (Triangle warning icon $+$ Amber badge)
  - `! PARTIAL SUPPORT` (Exclamation icon $+$ Orange badge)
  - `× OUTSIDE` (Cross icon $+$ Red badge)
* **Keyboard Navigability:** Full tab-index traversal across sliders, buttons, and drawers.
* **Motion Preferences:** Supports `prefers-reduced-motion: reduce`.

---

## 17.51 Dual Information Density Modes

* **Standard Mode (Default for Judges & Executives):** Clean aerospace layout focusing on results, domain status, plain-language interpretations, and source buttons.
* **Technical Mode (Toggle for Combustion Researchers):** Surfaces exact $k$-NN neighbor distances ($D_k$), model registry commit hashes, Brier scores, and raw PSI sensor channels.

---

## 17.52–17.55 The 120-Second Winning Judge Journey

To eliminate live typing delays or unpredictable queries, the UI features a dedicated **`[Demo Scenario]`** launch button:

```
[00:00–00:10] MISSION CONTROL: Judge views NASA microgravity overview; clicks [Demo Scenario].
[00:10–00:30] ANALYZE LAB: PMMA solid scenario loads; BASS-II flight evidence and SAFFIRE context appear.
[00:30–00:45] SUPPORT MAP: Judge sees user scenario (★) plotted directly amongst NASA spaceflight burns (●).
[00:45–01:15] COUNTERFACTUAL: Judge drags oxygen slider (21% -> 18%); flammability drops; boundary approaches.
[01:15–01:35] ACTIVE REFUSAL: Slider dragged to 12%; system triggers OUTSIDE; prediction withheld; nearest burns show.
[01:35–02:00] PROVENANCE: Judge clicks [Why should I trust this?]; complete lineage traces to NASA PSI-25 DOI.
```

---

## 17.57 Canonical Component Library Taxonomy

1. `ScenarioInputForm`: Adaptive input controls for environmental parameters.
2. `StatusBadge`: Dual-encoded domain and evidence strength tags.
3. `ResultCard`: Primary regime prediction and calibrated probability readouts.
4. `SupportMap2D`: Interactive SVG scatter plot with NASA flight overlays.
5. `EvidenceCard`: Flight experiment summaries with relevance tags.
6. `CounterfactualSlider`: Debounced slider with live parameter freezing and deltas.
7. `WhyTrustDrawer`: Slide-over provenance and limitation inspector.
8. `ReasoningTrace`: Real-time pipeline execution stages.
9. `ComparisonTable`: Structured feature comparison across tests.
10. `ModelCardSummary`: Quantitative model metrics and training manifests.
11. `LimitationBanner`: High-visibility hardware and scale constraints.
12. `CitationPill`: Clickable DOI link with copy-to-clipboard functionality.

---

## 17.60 Scientific Microcopy Principles

* Use **"Prediction withheld"** — never *"Error"*.
* Use **"Limited experimental support"** — never *"Low confidence AI"*.
* Use **"Observed flight outcome"** — never generic *"Ground truth"*.
* Use **"Closest NASA experiments"** — never *"Recommended documents"*.

---

## 17.70 The Canonical Analyze Screen Wireframe

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ FLARE-X                   Mission Control   Analyze   Explore   Compare     │
├─────────────────────────────────────────────────────────────────────────────┤
│ SCENARIO: PMMA Solid Slab | O2 = 18.0% | Airflow = 20.0 cm/s | Opposed Flow │
│ [Modify Scenario]                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ RESULT: SUSTAINED FLAME PROPAGATION LEANING                                │
│ Domain: 🟢 INSIDE DOMAIN   |   Evidence Strength: MODERATE                  │
│ [Why should I trust this?]                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ EXPERIMENTAL SUPPORT MAP                                                    │
│  O2 (%)                                                                     │
│   35 ┌──────────────────────────────────────────┐                           │
│   21 │           ●      ★ (Current Scenario)    │                           │
│   17 │    ●    ●   (Boundary Zone)              │                           │
│   15 ├────●─────────────────────────────────────┤                           │
│    0 └──────────────────────────────────────────┘                           │
│      0         10         20         30         40 Airflow (cm/s)           │
├─────────────────────────────────────────────────────────────────────────────┤
│ TOP RANKED NASA FLIGHT EVIDENCE                                             │
│ #1 BASS-II Test 31 (PMMA, 18% O2, 20 cm/s) ──► Sustained Propagation        │
│ #2 BASS-II Test 42 (PMMA, 18% O2, 10 cm/s) ──► Slow Flame Spread           │
│ #3 SAFFIRE-I Burn 2 (PMMA, 21% O2, Spacecraft Scale) ──► Rapid Growth       │
├─────────────────────────────────────────────────────────────────────────────┤
│ COUNTERFACTUAL FLAMMABILITY EXPLORER                                        │
│ Oxygen Concentration: [───────●───────] 21.0% ──► 18.0%                     │
│ Flammability Delta:   0.78 ──► 0.44 (Δ = -0.34)                             │
│ Regime Shift:         Steady Spread ──► Boundary Extinction                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ LIMITATIONS & PROVENANCE                                                    │
│ • Flat sheet sample geometry differs from cylindrical wire queries.         │
│ • Traceable to NASA PSI Accession 25 (DOI: 10.2514/6.2014-3677).           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ✅ Phase 17 Acceptance Sign-off

- [x] Primary navigation and global sitemap finalized.
- [x] Analyze flagship screen hierarchy locked.
- [x] Dual scenario input (NLP + manual controls) specified.
- [x] Reasoning Trace loading UI locked.
- [x] Experimental Support Map layout and hover interactions formalized.
- [x] Domain Guard status and prediction refusal UX defined.
- [x] Counterfactual slider and sensitivity curve layouts specified.
- [x] "Why should I trust this?" audit drawer detailed.
- [x] Explore, Compare, and Evidence screen layouts finalized.
- [x] Edge cases, empty states, and outside-domain screens designed.
- [x] Desktop 3-column and mobile responsive breakpoints formalized.
- [x] WCAG 2.1 AA accessibility and microcopy standards enforced.
- [x] 120-second judge demonstration journey locked.

---

## ✅ Phase 17 Status: COMPLETE

The UI/UX Information Architecture is formally codified, verified, and locked.

We now advance to **Phase 18: Professional UI Mockups & Visual Design System** (defining the dark aerospace visual identity, design tokens, typography, CSS color palette, high-fidelity screen mockups, micro-animations, and visual presentation assets for the October 7 prescreening deliverables).
