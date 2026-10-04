# Phase 11 — Experimental Envelope Guard: FLARE-X

> **Status:** ✅ COMPLETE  
> **Challenge:** Flame in Freefall (NASA Space Apps Challenge 2026)  
> **Core Mandate:** Deterministic scientific validation of experimental support prior to model execution. Combines required feature completeness, categorical support modes, hard parameter boundaries, 5% edge proximity, and multi-dimensional weighted Gower $k$-NN density against empirical flight burns.

---

## Executive Summary & Engineering Mandate

This phase turns one of FLARE-X’s strongest ideas into an actual algorithm.

The Experimental Envelope Guard answers:
> **“Is this prediction supported by NASA experiments that are genuinely close to the user’s scenario, or is the model being asked to extrapolate into territory it has barely or never seen?”**

That distinction is crucial. A model can happily return a number for nonsense input. Computers are admirably free of embarrassment.

The Guard operates as **deterministic scientific code**, not an LLM agent.

---

## 11.1 Final Role of the Guard

The Guard sits as a strict firewall between the **Model Router**, **Quantitative Prediction**, and the **User**:

```
                       USER SCENARIO
                             │
                             ▼
                        MODEL ROUTER
                             │
                             ▼
                      COMPATIBLE MODEL
                             │
                             ▼
               EXPERIMENTAL ENVELOPE GUARD
                             │
              ├── 1. Feature Completeness
              ├── 2. Categorical Compatibility
              ├── 3. Hard Numerical Bounds
              ├── 4. Boundary Proximity (Edge 5%)
              └── 5. Local Experiment Density (k-NN)
                             │
                             ▼
                       DOMAIN STATUS
                             │
                             ▼
                     PREDICTION POLICY
```

---

## 11.2 Five Final Domain Statuses

FLARE-X locks five definitive domain statuses across the system:

| Status | Scientific Meaning | User & Execution Impact |
| :--- | :--- | :--- |
| **`INSIDE`** | Strong experimental support from nearby flight burns | Model prediction displayed normally with standard confidence |
| **`NEAR_BOUNDARY`** | Supported, but operating near the edge of tested parameter space | Prediction shown with an explicit, prominent boundary caution flag |
| **`PARTIAL_SUPPORT`** | Technically compatible, but evidence is sparse or matches only at family level | Quantitative prediction de-emphasized; highlights empirical evidence |
| **`OUTSIDE`** | Outside observed or model-supported experimental conditions | **Prediction blocked as authoritative output.** Nearest NASA evidence shown |
| **`UNKNOWN`** | Insufficient parameter information to determine empirical support | Prediction blocked; requests missing required physical constraints |

---

## 11.3 Family-Specific Envelopes (No Universal Envelope)

There is no universal NASA fire envelope. A droplet in stagnant air has completely different empirical limits than a solid slab in forced flow or a gaseous burner.

Each model family defines its own empirical domain dimensions:

```
                            FAMILY-SPECIFIC ENVELOPES
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
   [SPICE-FL GAS]              [FLEX-EX DROPLET]             [BASS-RG SOLID]
   • fuel                      • fuel                        • material / family
   • burner_diameter           • oxygen_fraction             • oxygen_fraction
   • coflow_velocity           • pressure                    • airflow_velocity
   • fuel_flow_rate            • droplet_diameter            • flow_direction
                               • suppressant / diluent       • sample geometry
```

---

## 11.4 The Five Guard Checks

For every prediction request, the Guard executes five checks in strict order:
1. **FEATURE COMPLETENESS:** Are all mandatory inputs specified?
2. **CATEGORICAL COMPATIBILITY:** Was this fuel/material ever tested in microgravity?
3. **HARD NUMERICAL BOUNDS:** Are numerical inputs within $[x_{\min}, x_{\max}]$?
4. **BOUNDARY PROXIMITY:** Are inputs within 5% of empirical extremities?
5. **LOCAL EXPERIMENTAL SUPPORT:** Are there actual multi-dimensional neighbors ($k$-NN)?

*The final status is determined by the most conservative failure encountered.*

---

## 11.5 Check 1 — Required Feature Completeness

Every model registry record defines its input schema:
* `required_features`: Parameters without which the mathematical model cannot execute.
* `optional_features`: Parameters that refine the calculation or context.

### Example: `SPICE_FL_V1`
* **Required:** `fuel`, `burner_diameter`, `coflow_velocity`, `fuel_flow_rate`.
* If `fuel_flow_rate` is missing:
  $$\text{Status} = \texttt{UNKNOWN}, \quad \text{Prediction} = \texttt{BLOCKED}, \quad \text{Reason} = \texttt{REQUIRED\_FEATURE\_MISSING}$$
* *Rule:* FLARE-X never quietly replaces a missing required parameter with a dataset mean.

---

## 11.6 Handling Optional Missing Variables

* If an optional variable is missing but the model can still compute:
  - Status may remain `INSIDE` or `NEAR_BOUNDARY`.
  - The missing optional variable is explicitly logged in `warnings`.
* If missingness materially weakens domain assessment:
  $$\text{Status} = \texttt{PARTIAL\_SUPPORT}$$

---

## 11.7 Check 2 — Categorical Compatibility

Covers fuels, materials, geometry, suppressants, and flow configuration. Each categorical input operates under one of three support modes:

| Mode | Rule | Example |
| :--- | :--- | :--- |
| **`EXACT_ONLY`** | Exact category string must exist in verified training data | `fuel = "Methane"` $\rightarrow$ Supported; `fuel = "Hydrogen"` $\rightarrow$ `OUTSIDE` |
| **`FAMILY_ALLOWED`** | Related canonical family may be substituted if model card allows | `material = "Acrylic variant"` $\rightarrow$ `material_family = "acrylic polymer"` |
| **`OPTIONAL`** | Category does not dictate physical eligibility | Operator ID, chamber lighting configuration |

---

## 11.8 Material-Family Fallback Rules

For solid fuels in BASS-II:
* Exact material match (`PMMA` $\equiv$ `PMMA`): Exact categorical support.
* Sibling material match (`Delrin` vs. `Cellulose`): Treated under distinct family kinetics.
* Material-family fallback: If a model was explicitly trained at the family level (`acrylic polymer`), an unknown PMMA derivative receives `PARTIAL_SUPPORT`, never silent `INSIDE`.
* *Rule:* We never invent chemical equivalence on the fly.

---

## 11.9 Check 3 — Hard Numerical Bounds

For every numerical feature $j$, store empirical extrema from flight experiments:
$$[\min_j, \max_j] \quad \text{from training data}$$

If for any critical feature:
$$x_j < \min_j \quad \text{or} \quad x_j > \max_j \implies \texttt{OUTSIDE}$$

### Ground Truth Limits Verified in Prototype (`cache/experiments.parquet`):
* **Oxygen Concentration:** $15.0\% \le O_2 \le 34.0\%$
* **Chamber Pressure:** $56.5\text{ kPa} \le P \le 101.3\text{ kPa}$
* **Ventilation Velocity:** $0.0\text{ cm/s} \le u \le 45.0\text{ cm/s}$

---

## 11.10 The Failure of 1D Min/Max Boxes (Multivariate Sparsity)

Suppose NASA flight data contains:
* $O_2 \in [15\%, 30\%]$
* $P \in [50\text{ kPa}, 150\text{ kPa}]$

The scenario:
$$O_2 = 29\%, \quad P = 148\text{ kPa}$$
is individually inside both 1D ranges. However, if NASA never tested high oxygen and high pressure simultaneously, the model is operating in an empty quadrant of parameter space. Simple bounding boxes fail to catch this.

---

## 11.11 Check 4 — Boundary Proximity Metric ($E_j$)

Even when inside hard bounds, the Guard checks proximity to empirical extremes:
$$E_j = \frac{\min(x_j - \min_j, \; \max_j - x_j)}{\max_j - \min_j}$$

* **Interpretation:**
  - $E_j \to 0$: Close to empirical boundary.
  - $E_j \to 0.5$: Centered in observed parameter envelope.
* **Initial 5% Threshold Law:**
  $$E_j \le 0.05 \implies \texttt{BOUNDARY\_WARNING}$$

---

## 11.12 Multi-Dimensional Boundary Evaluation

A boundary warning on a single feature does not automatically force rejection:
* Oxygen: Near minimum ($15.2\%$, $E_{O_2} = 0.01$) $\rightarrow$ Boundary flag.
* Airflow: Well-centered ($15.0\text{ cm/s}$) $\rightarrow$ Interior.
* Material: Exact PMMA match.
* **Result:** `NEAR_BOUNDARY` (cautious prediction permitted with warning, not `OUTSIDE`).

---

## 11.13 Check 5 — Local Experimental Support (Weighted Gower Metric)

To detect empty multi-dimensional space, FLARE-X measures distance to historical NASA flight tests using a **weighted Gower-style scientific distance metric**.

---

## 11.14 Numerical Distance Component ($d_j$)

For numerical feature $j$ between user input $x_j$ and reference experiment $y_j$:
$$d_j(x_j, y_j) = \frac{|x_j - y_j|}{\text{range}_j}$$
where $\text{range}_j = \max_j - \min_j$. Distance is bounded in $[0, 1]$.

---

## 11.15 Categorical Distance Component ($d_{\text{cat}}$)

For categorical features:
$$d_{\text{cat}}(x, y) = \begin{cases} 
0.0 & \text{Exact match (e.g., PMMA == PMMA)} \\ 
0.5 & \text{Same material family (e.g., Cast PMMA vs Extruded PMMA)} \\ 
1.0 & \text{Different family (e.g., PMMA vs Nomex)} 
\end{cases}$$

---

## 11.16 Weighted Scientific Distance Formulation

$$D(\mathbf{x}, \mathbf{y}) = \frac{\sum_{j=1}^M w_j d_j(x_j, y_j)}{\sum_{j=1}^M w_j}$$

### Standard Model Weights (BASS-II Solid Example):
* Material Match ($w_{\text{mat}}$): **3.0** (High chemical impact)
* Oxygen Proximity ($w_{O_2}$): **3.0** (Critical flammability driver)
* Airflow Velocity ($w_{\text{flow}}$): **2.5** (Convective cooling/transport)
* Geometry / Thickness ($w_{\text{geo}}$): **1.5** (Thermal mass)
* Flow Direction ($w_{\text{dir}}$): **1.5** (Opposed vs. concurrent)

*Weights are frozen during model registry creation and never hand-tuned per demo.*

---

## 11.17 $k$-Nearest Neighbor Support Metric ($D_k$)

For a user scenario $\mathbf{x}$, locate the $k = 5$ closest verified NASA flight experiments:
$$D_k(\mathbf{x}) = \frac{1}{k} \sum_{i=1}^k D(\mathbf{x}, \mathbf{y}_{(i)})$$
where $\mathbf{y}_{(1)}, \dots, \mathbf{y}_{(k)}$ are the $k$ nearest neighbors in the verified dataset.

---

## 11.18 Data-Adaptive Thresholds ($Q_{90}, Q_{97.5}$)

Rather than inventing arbitrary distance thresholds, thresholds are derived from the training set's own internal neighbor distances:
1. For every training experiment $\mathbf{x}_i$, compute its distance $D_k(\mathbf{x}_i)$ to its $k$ nearest peers in the training set.
2. Establish the empirical percentiles: $Q_{90}$ and $Q_{97.5}$.

| Local Distance ($D_k$) | Neighborhood Support Level | Domain Interpretation |
| :--- | :--- | :--- |
| **$D_k \le Q_{90}$** | Normal Experimental Density | Well-supported interior space |
| **$Q_{90} < D_k \le Q_{97.5}$** | Sparse Experimental Density | Boundary / marginal density |
| **$D_k > Q_{97.5}$** | Unusually Isolated Space | Unsupported combination $\rightarrow$ `PARTIAL` or `OUTSIDE` |

---

## 11.19 Protection Against Multi-Dimensional Extrapolation

* $O_2 = 21.0\%$ (Normal)
* $P = 101.3\text{ kPa}$ (Normal)
* $d_0 = 4.5\text{ mm}$ (Normal individually)
* But if NASA droplet tests only paired large droplets with reduced pressure, $D_k$ exceeds $Q_{97.5}$.
* **The Guard triggers:** Flags the multivariate gap immediately.

---

## 11.20 Final Decision Logic: UNKNOWN

Triggered when:
* A required feature is omitted.
* Model envelope metadata cannot be retrieved.
* **Execution:** $\texttt{BLOCK PREDICTION}$.

---

## 11.21 Final Decision Logic: OUTSIDE

Triggered when any critical condition fails:
* Unsupported categorical value under `EXACT_ONLY`.
* Critical numerical feature exceeds empirical $[\min_j, \max_j]$.
* Physical model family mismatch (e.g., solid scenario queried against gas model).
* Neighbor distance $D_k$ exceeds extreme extrapolation limits.
* **Execution:** $\texttt{BLOCK AS AUTHORITATIVE OUTPUT}$. System gracefully presents nearest NASA evidence.

---

## 11.22 Final Decision Logic: PARTIAL_SUPPORT

Triggered when:
* Hard bounds pass, but local experimental density is sparse ($D_k > Q_{90}$).
* Material matches only at the family level.
* Secondary optional variables are unrecorded.
* **Execution:** Model executes internally; UI marks output as low-support context.

---

## 11.23 Final Decision Logic: NEAR_BOUNDARY

Triggered when:
* All categorical and numerical bounds pass.
* At least one critical parameter lies within the 5% edge boundary ($E_j \le 0.05$) or near a known physical extinction cliff.
* **Execution:** Prediction rendered with a clear boundary warning badge.

---

## 11.24 Final Decision Logic: INSIDE

Triggered when:
* All required features present and valid.
* All categories verified.
* All numerical features well within bounds ($E_j > 0.05$).
* Local experimental density is strong ($D_k \le Q_{90}$).
* **Execution:** Prediction rendered with standard confidence.

---

## 11.25 Conservative Decision Precedence

When multiple conditions trigger simultaneously, the most conservative status dominates:

$$\texttt{UNKNOWN} \quad / \quad \texttt{OUTSIDE} \;\; \longrightarrow \;\; \texttt{PARTIAL\_SUPPORT} \;\; \longrightarrow \;\; \texttt{NEAR\_BOUNDARY} \;\; \longrightarrow \;\; \texttt{INSIDE}$$

---

## 11.26 Exact Prediction & Rendering Policy

| Status | Prediction Action | UI Visual Badge | Evidence Display |
| :--- | :--- | :--- | :--- |
| **`INSIDE`** | Render predicted value and confidence interval | 🟢 **IN-DOMAIN** | Standard nearest experiments |
| **`NEAR_BOUNDARY`** | Render prediction $+$ boundary warning banner | 🟡 **NEAR BOUNDARY** | Nearest experiments $+$ boundary delta |
| **`PARTIAL_SUPPORT`** | De-emphasize numerical prediction; display range | 🟠 **PARTIAL SUPPORT** | Prominent empirical test comparisons |
| **`OUTSIDE`** | **Suppress quantitative prediction** | 🔴 **OUT OF DOMAIN** | **Nearest NASA evidence only $+$ delta** |
| **`UNKNOWN`** | Block quantitative prediction | ⚪ **UNKNOWN** | Missing parameter prompt |

---

## 11.27 OUTSIDE Graceful Degradation (Nearest Evidence Fallback)

When a query is out-of-domain, FLARE-X never renders an empty error screen. It displays:
```
┌─────────────────────────────────────────────────────────────┐
│ 🔴 OUTSIDE NASA EXPERIMENTAL ENVELOPE                       │
│ Reason: Oxygen concentration (12.0%) is below minimum       │
│ tested flight limit (15.0%). Quantitative model suppressed. │
├─────────────────────────────────────────────────────────────┤
│ Closest Published NASA Flight Burns:                        │
│ 1. BASS-II Test 14 (O2 = 16.2%, Opposed Flow 10 cm/s)      │
│    Outcome: Extinguished after 4.2 seconds                   │
│ 2. BASS-II Test 19 (O2 = 17.0%, Opposed Flow 15 cm/s)      │
│    Outcome: Marginal spread / Extinction cliff              │
└─────────────────────────────────────────────────────────────┘
```

---

## 11.28 Standard Machine-Readable Reason Codes

```
UNSEEN_FUEL
UNSEEN_MATERIAL
OXYGEN_BELOW_RANGE
OXYGEN_ABOVE_RANGE
PRESSURE_BELOW_RANGE
PRESSURE_ABOVE_RANGE
FLOW_BELOW_RANGE
FLOW_ABOVE_RANGE
OXYGEN_NEAR_MINIMUM
FLOW_NEAR_MAXIMUM
SPARSE_LOCAL_SUPPORT
GEOMETRY_FAMILY_ONLY
REQUIRED_FEATURE_MISSING
MODEL_FAMILY_MISMATCH
```

---

## 11.29 Guard Output Contract (JSON Schema)

```json
{
  "status": "NEAR_BOUNDARY",
  "model_id": "flame_spread_gb",
  "hard_bounds_passed": true,
  "categorical_support": "EXACT",
  "local_support": {
    "k": 5,
    "distance": 0.194,
    "training_q90": 0.165,
    "training_q975": 0.248
  },
  "boundary_features": [
    {
      "feature": "oxygen_pct",
      "value": 16.2,
      "edge_proximity": 0.042,
      "limit": "min (15.0%)"
    }
  ],
  "reason_codes": [
    "OXYGEN_NEAR_MINIMUM",
    "SPARSE_LOCAL_SUPPORT"
  ],
  "nearest_experiments": [
    "BASS-II-EXP-042",
    "BASS-II-EXP-044",
    "BASS-II-EXP-049"
  ]
}
```

---

## 11.30 Scenario Walkthrough: INSIDE

* **Input:** PMMA solid slab, $21.0\% O_2$, $101.3\text{ kPa}$, $15.0\text{ cm/s}$ opposed flow.
* **Guard Processing:**
  - Material: Exact match in BASS-II.
  - Hard bounds: All within interior ranges.
  - Proximity: $E_j > 0.20$ across all features.
  - Local density: $D_k = 0.082 < Q_{90}$.
* **Status:** `INSIDE` $\longrightarrow$ Gradient Boosting predicts `spread` ($P = 0.89$).

---

## 11.31 Scenario Walkthrough: NEAR_BOUNDARY

* **Input:** PMMA solid slab, $16.2\% O_2$, $101.3\text{ kPa}$, $10.0\text{ cm/s}$ flow.
* **Guard Processing:**
  - $O_2$ is within range $[15.0\%, 34.0\%]$, but $(16.2 - 15.0)/(34.0 - 15.0) = 0.063 \approx$ edge.
  - In PMMA, $16.0\text{–}17.5\% O_2$ represents the empirical microgravity extinction cliff.
* **Status:** `NEAR_BOUNDARY` $\longrightarrow$ Predicts `marginal_spread` with warning banner.

---

## 11.32 Scenario Walkthrough: PARTIAL_SUPPORT

* **Input:** Cast acrylic variant, $18.0\% O_2$, $80.0\text{ kPa}$, $20.0\text{ cm/s}$ flow.
* **Guard Processing:**
  - Exact material not tested; falls back to `material_family = "acrylic polymer"`.
  - Environmental parameters valid.
* **Status:** `PARTIAL_SUPPORT` $\longrightarrow$ Model runs internally; UI emphasizes nearest PMMA burns.

---

## 11.33 Scenario Walkthrough: OUTSIDE

* **Input:** PMMA slab, $11.5\% O_2$, $101.3\text{ kPa}$, $15.0\text{ cm/s}$ flow.
* **Guard Processing:**
  - $O_2 = 11.5\% < 15.0\%$ minimum observed flight test.
* **Status:** `OUTSIDE` $\longrightarrow$ **Quantitative prediction suppressed.** UI displays: *"Lowest tested oxygen for PMMA is 15.0%. Nearest flight runs extinguished."*

---

## 11.34 The Experimental Support Map (Signature UI Visual)

In the frontend Mission Control view, FLARE-X renders an interactive 2D parameter slice:

```
      EXPERIMENTAL SUPPORT MAP (BASS-II SOLID FUELS)
  O₂ (%)
   35 ┌──────────────────────────────────────────────
      │                     ●        ●               
   30 │               ●  ●      ●       ●            
      │            ●         ●                       
   21 │         ●      ●   ★ YOU ARE HERE (INSIDE)   
      │      ●      ●                                
   17 │   ●   ●   (BOUNDARY ZONE)                    
   15 ├───●──────────────────────────────────────────
      │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
   10 │░░░░░░░░░ OUT OF DOMAIN (UNTESTED) ░░░░░░░░░░░
    0 └──────────────────────────────────────────────
      0        10        20        30        40     50
                     AIRFLOW (cm/s)
      ● NASA Spaceflight Burn    ★ Active Query Scenario
```

---

## 11.35 Family-Specific Support Map Slices

The visual representation automatically adapts to the active model family:
* **BASS-II (Solid):** Oxygen Concentration vs. Airflow Velocity (filtered by material).
* **FLEX (Droplet):** Oxygen Concentration vs. Total Pressure (filtered by fuel).
* **SPICE (Gas):** Coflow Velocity vs. Fuel Flow Rate (filtered by burner diameter).

---

## 11.36 The "You Are Here" Interactive Slider Experience

As the user manipulates parameter sliders:
1. At $21\% O_2$: Star is in dense green zone $\longrightarrow$ `INSIDE`.
2. Slider pulled to $17\% O_2$: Star moves into amber boundary zone $\longrightarrow$ `NEAR_BOUNDARY`.
3. Slider pulled to $14\% O_2$: Star enters gray cross-hatched region $\longrightarrow$ `OUTSIDE`. Model number disappears and turns into a warning, while nearest flight tests highlight below.

---

## 11.37 Counterfactual Integration

Counterfactual analysis executes the Guard independently on both scenarios:
* **Baseline:** $21\% O_2 \longrightarrow \texttt{INSIDE}$
* **Counterfactual:** $13\% O_2 \longrightarrow \texttt{OUTSIDE}$
* **System Action:** System prevents an ungrounded model comparison and explains: *"Model comparison truncated: counterfactual condition exceeds NASA-tested flammability limits."*

---

## 11.38 Decoupling Guard Support from Model Confidence

A neural network or tree ensemble may output a 98% class probability on complete garbage.
* Model Probability: *"Algorithm confidence"*
* Guard Support: *"Empirical NASA backing"*
* **Rule:** A high model probability under `PARTIAL_SUPPORT` or `NEAR_BOUNDARY` is rendered as **Low Overall Confidence**.

---

## 11.39 Decoupling Guard Support from Evidence Similarity

* **Evidence Similarity:** How close the single closest NASA experiment is.
* **Domain Support:** Whether the multidimensional space as a whole is populated with test density.
* Both metrics remain distinct and visible.

---

## 11.40 Training-Time Envelope Construction Protocol

1. Read verified training slice (`cache/experiments.parquet`).
2. Calculate feature-level $\min_j, \max_j$ and range.
3. Compute all pairwise training distances and derive $k$-NN distribution $D_k$.
4. Extract $Q_{90}$ and $Q_{97.5}$.
5. Serialize to `envelope.json` alongside model weights.
6. Zero test data leakage.

---

## 11.41 Guard Serialization Artifacts

```
models/
└── flame_spread_gb/
    ├── pipeline.joblib
    ├── envelope.json            # Hard bounds, Q90, Q97.5, weights
    ├── domain_reference.parquet  # Reference neighbor points
    ├── feature_schema.json      # Required vs optional fields
    └── model_card.md
```

---

## 11.42 Automated Guard Unit Test Suite

Verified in `tests/test_envelope.py`:
- [x] Typical interior flight condition $\longrightarrow$ `INSIDE`
- [x] Condition at $15.2\% O_2$ $\longrightarrow$ `NEAR_BOUNDARY`
- [x] Condition at $12.0\% O_2$ $\longrightarrow$ `OUTSIDE`
- [x] Unseen material (`"Polyurethane"`) $\longrightarrow$ `OUTSIDE`
- [x] Omitted oxygen field $\longrightarrow$ `UNKNOWN`
- [x] Valid 1D ranges but sparse combination $\longrightarrow$ `PARTIAL_SUPPORT`

---

## 11.43 Leave-One-Region-Out Stress Test

To prove the Guard detects empty space:
* Artificially excise all flight burns where $u_{\text{flow}} > 30\text{ cm/s}$.
* Query the Guard at $u = 35\text{ cm/s}$.
* **Verification:** Guard flags the query as `OUTSIDE` / `SPARSE_LOCAL_SUPPORT`, proving it does not blindly trust 1D max bounds.

---

## 11.44 Guard Explainability Panel

The UI explains every domain designation transparently:
```
┌─────────────────────────────────────────────────────────────┐
│ DOMAIN STATUS: NEAR BOUNDARY                                │
│ ✓ Material: PMMA (Verified in BASS-II)                      │
│ ✓ Chamber Pressure: 101.3 kPa (Inside normal range)         │
│ △ Oxygen: 16.5% (Within 1.5% of empirical extinction cliff) │
│ △ Airflow: 8.0 cm/s (Low density in flight archives)        │
└─────────────────────────────────────────────────────────────┘
```

---

## 11.45 Prohibition of Opaque Scalar "Domain Scores"

The primary interface renders explicit categorical states (`INSIDE`, `NEAR_BOUNDARY`, etc.) and physical explanations. Opaque scalars like `Domain Score: 0.742` are prohibited because they create an illusion of mathematical certainty where qualitative boundaries exist.

---

## 11.46 Impact on Evidence Auditor Behavior

The Evidence Auditor consumes the Guard's output:
* If domain is `OUTSIDE` and draft text contains predictive assertions $\longrightarrow$ **BLOCKED**.
* If domain is `NEAR_BOUNDARY` and draft text uses definitive language $\longrightarrow$ **REVISE** to conditional language.

---

## 11.47 Language Policy Governed by Domain Status

| Status | Mandatory Synthesizer Wording Rules |
| :--- | :--- |
| **`INSIDE`** | *"The model predicts steady flame propagation under these conditions..."* |
| **`NEAR_BOUNDARY`** | *"The model predicts extinction-leaning behavior, but conditions approach empirical limits..."* |
| **`PARTIAL_SUPPORT`** | *"Limited-support estimates suggest..., but primary guidance relies on nearby NASA burns..."* |
| **`OUTSIDE`** | *"NASA flight evidence is insufficient for authoritative model prediction. Nearest observations indicate..."* |
| **`UNKNOWN`** | *"Experimental support cannot be established due to unspecified physical parameters."* |

---

## 11.48 Automatic Emergence of Research-Gap Detection

Because the Guard quantifies $D_k$, sweeping parameter space automatically generates a **Microgravity Research-Gap Map**:
$$\text{Where } D_k(\mathbf{x}) > Q_{97.5} \implies \text{Unexplored Spaceflight Combustion Territory}$$
This provides aerospace researchers with immediate value: showing where future Artemis or ISS flight burns are urgently needed.

---

## 11.49 Competitive Advantage: Self-Restrained AI

Generic hackathon projects predict blindly across any input. FLARE-X gains credibility by demonstrating aerospace discipline:
$$\text{Query} \longrightarrow \text{Domain Check} \longrightarrow \text{Active Refusal if Unsupported} \longrightarrow \text{Ground Truth NASA Fallback}$$

---

## 11.50 Prescreening Video 1 Pitch Narration (25–30 Seconds)

> *"Before FLARE-X shows any model prediction, an Experimental Envelope Guard checks whether the requested fuel or material, oxygen level, pressure, flow, and geometry are actually supported by NASA flight experiments.*
> 
> *It combines hard empirical ranges with nearest-neighbor experiment density, flagging scenarios as inside, near the boundary, partially supported, or outside the evidence domain.*
> 
> *If a condition is unsupported, FLARE-X withholds an authoritative prediction and instead displays the nearest verified NASA evidence."*

---

## 11.51 The One-Line Pitch Anchor

> **“FLARE-X knows when not to predict. Its Experimental Envelope Guard checks whether a scenario is actually supported by NASA-tested conditions before trusting the model.”**

---

## 11.52 Locked Master Algorithm Flowchart

```
                          USER SCENARIO
                                │
                                ▼
                     Correct Model Family?
                                │
                 NO ────────────┴──────────── YES
                 │                             │
                 ▼                             ▼
        [OUTSIDE / ROUTE]            Required Inputs Present?
                                               │
                                 NO ───────────┴─────────── YES
                                 │                           │
                                 ▼                           ▼
                            [UNKNOWN]            Supported Categories?
                                                             │
                                               NO ───────────┴─────────── YES
                                               │                           │
                                               ▼                           ▼
                                           [OUTSIDE]             Hard Numeric Bounds?
                                                                           │
                                                             NO ───────────┴─────────── YES
                                                             │                           │
                                                             ▼                           ▼
                                                         [OUTSIDE]             Boundary Proximity?
                                                                                       │
                                                                         YES ──────────┴────────── NO
                                                                         │                          │
                                                                         ▼                          ▼
                                                                  [NEAR_BOUNDARY]         Compute k-NN Density
                                                                                                    │
                                                                               Dk > Q97.5 ──────────┴────────── Dk <= Q90
                                                                               │                                  │
                                                                               ▼                                  ▼
                                                                       [PARTIAL_SUPPORT]                      [INSIDE]
```

---

## 11.53 Phase 11 Acceptance Gate

- [x] Purpose and positioning of the Guard finalized.
- [x] Family-specific envelope schemas defined (SPICE, FLEX, BASS-II).
- [x] Five domain statuses locked (`INSIDE`, `NEAR_BOUNDARY`, `PARTIAL_SUPPORT`, `OUTSIDE`, `UNKNOWN`).
- [x] Five sequential checks specified and verified in code.
- [x] 5% edge boundary proximity ($E_j \le 0.05$) formalized.
- [x] Multi-dimensional weighted Gower metric formulated.
- [x] Nearest-neighbor support ($k=5$) and data-adaptive thresholds ($Q_{90}, Q_{97.5}$) locked.
- [x] Conservative precedence hierarchy locked.
- [x] Prediction rendering policy locked (extrapolation suppression).
- [x] JSON output contract specified.
- [x] Interactive Support Map visual defined.
- [x] Language policies governing Synthesizer and Auditor enforced.
- [x] Automated unit test suite passing (`tests/test_envelope.py`).

---

## ✅ Phase 11 Status: COMPLETE

The Experimental Envelope Guard is formally codified, verified, and locked.

We now advance to **Phase 12: NASA Evidence & Provenance System** (evidence bundle schemas, persistent DOI resolution, claim-level provenance linking, source authority hierarchies, contradictory evidence resolution, and the "Why should I trust this?" audit trail).
