# Phase 13 — Counterfactual Intelligence: FLARE-X

> **Status:** ✅ COMPLETE  
> **Challenge:** Flame in Freefall (NASA Space Apps Challenge 2026)  
> **Core Mandate:** Dynamic, scientifically controlled comparison of combustion scenarios. When a user perturbs a variable (e.g., $O_2: 21\% \to 18\%$), FLARE-X reruns the complete scientific pipeline—re-retrieving NASA evidence, recalculating model inferences, and re-evaluating the Experimental Envelope Guard. Association and model response are clearly demonstrated without claiming unproven physical causation.

---

## Executive Summary & Guiding Principle

FLARE-X does not stop at answering *"What happens at these conditions?"* When a user changes an environmental parameter, FLARE-X dynamically illustrates how the model response, evidence coverage, nearest NASA experiments, experimental domain support, and scientific interpretation shift.

### The Causal Discipline Invariant
> **“Observing that a model prediction shifts when oxygen decreases from 21% to 18% is not causal proof that oxygen alone caused the physical outcome.”**

This distinction forms the scientific bedrock of Phase 13.

---

## 13.1 The Canonical Counterfactual Workflow

```
                    BASELINE SCENARIO
                     (O₂ = 21%, u = 20 cm/s, PMMA)
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
      [EVIDENCE RETRIEVAL]        [MODEL + ENVELOPE GUARD]
      NASA PSI-25 / BASS-II       P(spread) = 0.78 | INSIDE
              │                           │
              └─────────────┬─────────────┘
                            ▼
                     BASELINE RESULT
                            │
              [PERTURBATION: O₂ 21% ──► 18%]
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
    [RE-RETRIEVE EVIDENCE]        [MODEL + ENVELOPE GUARD]
    Newly relevant burns          P(spread) = 0.44 | NEAR_BOUNDARY
              │                           │
              └─────────────┬─────────────┘
                            ▼
                  COUNTERFACTUAL RESULT
                            │
                            ▼
         STRUCTURED SCIENTIFIC COMPARISON
         • Model Probability Delta: Δ = -0.34
         • Physical Regime: Sustained ──► Boundary / Extinction
         • Evidence Shift: 3 newly relevant low-O₂ burns
         • Domain Status: INSIDE ──► NEAR_BOUNDARY
```

---

## 13.2 Default Rule: Controlled Single-Variable Sensitivity

* **Primary Mode:** Perturb exactly **one variable** while holding all other physical variables strictly constant:
  - Baseline: $O_2 = 21.0\%$, $u = 20.0\text{ cm/s}$, $P = 101.3\text{ kPa}$, $\text{Material} = \text{PMMA}$
  - Counterfactual: $O_2 = 18.0\%$, $u = 20.0\text{ cm/s}$, $P = 101.3\text{ kPa}$, $\text{Material} = \text{PMMA}$
* **Rationale:** Single-variable control guarantees that output deltas are attributable to the isolated parameter shift within the model formulation.

---

## 13.3 Multi-Variable Scenario Comparisons

When a user modifies multiple sliders simultaneously (e.g., $O_2: 21\% \to 18\%$ and $u: 10 \to 30\text{ cm/s}$):
* System labels the analysis as a **Multi-Parameter Scenario Comparison**, not a controlled counterfactual.
* **Mandatory UI Disclaimer:**
  > *"Multiple parameters modified simultaneously. The observed prediction shift cannot be attributed to a single variable."*

---

## 13.4 Family-Specific Editable Variables

Sliders adapt dynamically to the active physical combustion family:

| Combustion Family | Editable Continuous Variables | Categorical Scenario Switches |
| :--- | :--- | :--- |
| **BASS-II (Solid)** | Oxygen concentration, Airflow velocity, Sample thickness | Material (`PMMA`, `Nomex`, `Delrin`), Flow direction |
| **SPICE (Gas)** | Coflow velocity, Fuel flow rate, Burner diameter | Fuel type (`Methane`, `Ethylene`, `Propane`) |
| **FLEX (Droplet)** | Oxygen concentration, Chamber pressure, Droplet diameter | Fuel, Diluent gas, Suppressant concentration |
| **SAFFIRE (Spacecraft)** | Airflow velocity, Oxygen concentration | Sample scale, Ignition configuration |

---

## 13.5 Three Classes of Counterfactual Analysis

1. **Class A: Evidence-Backed Observed Comparison (Gold Standard):**
   - NASA historical archives contain flight burns at both conditions (e.g., BASS-II burns at both $21\%$ and $18\% O_2$).
   - Direct empirical comparison of flight outcomes.
2. **Class B: Model-Supported Interpolation:**
   - No flight burn exists at the exact value (e.g., $18.3\% O_2$), but dense flight tests surround the point within the empirical envelope ($D_k \le Q_{90}$).
   - Model interpolates within verified domain bounds.
3. **Class C: Unsupported Hypothetical (Boundary Refusal):**
   - Slider moves into untested territory ($O_2 < 15.0\%$).
   - **System suppresses authoritative model comparison** and anchors on nearest NASA evidence: *"Counterfactual condition exceeds NASA-tested flammability boundaries."*

---

## 13.6 Counterfactual State Schema

```json
{
  "comparison_id": "cf_20261004_042",
  "baseline": {
    "scenario_id": "scen_base_01",
    "parameters": {
      "material": "PMMA",
      "oxygen_pct": 21.0,
      "flow_cm_s": 20.0,
      "pressure_kpa": 101.3
    },
    "model_run_id": "run_base_01",
    "prediction": "spread",
    "probability_spread": 0.78,
    "domain_status": "INSIDE",
    "evidence_count": 8
  },
  "counterfactual": {
    "scenario_id": "scen_pert_01",
    "parameters": {
      "material": "PMMA",
      "oxygen_pct": 18.0,
      "flow_cm_s": 20.0,
      "pressure_kpa": 101.3
    },
    "model_run_id": "run_pert_01",
    "prediction": "marginal_spread",
    "probability_spread": 0.44,
    "domain_status": "NEAR_BOUNDARY",
    "evidence_count": 5
  },
  "changed_variables": ["oxygen_pct"],
  "deltas": {
    "probability_spread": -0.34,
    "regime_shift": "spread -> marginal_spread",
    "domain_shift": "INSIDE -> NEAR_BOUNDARY"
  }
}
```

---

## 13.8 Parameter Freeze Record

To prevent confusion, the UI explicitly highlights fixed vs. modified variables:
```
┌─────────────────────────────────────────────────────────────┐
│ PERTURBED VARIABLE:                                         │
│ • Oxygen Concentration: 21.0% ──► 18.0%  (Δ = -3.0%)        │
├─────────────────────────────────────────────────────────────┤
│ HELD CONSTANT (CONTROLLED):                                 │
│ • Material: PMMA (Solid flat slab)                          │
│ • Airflow Velocity: 20.0 cm/s (Opposed forced flow)         │
│ • Total Pressure: 101.3 kPa (1.0 atm standard cabin)       │
└─────────────────────────────────────────────────────────────┘
```

---

## 13.9–13.11 Model Output & Uncertainty Comparison

* **Classification Delta Wording:**
  - Permitted: *"The model's predicted probability of sustained flame spread decreases by 0.34 (from 0.78 to 0.44)."*
  - Prohibited: *"Combustion drops by 34%."*
* **Continuous Regression Delta (SPICE):**
  - $\Delta L_{\text{flame}} = \hat{L}_{\text{CF}} - \hat{L}_{\text{Base}}$ (reported in physical mm).
* **Interval Overlap Check:**
  - If Baseline interval is $[30\text{ mm}, 38\text{ mm}]$ and Counterfactual interval is $[28\text{ mm}, 36\text{ mm}]$, the UI warns: *"Substantial interval overlap ([28, 36] vs. [30, 38] mm); prediction difference is within model uncertainty."*

---

## 13.12–13.14 Regime & Boundary Transition Detection

The Counterfactual Engine detects physical regime crossings:
1. **Regime Transition:** Model classification transitions across decision boundaries (`spread` $\to$ `marginal_spread` $\to$ `no_spread`).
2. **Envelope Crossing:** Scenario crosses from `INSIDE` $\to$ `NEAR_BOUNDARY` $\to$ `OUTSIDE`.
*Language Restraint:* The system reports *"The selected model changes predicted regime within this interval"*, never claiming *"The absolute universal flammability limit is 18.2%"*.

---

## 13.15 The Signature Counterfactual Slider Visual

```
       COUNTERFACTUAL FLAMMABILITY & DOMAIN SLIDER
  OXYGEN CONCENTRATION (%)
  15         17         18         20         21         24
  ├───●───────●──────────★──────────●──────────●──────────┤
  │ Flight   Flight    ACTIVE     Flight     Flight       │
  │ Burn     Burn      SLIDER     Burn       Burn         │
  └───────────────────────────────────────────────────────┘
  REGIME:     Extinguished ──► Boundary ──► Sustained
  SUPPORT:    [░░░ OUTSIDE ░░░][  NEAR BOUNDARY  ][████ INSIDE ████]
```

As the slider moves:
* User star ($\star$) translates across historical NASA burns ($\bullet$).
* Prediction dynamically updates from `spread` to `marginal_spread`.
* Experimental Support bar shifts from green (`INSIDE`) to amber (`NEAR_BOUNDARY`).

---

## 13.16–13.18 Dynamic Evidence Re-Retrieval & Evidence Delta

Counterfactual analysis **re-executes evidence retrieval** for every perturbed state:
* At $21\% O_2$, BASS-II Tests 20, 24, and 31 dominate.
* At $18\% O_2$, BASS-II Tests 42 and 51 become newly relevant.
* **Evidence Delta Card:**
  - **Newly Relevant:** BASS-II Test 42 ($18.0\% O_2$, slow spread)
  - **Less Relevant:** BASS-II Test 20 ($21.0\% O_2$, rapid spread)
  - **Evidence Strength Shift:** `STRONG` ($21\% O_2$) $\to$ `MODERATE` ($18\% O_2$)

---

## 13.20 Causal-Language Governance Policy

| Permitted Statements | Strictly Prohibited Statements |
| :--- | :--- |
| *"When oxygen decreases while flow and material are held constant, the model output shifts toward extinction."* | *"Lowering oxygen causes the flame to extinguish."* |
| *"Nearby NASA flight experiments under reduced oxygen observed marginal spread."* | *"Reducing oxygen guarantees flight safety."* |
| *"The retrieved evidence is consistent with a lower propagation rate."* | *"This proves that oxygen is the sole physical driver."* |

---

## 13.21–13.22 One-Factor Sensitivity Curves

The engine automatically sweeps a parameter across empirical bounds (e.g., $O_2 \in [15\%, 24\%]$ in $0.5\%$ increments):
* **Curve Styling Rule:**
  - Solid Line: `INSIDE` empirical envelope ($D_k \le Q_{90}$).
  - Dashed Line: `NEAR_BOUNDARY` ($Q_{90} < D_k \le Q_{97.5}$).
  - Curve Terminated / Faded: `OUTSIDE` ($D_k > Q_{97.5}$).

---

## 13.23 Two-Variable Response Surfaces

For models with bivariate flight coverage:
* **BASS-II:** Oxygen Concentration vs. Opposed Airflow Velocity $\to$ Flame Spread Probability Surface.
* **SPICE:** Coflow Velocity vs. Fuel Flow Rate $\to$ Flame Length Surface.
* Historical NASA flight burns are plotted as points directly on the contour surface.

---

## 13.26 Categorical Counterfactuals (Scenario Comparisons)

Switching material (e.g., PMMA $\to$ Nomex) is not a continuous perturbation:
* System executes a discrete **Scenario Comparison**.
* Both scenarios run through the Envelope Guard independently.
* If Nomex lacks training support, the quantitative model is blocked and the system compares direct NASA flight records.

---

## 13.28 Evidence Auditor Counterfactual Gate

The Auditor rejects counterfactual drafts if:
- [x] More than one variable changed without a multi-parameter disclosure.
- [x] Extrapolation occurs in either scenario without boundary warnings.
- [x] Causal claims (*"oxygen causes"*) appear without direct experimental proof.
- [x] Delta calculations do not match underlying model runs.

---

## 13.30 Live Prescreening Demo Sequence (PMMA Slider 21% $\to$ 17%)

1. **Baseline View:** Display PMMA at $21\% O_2$, $20\text{ cm/s}$ flow. Show 8 BASS-II experiments, model predicting steady spread ($P = 0.78$), `INSIDE` domain badge.
2. **Interactive Slider Movement:** Pull slider down to $18\% O_2$.
3. **Live System Update:**
   - Model probability drops to $0.44$ (`marginal_spread`).
   - Domain badge transitions to `NEAR_BOUNDARY`.
   - Nearest flight tests shift to BASS-II Tests 42 and 51.
4. **Transition Drilldown:** Click *"Why did the prediction change?"*
   - Explains that flow cooling balances chemical heat release near the 17% microgravity extinction limit.

---

## 13.31 Phase 13 Locked Decisions Matrix

| Decision | Status | Rationale |
| :--- | :---: | :--- |
| **Single-Variable Control as Default** | ✅ Locked | Maximizes interpretability and attribution |
| **Multi-Variable Comparisons Labeled** | ✅ Locked | Mandatory warning prevents false single-factor claims |
| **Dynamic Evidence Re-Retrieval** | ✅ Locked | Counterfactual updates both model and NASA evidence |
| **Full Pipeline Re-Execution** | ✅ Locked | Evidence, Model, Guard, and Audit rerun on every shift |
| **Regime Transition Detection** | ✅ Locked | Identifies physical tipping points |
| **Causal Claims Prohibited** | ❌ Banned | Association $\neq$ physical causation |
| **Active Refusal on OOD Sliders** | ✅ Locked | Curve terminates when leaving experimental support |
| **Sensitivity Curves Styled by Support** | ✅ Locked | Solid inside, dashed near boundary, terminated outside |
| **Two-Variable Response Surfaces** | ✅ Locked | Bivariate flammability maps with flight overlays |

---

## ✅ Phase 13 Status: COMPLETE

Counterfactual Intelligence is formally codified and locked.
