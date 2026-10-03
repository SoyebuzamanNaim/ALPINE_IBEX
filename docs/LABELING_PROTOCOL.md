# Labeling Protocol: Flame-Spread Regimes (Phase 03)

> **Document Status:** Authoritative scientific protocol for categorizing microgravity combustion observations
> into target regime classes.

## 1. Target Classes

Microgravity solid fuel flammability is mapped into three distinct physical regimes:

| Target Class | Physical Definition | Spacecraft Safety Significance |
|---|---|---|
| `no_spread` | The ignition flame fails to establish, self-extinguishes immediately after igniter de-energization, or undergoes total blowoff/quench. No flame propagation across the solid surface. | Non-flammable / inherently safe under the specified atmosphere and flow conditions. |
| `marginal_spread` | A weak, unstable, or flickering flame survives near the flammability limit. Spreads unsteadily, exhibits partial surface regression, or slowly fades toward delayed extinction. | High-risk hazard: flame may survive undetected in ventilation dead-zones and transition to vigorous burning if airflow increases. |
| `spread` | A self-sustaining flame propagates steadily along the solid fuel surface until fuel is consumed or external intervention occurs. | Unsafe / catastrophic fire hazard: sustained combustion requiring immediate suppression. |

---

## 2. Textual Mapping Rules

Published NASA technical reports describe outcomes using PI narrative notes, table columns, and experimental remarks.
The following deterministic mapping rules are applied:

| Raw Literature Wording / Keywords | Assigned Class | Interpretation Required? (`outcome_interpreted`) |
|---|---|---|
| `"extinguished immediately"`, `"no ignition"`, `"failed to ignite"`, `"immediate extinction"`, `"quenched"`, `"blowoff"`, `"no flame"` | `no_spread` | False (Direct observation) |
| `"extinguished after flow turned off"`, `"self-extinguished"`, `"spread < 5 mm then out"`, `"did not sustain"` | `no_spread` | False (Direct observation) |
| `"flickering"`, `"near-limit"`, `"unsteady spread"`, `"weak blue flame"`, `"marginal"`, `"decaying flame"`, `"intermittent burning"`, `"oscillating"` | `marginal_spread` | True (Rule applied) |
| `"slow spread near extinction"`, `"limitation boundary"`, `"partial consumption with fade"` | `marginal_spread` | True (Rule applied) |
| `"steady spread"`, `"sustained spread"`, `"propagated along rod"`, `"burned to end"`, `"robust flame"`, `"vigorous burning"`, `"steady flame"` | `spread` | False (Direct observation) |
| `"multiple velocities for steady spread"`, `"spread rate = X mm/s"` (where rate > 0) | `spread` | False (Direct observation) |

---

## 3. Ambiguity Resolution & Conflict Protocol

1. **Velocity Sweeps within Single Run:** In several BASS-II tests (e.g. B10, B11), the astronaut varied fan speeds from 5 cm/s down to 0.35 cm/s within a single test run to locate the low-speed extinction boundary.
   - For conditions where the flame spread steadily, a row is recorded as `spread`.
   - At the specific velocity where the flame faded and extinguished (e.g. at 0.35 cm/s), a separate discrete condition row is recorded as `no_spread` (or `marginal_spread` if hovering before extinction).
2. **Flagging:** Every row where the outcome was inferred from narrative notes rather than an explicit "Outcome" column must have `outcome_interpreted: true`.
3. **Quarantine:** If a publication notes "video lost", "camera malfunction", or "ambiguous test point without visual confirmation", that row is excluded from model training and quarantined.
