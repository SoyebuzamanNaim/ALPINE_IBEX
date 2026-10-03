# Phase 08 Report: Counterfactual Engine

## Executive Summary
Phase 08 implements the interactive what-if and parameter sweep capability for FLARE-X. In spacecraft fire safety, operations personnel must understand how changing ventilation speeds, cabin depressurization, or oxygen reduction alters the flammability state of materials. The Counterfactual Engine allows users to perturb variables, compute multi-point continuous sweeps, detect empirical regime boundaries, and measure safety margins, all while strictly adhering to domain guards.

## Deliverables Completed
1. **Engine Core (`src/features/counterfactual.py`):**
   - Implements `CounterfactualEngine` class.
   - `evaluate_scenario`: unified prediction and envelope guard interface.
   - `compute_perturbation`: computes variable deltas, prediction shifts, probability shifts, and evidence deltas.
   - `run_sweep`: multi-step 1D sweep across continuous variables with regime boundary transition detection and safety margin calculation.
   - Non-causal scientific disclaimer embedded in all outputs.
2. **Technical Specification (`docs/COUNTERFACTUAL_SPEC.md`):**
   - Mathematical formulation of perturbations and sweeps.
   - Verification of PMMA oxygen sweep benchmark against NASA BASS/BASS-II limiting oxygen indices (~17.0% O2).
3. **Automated Test Suite (`tests/test_counterfactual.py`):**
   - 6 comprehensive tests covering in-domain evaluation, out-of-range refusal, oxygen perturbation, oxygen boundary sweep with transition detection, invalid sweep parameters, and unsupported material refusal.
4. **Validation Documentation (`reports/PHASE_08_VALIDATION.md`):**
   - Full test run audit and compliance verification.

## Quantitative Validation
- PMMA 21.0% O2 to 16.0% O2 sweep reliably detects regime transitions from `spread` to `marginal_spread` (at ~17.5% O2) to `no_spread` (at ~17.0% O2).
- Real empirical NASA experiments cited on both sides of the boundary (BASS flight test points).
- Safety margin of +3.25% O2 above extinction threshold calculated for 21.0% O2 ambient conditions.
