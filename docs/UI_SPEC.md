# Frontend UI Specification (Phase 11)

> **Document Status:** Authoritative design and visual interaction specification for the FLARE-X web interface.

## 1. Design Aesthetics & Visual Hierarchy

In compliance with the project guidelines, FLARE-X delivers a science-first, NASA mission control aesthetic:
- **Atmosphere:** Aerospace dark mode (`#060913`, `#0c1222`) with glowing neon accents (`#00e5ff` cyan, `#ff3366` spread crimson, `#ffb300` marginal amber, `#00b4d8` extinction blue).
- **Typography:**
  - Headers & Badges: *Orbitron* (aerospace, futuristic, high legibility).
  - Body & Briefings: *Inter* (clean, accessible reading).
  - Telemetry & Numbers: *JetBrains Mono* (monospaced data alignment).
- **Glassmorphism:** Layered translucent cards (`rgba(12, 18, 34, 0.75)` with `backdrop-filter: blur(16px)` and subtle cyan borders).

---

## 2. Core Operational Views

### View 1: Mission Control & Scenario Lab
1. **Operational Controls Panel (Left):**
   - **NLP Scenario Parser:** Natural language text box converting conversational statements ("21% O2 at sea level for PMMA") into calibrated parameters.
   - **Material Selector:** Dropdown for supported microgravity fuels (`PMMA`, `Cellulose`, `Cotton`, `Nomex`, `Delrin`), indicating real sample counts.
   - **Atmospheric Sliders:**
     - Oxygen Concentration (% O2, 15.0% to 34.0%).
     - Ambient Pressure (kPa, 56.5 to 101.3 kPa).
     - Ventilation Flow Velocity (cm/s, 0.0 to 45.0 cm/s).
   - **Extrapolation Override Switch:** Explicit toggle enabling out-of-range testing (up to 50% O2) to test refusal triggers.
   - **Quick Presets:** One-click setups for *ISS Standard*, *Exploration Atmosphere*, and *Near Extinction*.
2. **Fire Intelligence & 2-D Boundary Map (Center):**
   - **Regime Prediction Hero:** Dynamic badge displaying `SUSTAINED SPREAD`, `MARGINAL SPREAD`, `EXTINCTION / NO SPREAD`, or `REFUSED (OUT OF ENVELOPE)`.
   - **Probability Distribution Bar:** Segmented bar displaying exact class percentages with model card stats (`Gradient Boosting`, `n=145`, `Grouped CV=79.31%`, `Baseline=51.72%`).
   - **Operator Safety Briefing:** Plain-language translation for flight operators assessing extinction boundaries and ventilation hazard corridors.
   - **Signature 2-D Flammability Map (Canvas):**
     - Slices parameter space holding Pressure & Material constant.
     - Shaded class regions (`spread` crimson, `marginal` amber, `no_spread` cyan).
     - Overlaid historical NASA flight test points (white-bordered scatter markers).
     - Pulsing reticle highlighting the operator's current query point.
3. **Nearest Citations & Grounded Explanation (Right):**
   - **Nearest Flight Tests List:** 3 closest empirical experiments with feature distances, observed outcomes, report numbers, and direct clickable links to NASA NTRS / PSI sources.
   - **Bounded Scientific Explanation:** Plain-text narrative audited to ensure zero numerical or citation hallucination.

### View 2: Killer Demo — Oxygen Sweep & Safety Margins (Brief §2)
- Simulates sliding cabin oxygen from 21% down to 16% O2 for PMMA under 5.0 cm/s opposed flow.
- Graph rendering sigmoidal probability curves for sustained spread vs extinction.
- Vertical transition boundary identified at 17.5% O2.
- Dual comparison cards showing real NASA BASS flight tests above the boundary (spread) and below the boundary (extinction).
- Extinction Safety Margin gauge measuring buffer from current ambient conditions.

### View 3: NASA Experiment Atlas
- Searchable and filterable data table of all 145 microgravity spaceflight observations.
- Filters for material and outcome.
- Direct links to NTRS report repositories.

### View 4: Model Card & Provenance
- Grouped 5-fold cross-validation metrics.
- Complete 3x3 confusion matrix and per-class recall scores.
- Catalog of 23 audited NASA investigations.
