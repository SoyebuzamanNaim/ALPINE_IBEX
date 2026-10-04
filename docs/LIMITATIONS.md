# System Boundaries, Scientific Limitations & Ethics: FLARE-X

> **Document Status:** Public, honest scientific disclosure of system scope, data concentration, physical model boundaries, and ethical safeguards for the FLARE-X prototype.  
> **Master Specification:** See complete canonical document at [`docs/PHASE_22_LIMITATIONS_AND_SCIENTIFIC_ETHICS.md`](file:///home/naiminator/Codebase/Project/FLARE_X/flare-x-prototype/docs/PHASE_22_LIMITATIONS_AND_SCIENTIFIC_ETHICS.md).

---

## 1. Official Product Classification & Canonical Disclaimer

FLARE-X is officially designated as:
> **A research and scientific decision-support prototype for exploring, comparing, modeling, and interpreting NASA microgravity-combustion evidence.**

### Canonical Limitation Statement
> **"FLARE-X is intended for research and scientific exploration. Its predictions and interpretations are derived from limited experimental datasets and statistical models and should not be used as certified engineering guidance, operational spacecraft safety instructions, or emergency-response recommendations."**

### Operational Boundaries
FLARE-X is explicitly **NOT**:
- A spacecraft fire certification system or flight-qualification standard.
- Operational mission-control software or emergency-response system.
- An autonomous fire suppression controller.
- A substitute for qualified aerospace combustion scientists or safety officers.

---

## 2. Core Ethical Axioms

1. **"FLARE-X treats uncertainty and abstention as primary scientific outputs, not product failures."**
2. **"The absence of experimental evidence is never presented as evidence of fire safety."**
3. **"NASA flight observations, statistical model inferences, and AI contextual syntheses are never represented as the same kind of evidence."**

---

## 3. Data Concentration & Fuel Sample Representation

- **Sample Size:** The dataset comprises discrete spaceflight observations extracted from published peer-reviewed NASA technical reports and Physical Sciences Informatics (PSI) flight records (BASS, BASS-II, FLEX, SPICE, SAFFIRE, SAME).
- **Material Imbalance in Solid Fuel Tests:**
  - **PMMA (Polymethyl Methacrylate / Cast Acrylic):** 92 tests (63.4% of BASS dataset). The PMMA envelope is exceptionally dense across 15.5% to 34% O₂ and 0 to 35 cm/s flow.
  - **Cellulose (Ashless Filter Paper):** 22 tests (15.2%).
  - **Cotton (Thin Woven Fabric):** 19 tests (13.1%).
  - **Nomex (Aramid Synthetic Fabric):** 7 tests (4.8%).
  - **Delrin (Polyoxymethylene):** 5 tests (3.4%).
- **Unsupported Materials:** The system **strictly refuses** predictions for materials not present in the published microgravity database (e.g., Teflon, Kapton, Silicone, Titanium, Lithium-ion battery casings). Spacecraft safety officers must not extrapolate these findings to unseen polymers. Exact-material support takes non-negotiable precedence over material-family similarity.

---

## 4. Experimental Atmospheric & Flow Boundaries

- **Oxygen Concentration:** Valid exclusively between **15.0% and 34.0% O₂** by volume. Hypoxic atmospheres below 15.0% or hyperoxic conditions above 34.0% trigger non-negotiable extrapolation refusal.
- **Ambient Pressure:** Valid exclusively between **56.5 kPa and 101.3 kPa** (0.56 to 1.0 atm). High-pressure regimes (e.g., hyperbaric chambers) are excluded.
- **Ventilation Velocity:** Valid between **0.0 cm/s (quiescent) and 45.0 cm/s**. High-velocity ventilation ducts exceeding 45.0 cm/s fall outside empirical flight data.
- **Flow Vector Dynamics:** Flow direction (opposed, concurrent, co-flow, quiescent) fundamentally alters physical flame spread. Scalar flow velocities must not be naively interchanged across differing flow geometries.

---

## 5. Modeling, Validation & Extrapolation Safeguards

- **Empirical Surrogates, Not CFD Simulators:** Inferences represent statistical pattern matching against historical NASA flight tests. They do **not** constitute computational fluid dynamics (CFD) or closed-form Navier-Stokes solutions.
- **Honest Grouped Validation:** All models report **Grouped Cross-Validation (`StratifiedGroupKFold`)** metrics grouped strictly on physical test specimen / run IDs. Video frame count is never equated with independent sample count.
- **Automated Abstention via Envelope Guard:** The **Experimental Envelope Guard** intercepts all queries. If environmental parameters lie outside the empirical flight convex hull or exhibit sparse local density, **quantitative predictions are withheld (`prediction: null`)**, and the 3 closest historical flight experiments are surfaced instead.
- **Non-Causal Counterfactuals:** Counterfactual sweeps evaluate mathematical model response surfaces; they do not simulate real-world physical interventions where coupled variables interact dynamically.
- **No False Certainty:** Class probabilities and prediction intervals ($\pm 95\%$) are presented alongside empirical domain coverage. Model confidence is never blended into a single artificial "AI confidence" metric.

---

## 6. Hardware, Scale & Gravitational Scope

- **Scale Disconnect (Sample vs. Compartment):** Small-scale rod/sheet tests (BASS-II) provide material flammability kinetics; compartment-scale burns (SAFFIRE) provide structural fire dynamics. Sample-level extinction limits must not be assumed to guarantee compartment-scale safety.
- **Gravity Scoping:** Flight data was collected under microgravity ($g \approx 10^{-4}g$). Extrapolation to lunar ($0.166g$), Martian ($0.38g$), or terrestrial ($1.0g$) environments is strictly barred without dedicated partial-gravity validated models.

---

## 7. Epistemic Claim Differentiation

All data, predictions, and text displayed across FLARE-X carry explicit epistemic badges:
- `[ 🟢 NASA OBSERVATION ]`: Direct, ground-truth measurement from flight telemetry.
- `[ 🟣 MODEL INFERENCE  ]`: Statistical prediction from a validated quantitative model.
- `[ ⚪ AI SYNTHESIS     ]`: Natural-language contextual summary audited by the Evidence Auditor.
- `[ 🔴 LIMITATION       ]`: Known scientific boundary, data gap, or caveat.

---

## 8. Master Red Lines (Permanently Prohibited Actions)

1. ❌ Claiming an empirical model output is a NASA flight observation.
2. ❌ Extrapolating quantitative predictions outside verified empirical flight envelopes.
3. ❌ Issuing certified spacecraft engineering flammability or flight safety standards.
4. ❌ Inferring fire safety from the absence of experimental data ("No evidence ≠ no risk").
5. ❌ Presenting statistical feature importance (SHAP) as physical causality.
6. ❌ Concealing empirical contradictions between NASA flight burns (`MIXED EVIDENCE` state enforced).
7. ❌ Hallucinating, rounding, or generating artificial telemetry numbers.
8. ❌ Operating as an active real-time fire emergency response tool.
9. ❌ Claiming NASA institutional endorsement or approval.

For complete architectural details, Q&A defense playbooks, and adversarial test suites, refer to [`docs/PHASE_22_LIMITATIONS_AND_SCIENTIFIC_ETHICS.md`](file:///home/naiminator/Codebase/Project/FLARE_X/flare-x-prototype/docs/PHASE_22_LIMITATIONS_AND_SCIENTIFIC_ETHICS.md).
