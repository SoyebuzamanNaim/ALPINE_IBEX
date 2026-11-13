# Counterfactual engine

> **Document Status:** Implemented research specification for guarded what-if scenarios and model sweeps. Estimates are exploratory and do not establish operational safety.

## 1. Safety and Scientific Philosophy

In spacecraft fire safety engineering (e.g. NASA-STD-6001, Exploration Atmospheres), decision makers often ask:
- *"If cabin ventilation fans drop flow from 20 cm/s to 5 cm/s, does PMMA extinguish or burn more vigorously?"*
- *"How does the research model's estimate change as cabin oxygen varies?"*

The `/counterfactual` and `/sweep` routes query the serving linear SVM against published microgravity tests. Its 84.0% grouped selection score exceeds the 81.5% majority baseline, enabling research estimates. The full search procedure scored 25.5% under nested report validation; no independent accuracy improvement or probability calibration is established. The design requires five scientific guardrails:

1. **Non-Causal Framing:** Observational machine learning predictions are explicitly labeled as model inferences, accompanied by a scientific disclaimer.
2. **Mandatory Envelope Verification:** Every perturbed point and sweep step passes through `EnvelopeGuard`. If an adjustment pushes conditions outside the tested domain, the engine refuses the prediction (`prediction: null`) and lists the out-of-range parameters.
3. **Preservation of Baseline State:** Baseline and counterfactual states are presented side-by-side with exact delta measurements.
4. **Empirical Evidence Attachment:** Changes in nearest historical experiments are tracked (`evidence_delta`), showing which NASA test records justify the shift.
5. **Model Transition Identification:** Sweeps report intervals where the model class changes between adjacent sampled points. These are discretized model transitions, not physical safety limits.

---

## 2. Supported Counterfactual Dimensions

The engine accepts changes to `oxygen_pct`, `flow_cm_s`, `pressure_kpa`, and
`material`. Public request values use the bounds in `PredictRequest`; empirical
support is narrower and determined from current model metadata and the joint
experimental domain. Unknown change keys and invalid merged scenarios return
HTTP 422. Every sampled point can independently abstain.

---

## 3. Mathematical & Algorithmic Formulation

### 3.1 Single-Point Perturbation (`compute_perturbation`)
Given baseline scenario $\mathbf{x}_{\text{base}} = [O_2, P, v, M]$ and modification vector $\Delta \mathbf{x}$:
1. Compute $\mathbf{x}_{\text{cf}} = \mathbf{x}_{\text{base}} \oplus \Delta \mathbf{x}$.
2. Evaluate $\mathcal{E}(\mathbf{x}_{\text{base}})$ and $\mathcal{E}(\mathbf{x}_{\text{cf}})$ using `EnvelopeGuard`.
3. If both in-domain:
   $$\Delta \hat{y} = (\hat{y}_{\text{base}} \neq \hat{y}_{\text{cf}})$$
   $$\Delta P(c) = P_{\text{cf}}(c) - P_{\text{base}}(c) \quad \forall c \in \{\text{no\_spread}, \text{marginal\_spread}, \text{spread}\}$$
4. Compute nearest-evidence set differences:
   $$\mathcal{S}_{\text{shared}} = \mathcal{N}(\mathbf{x}_{\text{base}}) \cap \mathcal{N}(\mathbf{x}_{\text{cf}})$$
   $$\mathcal{S}_{\text{added}} = \mathcal{N}(\mathbf{x}_{\text{cf}}) \setminus \mathcal{N}(\mathbf{x}_{\text{base}})$$
   $$\mathcal{S}_{\text{removed}} = \mathcal{N}(\mathbf{x}_{\text{base}}) \setminus \mathcal{N}(\mathbf{x}_{\text{cf}})$$

### 3.2 Parameter Sweep & Boundary Transition Detection (`run_sweep`)
For a designated sweep variable $x_j \in [x_{\text{start}}, x_{\text{end}}]$ with $N$ steps:
1. Generate uniform grid: $x_j^{(k)} = x_{\text{start}} + k \frac{x_{\text{end}} - x_{\text{start}}}{N - 1}$ for $k \in \{0, \dots, N-1\}$.
2. At each grid point $k$, evaluate $\hat{y}^{(k)}$ and class probabilities.
3. Detect transition events where both adjacent points have predictions and $\hat{y}^{(k-1)} \neq \hat{y}^{(k)}$:
   - Transition interval: $[x_j^{(k-1)}, x_j^{(k)}]$
   - Transition midpoint: $x_j^* = \frac{x_j^{(k-1)} + x_j^{(k)}}{2}$
   - Real NASA evidence before and after boundary: $\mathcal{N}(x_j^{(k-1)})$ and $\mathcal{N}(x_j^{(k)})$
4. Select the transition involving `no_spread` nearest the baseline value,
   independent of traversal direction. The legacy `safety_margin` key reports
   signed `delta_to_boundary = baseline_value - boundary_midpoint`,
   `baseline_predicted_regime`, and `is_no_spread_side`. It never reports
   `is_safe_side`. If the baseline abstains, the field is `null`.

---

## 4. Current Availability

`/counterfactual` and `/sweep` currently serve guarded research estimates and
include the model's research status and limitations. They return HTTP 503 if
the dataset/artifact integrity checks or grouped-baseline gate fail. Refused
sweep points have null predictions and probabilities; the UI leaves gaps in
the probability curves rather than drawing them at zero. These results are
not flight-safety decisions.
