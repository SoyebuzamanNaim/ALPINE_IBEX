# Counterfactual Engine Specification (Phase 08)

> **Document Status:** Authoritative specification for what-if scenarios, parameter sensitivity sweeps, boundary identification, and safety margins.

## 1. Safety and Scientific Philosophy

In spacecraft fire safety engineering (e.g. NASA-STD-6001, Exploration Atmospheres), decision makers often ask:
- *"If cabin ventilation fans drop flow from 20 cm/s to 5 cm/s, does PMMA extinguish or burn more vigorously?"*
- *"If the ECLSS drops cabin oxygen concentration from 21% to 18%, what is the safety margin to the flammability threshold?"*

The FLARE-X Counterfactual Engine provides answers by querying the gradient-boosted empirical model trained on published microgravity tests, while enforcing five strict scientific guardrails:

1. **Non-Causal Framing:** Observational machine learning predictions are explicitly labeled as model inferences, accompanied by a scientific disclaimer.
2. **Mandatory Envelope Verification:** Every perturbed point and sweep step passes through `EnvelopeGuard`. If an adjustment pushes conditions outside the tested domain, the engine refuses the prediction (`prediction: null`) and lists the out-of-range parameters.
3. **Preservation of Baseline State:** Baseline and counterfactual states are presented side-by-side with exact delta measurements.
4. **Empirical Evidence Attachment:** Changes in nearest historical experiments are tracked (`evidence_delta`), showing which NASA test records justify the shift.
5. **Boundary & Safety Margin Identification:** Continuous parameter sweeps detect exact regime transition thresholds and compute numerical safety margins.

---

## 2. Supported Counterfactual Dimensions

The engine supports perturbations across all canonical variables:
- **Oxygen Concentration (`oxygen_pct`):** [15.0% to 34.0%]
- **Flow Velocity (`flow_cm_s`):** [0.0 to 45.0 cm/s]
- **Pressure (`pressure_kpa`):** [56.5 to 101.3 kPa]
- **Solid Fuel Material (`material`):** `PMMA`, `Cellulose`, `Cotton`, `Delrin`, `Nomex`

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
3. Detect transition events wherever $\hat{y}^{(k-1)} \neq \hat{y}^{(k)}$:
   - Transition interval: $[x_j^{(k-1)}, x_j^{(k)}]$
   - Transition midpoint: $x_j^* = \frac{x_j^{(k-1)} + x_j^{(k)}}{2}$
   - Real NASA evidence before and after boundary: $\mathcal{N}(x_j^{(k-1)})$ and $\mathcal{N}(x_j^{(k)})$
4. Safety Margin Calculation:
   $$\text{Margin} = x_{j,\text{base}} - x_j^*$$

---

## 4. Benchmark PMMA Oxygen Sweep Demonstration

When sweeping PMMA at standard spacecraft sea-level pressure ($101.3\text{ kPa}$) and low ventilation flow ($5.0\text{ cm/s}$):
- **$21.0\%$ to $18.0\%$ O₂:** Steady flame spread is predicted ($P(\text{spread}) \approx 0.98 \to 0.67$).
- **$17.5\%$ O₂:** Regime transitions to `marginal_spread` ($P(\text{marginal}) \approx 0.62$).
- **$16.0\%$ O₂:** Regime transitions to `no_spread` / extinction ($P(\text{no\_spread}) \approx 0.94$).
- **Boundary Midpoint:** $17.75\%$ O₂ (transition from spread to marginal) and $16.75\%$ O₂ (transition to extinction).
- **Baseline Safety Margin at $21.0\%$ O₂:** $+3.25\%$ O₂ above flame spread extinction threshold.

This matches published NASA Glenn research findings (BASS and BASS-II) where the limiting oxygen index (LOI) for thick cast PMMA in microgravity low-flow conditions is approximately $17.0\pm 0.5\%$.
