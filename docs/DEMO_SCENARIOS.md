# Repeatable Demo Scenarios (Phase 14)

> **Document Status:** Authoritative specification for repeatable demonstration scenarios for hackathon judges, prescreening videos, and scientific evaluations.
> **Classification:** RESEARCH PROTOTYPE DEMONSTRATION

---

## Scenario 1: Strong In-Domain Spacecraft Baseline (ISS Standard)

### Operational Context
A mission safety officer evaluates fire risk for cast acrylic (PMMA) hardware stored inside an International Space Station (ISS) rack under standard atmospheric composition and low-speed ventilation fan operation.

### Exact Inputs
- **Solid Fuel Material:** `PMMA` (Polymethyl Methacrylate)
- **Oxygen Concentration:** `21.0%`
- **Cabin Pressure:** `101.3 kPa` (1.0 atm)
- **Ventilation Velocity:** `5.0 cm/s` (Opposed forced airflow)

### Expected System Output
- **In-Training-Range:** `true` (Domain Status: `in_domain`)
- **Predicted Regime:** `spread` (Sustained flame propagation)
- **Calibrated Probabilities:**
  - `spread`: **97.7%**
  - `marginal_spread`: **1.5%**
  - `no_spread`: **0.8%**
- **Nearest Empirical NASA Evidence:**
  1. `EXP_BASS_001` (BASS / ISS) — $21.0\%$ O₂, $101.3\text{ kPa}$, $5.0\text{ cm/s}$ → `spread` ([NTRS 20160010041](https://ntrs.nasa.gov/citations/20160010041))
  2. `EXP_BASS_044` (BASS / ISS) — $18.0\%$ O₂, $101.3\text{ kPa}$, $5.0\text{ cm/s}$ → `spread` ([NTRS 20140011099](https://ntrs.nasa.gov/citations/20140011099))
  3. `EXP_BASS_012` (BASS / ISS) — $21.0\%$ O₂, $101.3\text{ kPa}$, $7.5\text{ cm/s}$ → `spread` ([NTRS 20160010041](https://ntrs.nasa.gov/citations/20160010041))
- **Operator Safety Briefing:** Active opposed airflow continuously feeds convective oxidizer to the flame base, overpowering microgravity radiative heat losses. Flammability risk is elevated.

---

## Scenario 2: Near-Boundary Transition & Oxygen Sweep (Killer Demo / Brief §2)

### Operational Context
Demonstrating the physical limiting oxygen concentration (LOC) boundary where microgravity flames transition from steady propagation to marginal oscillations and self-extinction.

### Exact Inputs & Sweep
- **Material:** `PMMA`
- **Cabin Pressure:** `101.3 kPa`
- **Ventilation Velocity:** `5.0 cm/s`
- **Oxygen Depletion Sweep:** Sweep from `21.0%` down to `16.0%` O₂

### Expected System Output
- **Boundary Crossover Point:** **$17.5\%$ O₂**
  - At $21.0\%$ O₂: $P(\text{spread}) \approx 98\%$
  - At $18.0\%$ O₂: $P(\text{spread}) \approx 67\%$ (near edge)
  - At $17.5\%$ O₂: transitions to `marginal_spread` ($P(\text{marginal}) \approx 62\%$)
  - At $16.5\%$ O₂: transitions to `no_spread` / extinction ($P(\text{no\_spread}) \approx 73\%$)
  - At $16.0\%$ O₂: $P(\text{no\_spread}) \approx 94\%$
- **Extinction Safety Margin at 21.0% O₂:** **$+3.25\%$ O₂** buffer above extinction limit
- **Nearest Evidence Cited on BOTH Sides of Boundary:**
  - **Above Boundary ($O_2 > 17.5\%$):** NTRS report `20160010041` ($20.8\%$ O₂, spread observed).
  - **Below Boundary ($O_2 \le 17.0\%$):** NTRS report `20140011099` ($16.5\%$ O₂, extinction / no spread observed).

---

## Scenario 3: Out-of-Domain Refusal (Extrapolation & Category Firewall)

### Operational Context
A user attempts to predict flammability in an unverified hyperoxic atmosphere (45% O2) or on an unverified spacecraft polymer (e.g. Kapton or Teflon).

### Exact Inputs
- **Case 3A (Atmospheric Extrapolation):** `PMMA`, `45.0%` O₂, `101.3 kPa`, `5.0 cm/s`
- **Case 3B (Unsupported Category):** `Kapton`, `21.0%` O₂, `101.3 kPa`, `5.0 cm/s`

### Expected System Output
- **In-Training-Range:** `false`
- **Status:** `extrapolation` (Case 3A) or `unsupported_category` (Case 3B)
- **Predictions & Probabilities:** Strictly `null`
- **Reason Structure:**
  ```json
  "out_of_range_reasons": [
    {
      "feature": "oxygen_pct",
      "value": 45.0,
      "train_min": 15.0,
      "train_max": 34.0,
      "reason": "Oxygen concentration 45.0% is outside global training envelope [15.0%, 34.0%]."
    }
  ]
  ```
- **Nearest NASA Experiments:** 3 closest real experiments are **retained and displayed** so the operator sees the empirical testing boundaries established by NASA.
- **Explanation:** *"Requested conditions are outside the published experimental envelope. No prediction is made."*
