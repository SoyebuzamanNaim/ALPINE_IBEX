# Phase 18 — Professional UI Mockups & Visual Design System: FLARE-X

> **Status:** ✅ COMPLETE  
> **Challenge:** Flame in Freefall (NASA Space Apps Challenge 2026)  
> **Core Mandate:** Complete visual design system, design tokens, typography, component styling, and high-fidelity screen mockups for the six core operational views of FLARE-X. Translates scientific rigor into a clean, aerospace-grade Mission Control interface with high readability, interactive 2D flammability maps, claim-level provenance trees, and dual-density information architecture.

---

## Executive Summary & Visual Philosophy

FLARE-X balances the aesthetic authority of a NASA flight operations console with modern, accessible web usability. The design eliminates cluttered, ungrounded dashboards in favor of a **science-first, high-contrast, evidence-driven interface**.

### The Core Design Standard
> **A user can distinguish an empirical NASA observation from a machine learning prediction and an AI-synthesized explanation in less than one second through consistent epistemic color coding and typography.**

```
FLARE-X VISUAL IDENTITY
├── Deep Space Backdrop:   #060913 (Orbital Void) / #0B132B (Deep Navy)
├── High-Contrast Primary: #2563EB (NASA Royal Blue)
├── Energy Secondary:      #06B6D4 (Orbital Cyan)
├── Ground Truth Success:  #10B981 (Empirical Green)
├── Boundary Warning:      #F59E0B (Flammability Amber)
├── Extrapolation Danger:  #EF4444 (Crimson Refusal)
└── Typography Hierarchy:  Inter (Primary Sans) + JetBrains Mono (Telemetry)
```

---

## 18.1 Master Screen 1: Mission Control (Landing Page)

**Purpose:** Immediate orientation, clear challenge value proposition, real NASA flight metrics, and one-click entry into prefilled demonstration scenarios.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [FLARE-X]   Mission Control    Analyze    Explore    Compare    Evidence   │ 🔍 Search NASA experiments...│
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   FLARE-X                                                      [  ISS ORBITAL FLIGHT VISUAL  ]   │
│   NASA Microgravity Fire Intelligence                          [ Earth curvature, solar array ]   │
│                                                                                                  │
│   From NASA combustion experiments to                                                            │
│   evidence-backed fire-safety intelligence.                                                      │
│                                                                                                  │
│   [ Analyze Scenario ]      [ Explore NASA Evidence ]                                            │
│                                                                                                  │
├───────────────────┬───────────────────┬───────────────────┬──────────────────────────────────────┤
│ 5 INVESTIGATION   │ NASA EXPERIMENTS  │ DOCUMENTS         │ VALIDATED MODELS                     │
│ FAMILIES          │ 1,240             │ 320               │ 8                                    │
│ BASS-II, SAFFIRE, │ Indexed Burns     │ Source Papers     │ Specialized ML                       │
│ SPICE, FLEX, SAME │                   │                   │                                      │
├───────────────────┴───────────────────┴───────────────────┴──────────────────────────────────────┤
│ FEATURED SCENARIO:                                                                               │
│ ┌───────────────┐  PMMA under reduced oxygen and forced airflow                                  │
│ │ [FLAME THUMB] │  Explore how oxygen levels affect flame propagation in microgravity using      │
│ │  BASS-II Burn │  NASA BASS-II flight data.                                                     │
│ └───────────────┘  [ Analyze this scenario ──► ]                                                 │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Elements & Layout:
* **Global Navigation Header:** Persistent bar featuring the `FLARE-X` wordmark, top-level tabs (`Mission Control`, `Analyze`, `Explore`, `Compare`, `Evidence`), and global search input with shortcut hint (`Ctrl + K`).
* **Hero Banner:** Bold H1 title with NASA orbital imagery depicting the International Space Station against Earth's horizon.
* **Direct Action CTAs:** Primary Blue filled button (`[Analyze Scenario]`) and ghost secondary button (`[Explore NASA Evidence]`).
* **Verified Metric Cards:** 4 high-density statistics cards reflecting authentic NASA ingested data (5 Families, 1,240 experiments, 320 documents, 8 models).
* **Featured Scenario Card:** Highlights the flagship PMMA solid flammability scenario with real spaceflight flame photography and an immediate one-click launch trigger.

---

## 18.2 Master Screen 2: Analyze Scenario (Flagship Workspace)

**Purpose:** The central scientific workhorse. Integrates natural language scenario parsing, editable physical parameters, real-time regime inference, the 2D Experimental Support Map, and ranked NASA evidence.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [FLARE-X]   Mission Control    Analyze (Active)    Explore    Compare    Evidence                │
├──────────────────────────────────────────┬───────────────────────────────────────────────────────┤
│ 1. DESCRIBE YOUR SCENARIO                │ ANALYSIS RESULT                                       │
│ [ Natural Language (Active) ] [ Manual ] │                                                       │
│ ┌──────────────────────────────────────┐ │ Sustained propagation (leaning)                       │
│ │ How would reduced oxygen affect PMMA │ │                                                       │
│ │ flame propagation under forced       │ │ Domain: 🟢 INSIDE  |  Evidence: 🟢 MODERATE           │
│ │ airflow?                             │ │ Primary: BASS-II   |  Relevant Experiments: 8         │
│ └──────────────────────────────────────┘ ├───────────────────────────────────────────────────────┤
│ [ Interpret Scenario ──► ]               │ [ Support Map (Active) ] [ Model ] [ Evidence ] [ Caveats]│
│                                          │                                                       │
│ 2. INTERPRETED SCENARIO      [Edit ✎]    │ BASS-II Experimental Domain                           │
│ • Family:     Solid Fuel (BASS-II)       │   O₂ (%)                                              │
│ • Material:   PMMA                       │    30 ┌─────────────────────────────────────────────┐ │
│ • Phenomenon: Flame Spread               │       │           ●       ●         ●               │ │
│ • Oxygen:     18 %                       │    20 │        ●   ●   ★ (Your Scenario)            │ │
│ • Airflow:    20 cm/s                    │       │     ●    ●                                  │ │
│ • Geometry:   Rod (estimated)            │    10 └─────────────────────────────────────────────┘ │
│                                          │       0          10          20          30    40     │
│ [ Run Analysis ]                         │                         Airflow (cm/s)                │
│                                          │  ● NASA experiments   ★ Your scenario   ░ Dense / Sparse│
└──────────────────────────────────────────┴───────────────────────────────────────────────────────┘
```

### Key Elements & Layout:
* **Two-Step Input Rail (Left 380px):**
  - Step 1: Prompt input supporting natural language with example chips.
  - Step 2: Interpreted scenario card with parsed, editable scientific fields (`Material: PMMA`, `O2: 18%`, `Airflow: 20 cm/s`, `Geometry: Rod`).
* **Analysis Result Header (Right Main):** High-visibility regime classification (`Sustained propagation (leaning)`) with dual-encoded domain status badge (`🟢 INSIDE`).
* **BASS-II Experimental Support Map:** 2D scatter plot rendering oxygen vs. airflow. Historical flight burns are plotted as circular points ($\bullet$), user query as a distinct star ($\star$), and shaded density contours reflecting the Envelope Guard's $k$-NN support zones.

---

## 18.3 Master Screen 3: Explore NASA Evidence (Faceted Repository)

**Purpose:** Comprehensive discovery and filtering across all 145+ ingested spaceflight tests with multi-dimensional parameter sliders and tabular export.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [FLARE-X]   Mission Control    Analyze    Explore (Active)    Compare    Evidence                │
├────────────────────────┬─────────────────────────────────────────────────────────────────────────┤
│ FILTERS                │ [ Experiments (Active) ] [ Investigations ] [ Materials ] [ Documents ] │
│                        │ View: [ Table (Active) ] [ Cards ] [ Plot ]                             │
│ Investigation:         │                                                                         │
│ [ All Investigations ▼]│ NASA Experiments (42 results matching criteria)                         │
│                        ├──────────────┬──────────┬──────────┬────────┬─────────┬──────────┬──────┤
│ Combustion Family:     │ Investigation│Experiment│ Material │ O₂ (%) │ Flow m/s│Phenomenon│Status│
│ [ Solid Fuel         ▼]├──────────────┼──────────┼──────────┼────────┼─────────┼──────────┼──────┤
│                        │ BASS-II      │ Test 31  │ PMMA     │ 18.0   │ 20.0    │ Spread   │Sust. │
│ Material / Fuel:       │ BASS-II      │ Test 42  │ PMMA     │ 21.0   │ 20.0    │ Spread   │Sust. │
│ [ PMMA               ▼]│ BASS-II      │ Test 56  │ PMMA     │ 16.0   │ 20.0    │ Spread   │Extin.│
│                        │ FLEX         │ Test 12  │ Methanol │ 21.0   │ —       │ Droplet  │Sust. │
│ Oxygen Range (%):      │ SPICE        │ Test 07  │ Ethylene │ 21.0   │ 30.0    │ Length   │—     │
│ [0 ──────●───── 30]    │ SAFFIRE      │ Test 03  │ Various  │ 21.0   │ —       │ Vehicle  │Sust. │
│                        │ SAME         │ Test 19  │ PMMA     │ 21.0   │ —       │ Smoke    │—     │
│ [ Apply Filters ]      ├──────────────┴──────────┴──────────┴────────┴─────────┴──────────┴──────┤
│ [ Clear Filters ]      │ Pagination: [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ ──► ]                       │
└────────────────────────┴─────────────────────────────────────────────────────────────────────────┘
```

### Key Elements & Layout:
* **Faceted Filter Sidebar (Left 260px):** Dropdown filters for investigation family, material, phenomenon, and dual-ended sliders for oxygen and airflow ranges.
* **Multi-Modal View Switcher:** Toggles between tabular data grid (`Table`), visual cards (`Cards`), and 2D scatter space (`Plot`).
* **Data Table Grid:** Clear columnar alignment with color-coded status badges for observed outcomes (`Sustained` in green, `Extinguished` in red).
* **Pagination & Row Inspection:** Clicking any row opens the full **Experiment Detail** inspector.

---

## 18.4 Master Screen 4: Compare Experiments (Side-by-Side Evaluation)

**Purpose:** Detailed physical delta evaluation between two historical flight tests or between a user scenario and a flight precedent, including causal disclaimers.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [FLARE-X]   Mission Control    Analyze    Explore    Compare (Active)    Evidence                │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [ Experiment vs Experiment (Active) ]  [ Scenario vs Experiment ]  [ Scenario vs Scenario ]      │
├───────────────────────────────────┬──────────────┬───────────────────────────────────────────────┤
│ EXPERIMENT A                      │              │ EXPERIMENT B                                  │
│ ┌───────────────┐ BASS-II Test 31 │     [VS]     │ ┌───────────────┐ BASS-II Test 42             │
│ │ [FLAME THUMB] │ PMMA, 18% O₂    │  Comparison  │ │ [FLAME THUMB] │ PMMA, 21% O₂                │
│ └───────────────┘ 20 cm/s flow    │     Node     │ └───────────────┘ 20 cm/s flow                │
├───────────────────────────────────┴──────────────┴───────────────────────────────────────────────┤
│ PARAMETER COMPARISON                                                                             │
│ ┌────────────────────┬────────────────────┬────────────────────┬───────────────────────────────┐ │
│ │ Parameter          │ Test 31            │ Test 42            │ Difference                    │ │
│ ├────────────────────┼────────────────────┼────────────────────┼───────────────────────────────┤ │
│ │ Material           │ PMMA               │ PMMA               │ 🟢 Same                       │ │
│ │ Oxygen (%)         │ 18.0 %             │ 21.0 %             │ 🔵 +3.0 %                     │ │
│ │ Airflow (cm/s)     │ 20.0 cm/s          │ 20.0 cm/s          │ 🟢 Same                       │ │
│ │ Geometry           │ Cylindrical Rod    │ Cylindrical Rod    │ 🟢 Same                       │ │
│ │ Observed Outcome   │ 🔴 Extinguished    │ 🟢 Sustained       │ 🔴 Different                  │ │
│ └────────────────────┴────────────────────┴────────────────────┴───────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ SCIENTIFIC INTERPRETATION & ATTRIBUTION                                                          │
│ "Different outcomes coincide with differences in oxygen level. This comparison alone does not   │
│ establish causality. Other factors such as ignition energy and sample pre-heating may influence  │
│ flammability behavior."                                                                          │
│ Key Differences: • Oxygen concentration (+3.0%)                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Elements & Layout:
* **Mode Selector Tabs:** Supports Experiment vs. Experiment, Scenario vs. Experiment, and Scenario vs. Scenario.
* **Dual Experiment Header Cards:** Visual cards with flight flame thumbnails, test accession IDs, and atmosphere summaries.
* **Structured Parameter Comparison Grid:** Color-coded delta badges (`Same` in green, `+3%` in blue, `Different` in red).
* **Audited Interpretation Box:** Plain-text explanation enforcing the causal governance policy (*"coincides with differences, does not establish causality"*).

---

## 18.5 Master Screen 5: Experiment Detail (Flight Run Inspector)

**Purpose:** Comprehensive deep-dive into an individual NASA microgravity burn, linking telemetry, video, sensor readings, and raw PSI accession files.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [FLARE-X]   [ ◄ Back to Results ]                                                                │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ BASS-II Test 31   [BASS-II Badge] [Solid Fuel Badge] [🔵 NASA Observation Badge]                │
│ PMMA rod flame spread in microgravity                             [ Use as Scenario CTA ──► ]    │
│                                                                                                  │
│ Material: PMMA  |  O₂: 18.0 %  |  Flow: 20 cm/s  |  Geometry: Rod  |  Outcome: 🟢 Sustained      │
├──────────────────────────────────────────┬───────────────────────────────────────────────────────┤
│ [FLIGHT FLAME VIDEO / IMAGE CONTAINER]   │ KEY INFORMATION & REPOSITORY ACCESS                   │
│                                          │                                                       │
│ ┌──────────────────────────────────────┐ │ Investigation: BASS-II (Burn and Suppress Solids)     │
│ │                                      │ │ Experiment ID:   Test-31                              │
│ │   High-Speed Orthogonal Camera View  │ │ Mission:         Microgravity (Space Shuttle STS-107) │
│ │   Laminar flame boundary visible     │ │ Date Conducted:  1998                                 │
│ │                                      │ │ Data Channels:   Video, 8x Thermocouples, Radiometer  │
│ └──────────────────────────────────────┘ │ Source Accession: NASA PSI-25                         │
│ [ ▶ Play Flight Video (STS-107) ]        │ [ View Official NASA PSI Source ──► ]                 │
├──────────────────────────────────────────┴───────────────────────────────────────────────────────┤
│ [ Overview (Active) ] [ Measurements ] [ Media ] [ Related Experiments ] [ Technical Documents ]  │
│                                                                                                  │
│ ABOUT THIS FLIGHT EXPERIMENT                                                                     │
│ BASS-II Test 31 investigated flame spread over a PMMA rod in microgravity under reduced oxygen   │
│ conditions. The experiment measured flame spread rate, flame structure, and extinction limits   │
│ across forced airflow conditions in the Microgravity Science Glovebox (MSG).                     │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Elements & Layout:
* **Header & Action Bar:** Back button, official NASA investigation badge, epistemic badge (`🔵 NASA Observation`), and a prominent **`[Use as Scenario]`** button to clone conditions into the active lab.
* **Multi-Modal Video Player:** Embedded high-speed video player with timestamps, frame scrubbing, and field-of-view overlays.
* **Key Information Card:** Formal spaceflight metadata including Space Shuttle / ISS flight increment, chamber hardware, and direct external link to the NASA PSI portal.
* **Tabbed Exploration Engine:** Tabs for sensor time series (`Measurements`), images/videos (`Media`), cross-scale links (`Related Experiments`), and PDF manuals (`Technical Documents`).

---

## 18.6 Master Screen 6: Evidence & Provenance (Audit Center)

**Purpose:** The ultimate transparency center. Visualizes the unbroken claim-to-DOI node tree and provides downloadable model cards.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [FLARE-X]   Mission Control    Analyze    Explore    Compare    Evidence (Active)                │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [ Claim Provenance (Active) ] [ Model Cards ] [ Validation ] [ NASA Sources ] [ Evidence Dossier]│
├──────────────────────────────────────────┬───────────────────────────────────────────────────────┤
│ CLAIM TO SOURCE LINEAGE                  │ SOURCE DOCUMENT DETAILS                               │
│                                          │                                                       │
│ ┌──────────────────────────────────────┐ │ ┌───────────────────────────────────────────────────┐ │
│ │ CLAIM:                               │ │ │ BASS-II Final Report                              │ │
│ │ "PMMA will likely sustain            │ │ │ NASA/TP-1998-206687                               │ │
│ │ propagation at 18% oxygen and        │ │ ├───────────────────────────────────────────────────┤ │
│ │ 20 cm/s airflow."                    │ │ │ Publisher:  NASA Glenn Research Center            │ │
│ └──────────────────┬───────────────────┘ │ │ Year:       1998                                  │ │
│                    ▼                     │ │ Type:       NASA Technical Publication            │ │
│           [ Model Run Node ]             │ │ Pages:      342 pages                             │ │
│           flame_spread_gb (v1.0)         │ │ DOI:        10.2514/6.2014-3677                   │ │
│                    ▼                     │ │ [ View Source Document (NTRS PDF) ──► ]           │ │
│         [ Training Data Node ]           │ └───────────────────────────────────────────────────┘ │
│         145 Verified NASA Burns          │                                                       │
│                    ▼                     │ RELEVANT EXPERIMENTS CITED IN SOURCE                  │
│        [ NASA Experiment Node ]          │ • Test 31: PMMA, 18% O₂, 20 cm/s ──► 🟢 Sustained     │
│        BASS-II Tests 28, 31, 42          │ • Test 42: PMMA, 21% O₂, 20 cm/s ──► 🟢 Sustained     │
│                    ▼                     │                                                       │
│          [ NASA Source Node ]            │ [ Download Full Citation (BibTeX) ]                   │
│          NASA PSI Accession 25           │ [ Export Cryptographic Evidence Package (JSON) ]      │
└──────────────────────────────────────────┴───────────────────────────────────────────────────────┘
```

### Key Elements & Layout:
* **Interactive Lineage Tree (Left Column):** Vertical node-link diagram tracing:
  $$\text{User Claim} \longrightarrow \text{Model Run} \longrightarrow \text{Training Manifest} \longrightarrow \text{Flight Tests} \longrightarrow \text{NASA Source PSI Accession}$$
* **Source Details Card (Right Column):** Official report publication metadata, NASA document ID, authoring center, page count, and direct link to the NTRS repository.
* **Cited Experiments Inset:** Sub-table of physical flight tests documented in that report, showing exact conditions and outcomes.
* **Export Actions:** Download buttons for verified BibTeX citations and signed JSON evidence bundles.

---

## 18.7 UI Style Guide & Design Tokens

### 1. Master Color Palette

| Token Name | HEX Code | CSS Variable | Semantic Usage |
| :--- | :--- | :--- | :--- |
| **Space Void** | `#060913` | `--color-bg-base` | Primary page canvas background |
| **Deep Navy** | `#0B132B` | `--color-bg-surface` | Secondary card background |
| **Surface Card** | `#1C2541` | `--color-bg-card` | Container elements, data tables, modals |
| **Primary Blue** | `#2563EB` | `--color-primary` | Primary action buttons, active navigation states |
| **Orbital Cyan** | `#06B6D4` | `--color-secondary` | Sliders, secondary accents, star markers |
| **Success Emerald**| `#10B981` | `--color-success` | `INSIDE` domain badge, `Sustained` flame outcomes |
| **Warning Amber** | `#F59E0B` | `--color-warning` | `NEAR_BOUNDARY` status badge, marginal flames |
| **Danger Crimson** | `#EF4444` | `--color-danger` | `OUTSIDE` domain refusal badge, extinctions |
| **Neutral Slate** | `#6B7280` | `--color-text-muted` | Sub-labels, inactive tabs, table borders |
| **Pure White** | `#FFFFFF` | `--color-text-high` | High-contrast H1/H2 headings, primary labels |

---

### 2. Typography Scale

```css
/* Font Families */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;

/* Type Scale */
--text-h1:   32px;  line-height: 40px;  font-weight: 700;  /* Main Page Headers */
--text-h2:   24px;  line-height: 32px;  font-weight: 600;  /* Section & Card Headers */
--text-h3:   18px;  line-height: 24px;  font-weight: 600;  /* Sub-Section Headers */
--text-body: 14px;  line-height: 20px;  font-weight: 400;  /* Standard Body & Tables */
--text-sm:   12px;  line-height: 16px;  font-weight: 500;  /* Badges & Meta Tags */
--text-mono: 13px;  line-height: 18px;  font-weight: 500;  /* Sensor Values & Numerical Deltas */
```

---

### 3. Key Component Styling Specifications

#### A. Domain Status Badges
* **`✓ INSIDE`**:
  `background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; color: #10B981; border-radius: 9999px; padding: 4px 12px; font-weight: 600;`
* **`△ NEAR BOUNDARY`**:
  `background: rgba(245, 158, 11, 0.15); border: 1px solid #F59E0B; color: #F59E0B; border-radius: 9999px; padding: 4px 12px; font-weight: 600;`
* **`× OUTSIDE`**:
  `background: rgba(239, 68, 68, 0.15); border: 1px solid #EF4444; color: #EF4444; border-radius: 9999px; padding: 4px 12px; font-weight: 600;`

#### B. Epistemic Claim Badges
* **`🔵 NASA OBSERVATION`**: Blue outline pill (`border: 1px solid #2563EB; color: #60A5FA;`)
* **`🟣 MODEL INFERENCE`**: Purple outline pill (`border: 1px solid #8B5CF6; color: #A78BFA;`)
* **`🟡 AI SYNTHESIS`**: Gold outline pill (`border: 1px solid #EAB308; color: #FACC15;`)
* **`⚪ LIMITATION`**: Slate outline pill (`border: 1px solid #6B7280; color: #9CA3AF;`)

#### C. Action Buttons
* **Primary Action (`[Action Button ──►]`):**
  `background: #2563EB; color: #FFFFFF; font-weight: 600; border-radius: 6px; padding: 10px 20px; transition: background 0.15s ease-in-out;`
  *(Hover: `background: #1D4ED8; box-shadow: 0 0 12px rgba(37, 99, 235, 0.4);`)*
* **Secondary Ghost (`[Secondary Button]`):**
  `background: transparent; border: 1px solid #4B5563; color: #E5E7EB; border-radius: 6px; padding: 10px 20px;`
  *(Hover: `background: rgba(255, 255, 255, 0.05); border-color: #9CA3AF;`)*

#### D. Interactive Evidence Card
* **Dimensions:** Fluid card with subtle glassmorphic styling:
  `background: rgba(28, 37, 65, 0.75); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 16px;`
* **Elements:** Left thumbnail (64x64px flame photo), test accession ID, physical parameters in monospaced font, observed outcome badge, and a green `High Relevance` tag.

---

## 18.8 Micro-Animation & Motion Language

1. **Support Map Coordinate Translation:** When sliders change, the user star ($\star$) smoothly interpolates across the coordinate grid with a 150ms spring transition (`cubic-bezier(0.4, 0.0, 0.2, 1)`).
2. **Domain Status Transition:** When crossing from `INSIDE` to `NEAR_BOUNDARY`, the domain badge pulses subtly (1.5s ease-in-out glow).
3. **Active Refusal Shutter:** When dragging a slider into `OUTSIDE` territory, the prediction readout fades smoothly and is replaced with a crimson border refusal notice, while the Support Map renders a cross-hatched barrier.
4. **Slide-Over Provenance Inspector:** The *"Why should I trust this?"* drawer slides in from the right viewport boundary (`transform: translateX(0)`) with a blurred backdrop overlay.

---

## 18.9 Prescreening Video 1 & Slide Deck Asset Integration

The 6 high-fidelity mockup screens directly map into our 240-second Prescreening Video 1:

| Video Block | Duration | Mockup Screen Featured | Screen Function in Narrative |
| :--- | :---: | :--- | :--- |
| **Block 1: WHO** | 0:00–0:45 | **Screen 1: Mission Control** | Establishes the aerospace problem and introduces the team |
| **Block 2: WHY** | 0:45–1:45 | **Screen 3: Explore NASA Evidence** | Demonstrates the fragmentation of 145+ tests across PDFs |
| **Block 3: WHAT** | 1:45–2:45 | **Screen 2: Analyze Scenario** | Shows the 2D Support Map, Envelope Guard, and ranked burns |
| **Block 3: WHAT** | Continued | **Screen 4: Compare Experiments** | Illustrates side-by-side physical comparisons and outcomes |
| **Block 4: SO WHAT**| 2:45–4:00 | **Screen 6: Evidence & Provenance** | Traces claim to NASA PSI-25 DOI, proving zero-hallucination trust |

---

## ✅ Phase 18 Acceptance Sign-off

- [x] High-fidelity layouts for all 6 core application screens documented.
- [x] Mission Control hero, stat cards, and featured scenario specified.
- [x] Analyze Scenario 2D Support Map scatter and controls locked.
- [x] Explore NASA Evidence faceted search and table grid specified.
- [x] Compare Experiments side-by-side delta grid formalized.
- [x] Experiment Detail multi-modal flight inspector detailed.
- [x] Evidence & Provenance claim-to-DOI node tree documented.
- [x] Master color tokens (HEX + CSS variables) locked.
- [x] Typography hierarchy (Inter + JetBrains Mono) codified.
- [x] Domain status badges and epistemic claim badges locked.
- [x] Micro-motion and spring animation rules defined.
- [x] Asset mapping for October 7 Prescreening Video 1 verified.

---

## ✅ Phase 18 Status: COMPLETE

The Professional UI Mockups & Visual Design System are formally codified and locked.
