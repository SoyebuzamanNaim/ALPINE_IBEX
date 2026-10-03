# System Boundaries & Limitations

> **Document Status:** Public, honest scientific disclosure of system scope, data concentration, and physical model boundaries for the FLARE-X prototype.

## 1. Data Concentration & Fuel Sample Representation
- **Sample Size:** The dataset comprises **145 discrete spaceflight observations** extracted from published peer-reviewed NASA technical reports and Physical Sciences Informatics (PSI) records.
- **Material Imbalance:**
  - **PMMA (Polymethyl Methacrylate / Cast Acrylic):** 92 tests (63.4% of dataset). The PMMA envelope is exceptionally dense across 15.5% to 34% O2 and 0 to 35 cm/s flow.
  - **Cellulose (Ashless Filter Paper):** 22 tests (15.2%).
  - **Cotton (Thin Woven Fabric):** 19 tests (13.1%).
  - **Nomex (Aramid Synthetic Fabric):** 7 tests (4.8%).
  - **Delrin (Polyoxymethylene):** 5 tests (3.4%).
- **Unsupported Materials:** The system **strictly refuses** predictions for materials not present in the published microgravity database (e.g. Teflon, Kapton, Silicone, Titanium, Lithium-ion battery casings). Spacecraft safety officers must not extrapolate these findings to unseen polymers.

---

## 2. Experimental Atmospheric & Flow Boundaries
- **Oxygen Concentration:** Valid exclusively between **15.0% and 34.0% O₂** by volume. Hypoxic atmospheres below 15.0% or hyperoxic conditions above 34.0% trigger non-negotiable extrapolation refusal.
- **Ambient Pressure:** Valid exclusively between **56.5 kPa and 101.3 kPa** (0.56 to 1.0 atm). High-pressure regimes (e.g. hyperbaric chambers) are excluded.
- **Ventilation Velocity:** Valid between **0.0 cm/s (quiescent) and 45.0 cm/s**. High-velocity ventilation ducts exceeding 45.0 cm/s fall outside the empirical flight data.

---

## 3. Modeling & Classification Limitations
- **Cross-Validation Accuracy:** The headline honest grouped CV accuracy is **79.31%**. While random un-grouped splits achieve **80.69%**, reporting the grouped accuracy prevents false overconfidence caused by intra-report correlation.
- **Marginal Spread Class Uncertainty:** Per-class recall for `marginal_spread` is **52.38%** (compared to 89.33% for `spread` and 75.51% for `no_spread`). This reflects the physical chaotic instability of near-extinction flames in low flow, where micro-perturbations dictate whether a flame stabilizes or self-extinguishes.
- **Observational Machine Learning:** Inferences represent statistical pattern matching against historical NASA tests. They do **not** constitute formal computational fluid dynamics (CFD) or closed-form Navier-Stokes solutions.

---

## 4. Hardware & Geometry Scope
- **Ignition Energy:** Experiments in the dataset were conducted using standard electrical igniter wires (Kanthal/Nichrome) per NASA flight protocols. Scenarios with non-standard ignition sources or extreme external heat fluxes are not modeled.
- **Droplet & Gaseous Combustion:** Droplet combustion (FLEX/FLEX-2) and gaseous diffusion flames (ACME) are cataloged in `data/metadata/dataset_catalog.csv` but excluded from the solid-fuel flame spread engine to maintain physical validity.

---

## 5. Non-Causal Exploration Disclaimer
The FLARE-X prototype is designed as an interactive decision-support and exploration system for spaceflight fire safety researchers. All predictions and counterfactual sweeps are empirical surrogates derived from 145 microgravity spaceflight tests. Final operational flight rules must always be validated against official NASA STD-6001 guidelines and designated NASA flight safety review boards.
