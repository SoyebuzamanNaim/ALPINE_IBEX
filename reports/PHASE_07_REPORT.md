# Phase 07 Report: Experimental Envelope Guard

## Executive Summary
Phase 07 delivers the strict domain boundary protection system for FLARE-X. Microgravity combustion models trained on empirical spaceflight datasets cannot physically predict behavior outside the tested parameter space. Rather than failing or generating ungrounded hallucinations, the Experimental Envelope Guard acts as an immutable firewall.

## Deliverables Completed
1. **Core Guard Module (`src/envelope/guard.py`):**
   - Implements `EnvelopeGuard` class reading `models/model_meta.json` and `cache/experiments.parquet`.
   - Four operational statuses: `in_domain`, `boundary`, `extrapolation`, `unsupported_category`.
   - Global numerical bounding box check for `oxygen_pct`, `pressure_kpa`, `flow_cm_s`.
   - Per-material specific boundary constraints matching literature limits.
   - 3-Nearest-Neighbor density evaluation alerting users when conditions fall into sparse data regimes.
   - Refusal contract preserving nearest real NASA flight test points.
2. **Methodology Documentation (`docs/ENVELOPE_METHOD.md`):**
   - Details safety rationale, defensive tiers, and refusal contract specification.
3. **Automated Test Suite (`tests/test_envelope.py`):**
   - 6 comprehensive tests covering in-domain, near-extinction boundary, global bounds violation, unsupported materials, per-material bounds, and sparse data detection.
4. **Validation Documentation (`reports/ENVELOPE_VALIDATION.md`, `reports/PHASE_07_VALIDATION.md`):**
   - Verification matrix and pass criteria verification.

## Quantitative Metrics
- Global Oxygen Limits: [15.0%, 34.0%]
- Global Pressure Limits: [56.5 kPa, 101.3 kPa]
- Global Flow Limits: [0.0 cm/s, 45.0 cm/s]
- Supported Materials: `PMMA` (92), `Cellulose` (22), `Cotton` (19), `Nomex` (7), `Delrin` (5)
- Density Threshold: $d_{3NN} > 0.35$ triggers sparse region alert
