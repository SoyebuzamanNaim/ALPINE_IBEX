# System Architecture & Technical Specifications (Phase 15)

> **Document Status:** Authoritative technical architecture documentation for FLARE-X.

## 1. High-Level Architectural Topology

```
┌────────────────────────────────────────────────────────────────────────┐
│                        NASA PSI & NTRS ARCHIVES                        │
│               (BASS, BASS-II, DARTFire, Exploration Atm)               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Pre-event Extraction
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          LOCAL CACHED DATA                             │
│     cache/experiments.parquet (145 rows, SHA-256 verified)             │
│     cache/report_corpus/*.json (13 verified NASA NTRS abstracts)       │
└──────────────┬────────────────────────────────────────────┬────────────┘
               │                                            │
               ▼                                            ▼
┌──────────────────────────────┐             ┌───────────────────────────┐
│     GRADIENT BOOSTING        │             │   RETRIEVAL & CITATION    │
│  src/compute/model.py        │             │  src/retrieval/nearest.py │
│  Honest Grouped CV: 79.31%   │             │  BM25 corpus_search.py    │
└──────────────┬───────────────┘             └──────────────┬────────────┘
               │                                            │
               └──────────────────────┬─────────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       EXPERIMENTAL ENVELOPE GUARD                      │
│                          src/envelope/guard.py                         │
│   • Global Bounding Box Checks (O2: 15-34%, P: 56.5-101.3 kPa)         │
│   • Per-Material Flight Envelope Constraints                           │
│   • kNN-Distance (d_3NN > 0.35) Data Density Warning                   │
│   • Non-Negotiable Refusal Firewall (prediction: null)                 │
└─────────────────────────────────────┬──────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   FINITE-STATE AGENT ORCHESTRATOR                      │
│                        src/agents/orchestrator.py                      │
│   ScenarioInterpreter ──► ModelRouter ──► EvidenceRetriever            │
│         ▲                                       │                      │
│         │                                       ▼                      │
│   Refusal/Ambiguity                    ExplanationComposer             │
│         │                                       │                      │
│         └─────────── EvidenceAuditor ◄──────────┘                      │
│                      (Strict Regex Numerical Check)                    │
└─────────────────────────────────────┬──────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       FASTAPI REST SERVICE & UI                        │
│                           src/api/main.py                              │
│   • POST /predict (Section 7 Contract)     • GET /health               │
│   • GET /boundary (2-D Slice Contours)     • GET /experiments          │
│   • POST /counterfactual (Perturbations)   • GET /model                │
│   • POST /sweep (Regime Boundaries)        • Static / (Mission App)    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Invariant Safety Guarantees

1. **Strict Rejection of Extrapolation:** In standard spacecraft fire safety, silent model extrapolation into unverified regimes is unacceptable. The `EnvelopeGuard` acts as an immutable firewall. If conditions fall outside tested limits, `prediction` and `probabilities` are returned as `null`, accompanied by explicit parameter-level reason dictionaries.
2. **Nearest Evidence Retention:** Whenever extrapolation refusal occurs, the top 3 nearest historical NASA experiments are still attached to the response. This ensures engineers and flight controllers see exactly what has been tested.
3. **Regex Numerical Hallucination Check:** Explanation texts are parsed with regular expressions. Any number or citation not matching an authorized value in the prediction payload is flagged and rejected, instantly triggering fallback to a verified deterministic template.
4. **Zero Mocked Metrics:** All evaluation scores (79.31% grouped accuracy, 51.72% baseline) are computed dynamically from `models/flame_spread_gb.joblib` and persisted in `models/model_meta.json`.
