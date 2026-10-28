# System Boundaries, Scientific Limitations & Ethics: FLARE-X

## Data integrity: verified defect in the BASS-II rows

The six NTRS identifiers used by this project are genuine and their titles were confirmed
against the live NASA Technical Reports Server. **The per-row values extracted from the
largest of those reports were not.**

NTRS serves machine-readable fulltext for every record:

```
https://ntrs.nasa.gov/api/citations/<id>/downloads/<filename>.pdf.txt
```

Re-reading `20210011385` (BASS-II Summary Report, which supplies 96 of 145 rows) through that
endpoint and comparing it against `src/ingestion/build_table.py` found:

Compared against the **authoritative PSI experimental table**
(`data/external/psi/PSI-25_Experimental_table_BASS-II.csv`, 129 rows, DOI
`10.60555/4qc4-de67`, CC0-1.0):

| Check | Result |
|---|---|
| Calibrated oxygen matches PSI (within 0.05 pts) | **0 of 81 tests** |
| **Oxygen differs by >0.35 pts** | **77 of 81** |
| Largest discrepancies | O4 PSI 14.8% vs coded 20.6%; O5 15.1% vs 19.8%; B14 15.0% vs 19.6%; O12 13.6% vs 18.1% |
| **Test IDs absent from the source** | **3** (`P7`, `P11`, `T8`) |

The PSI table spans **13.6 to 22.2 % calibrated initial O2**. The current table claims a
15.0 % floor, so the entire near-limit region the campaign was designed to probe is missing.

Specific confirmed errors:

- **`B14` outcome is inverted.** The report records 15.0% calibrated O2, spread rate `0.00`,
  *"only brief ignition, flame extinguished"*. The dataset records 19.6% O2 and `spread`.
- **Low-flow velocities are fan-potentiometer settings, not cm/s.** Values such as 0.35, 0.40
  and 0.50 cm/s correspond to pot readings quoted in observations
  (*"extinguished at pot 0.35"*). In the source tables, `Fan display` is a potentiometer
  reading and `Air display` is the duct velocity in cm/s; the two were conflated.
  These velocities **are recoverable**: `data/external/psi/PSI-25_Fan_calibration_data.xlsx`
  maps `Pot -> Fan Display -> Air Display -> Fan V -> U cm/s` separately for each date and
  flow-restrictor configuration. No single global conversion exists, which is why the same
  pot setting appears against different velocities in different tests.
- **Near-limit data was lost.** The real campaign probed 12.7-17% O2, the region where flames
  actually stop propagating. Those values were replaced with ~18-21% O2, so the learned
  flammability boundary sits several percentage points too high in oxygen.
- `build_table.py` calls `pdftotext` and discards the result (`txt` is assigned at line 55 and
  never read); the committed values are Python literals. With `data/raw/` gitignored and empty,
  the table cannot currently be regenerated.

### What this means for the reported accuracy

The metrics below are reproducible and the evaluation machinery is sound, but they measure the
model's fit to **this table**, not verified physical predictive skill. They should not be quoted
as evidence of real-world flammability prediction until the rows are re-transcribed.

The other 49 rows, from five further reports, have **not** been checked.

**Correction.** An earlier version of this section stated that five test IDs were absent
from the source and that the low-flow velocities were unrecoverable. Both were wrong, and
both were found by checking against PSI rather than the narrative report alone. Seven of
those IDs exist as sub-lettered variants (`O3a/b`, `O5a/b`, `O8a/b`, `O13a/b`, `O15a/b`,
`P3a/b`, `P13a/b`) that the earlier PDF-based scan did not match; only `P7`, `P11` and
`T8` are genuinely absent. The velocities are recoverable from the PSI fan calibration.

**Fix path.** A faithful rebuild joins PSI conditions (oxygen, `Air display` velocity,
material, geometry) to the `Test observations and anomalies` column of NTRS `20210011385`
on `Test #`. PSI carries no outcome column; the narrative report carries no clean
conditions. Both are needed. See `data/external/psi/README.md`.

---


> **Document Status:** Public, honest scientific disclosure of system scope, data concentration, physical model boundaries, and ethical safeguards for the FLARE-X prototype.  
> **Master Specification:** See complete project requirements in [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md).

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

For complete architectural details, Q&A defense playbooks, and adversarial test suites, refer to [`docs/PHASE_22_LIMITATIONS_AND_SCIENTIFIC_ETHICS.md`](docs/PHASE_22_LIMITATIONS_AND_SCIENTIFIC_ETHICS.md).
