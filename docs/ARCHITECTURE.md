# Architecture

FLARE-X is a local research application with a static browser UI and a FastAPI backend. The backend loads the curated experiment table, model artifact, NASA report corpus, and dataset catalog from the repository.

```text
NASA / PSI source records
        │ curated and validated
        ▼
data/processed ──► src/ingestion/build_table.py ──► cache/experiments.parquet
                                                        │
                          ┌─────────────────────────────┼──────────────────────┐
                          ▼                             ▼                      ▼
                  EnvelopeGuard                 ModelRouter             Evidence retrieval
                  joint domain,                 model artifact,         nearest observations,
                  sparse/conflict checks        hash and baseline gate  report corpus
                          └─────────────────────────────┬──────────────────────┘
                                                        ▼
                                            AgentOrchestrator
                                      explanation composition and audit
                                                        │
                                                        ▼
                                    FastAPI API + app/ browser interface
```

## Main components

- `src/ingestion/` validates curated records and builds canonical Parquet/CSV tables and provenance metadata.
- `src/compute/model.py` trains the classifier, performs grouped validation, and writes model artifacts and generated reports.
- `src/envelope/` checks scalar ranges, joint empirical coverage, conflicting observations, and sparse materials before inference.
- `src/agents/` interprets scenario text, retrieves and composes evidence, audits the final explanation, and withholds failed results.
- `src/features/` and `src/analysis/` implement counterfactual sweeps, study comparisons, coverage summaries, and provenance lookup.
- `src/api/` exposes these functions through FastAPI, validates request fields, caps bodies at 64 KiB, and applies per-client request limits.
- `app/` contains the static frontend.

## Inference gate

The checked-in linear SVM has 200 training rows and an 84.0% exploratory grouped selection score against an 81.5% majority baseline. Guarded research estimates are available; this score was used for selection and is not independent validation. The full search procedure's nested accuracy is 25.5%, which evaluates model selection rather than the fixed SVM alone. Probabilities have not been validated across reports.

The API verifies dataset and model artifact hashes against the loaded metadata. A failed integrity or baseline check returns `model_unvalidated` for an otherwise eligible `/predict` request and HTTP 503 for model-dependent visualization routes. Domain violations, identical-input outcome conflicts, and insufficient material coverage produce explicit abstentions. A final explanation audit failure clears prediction and probability fields before the response is returned.

The request limiter is process-local and keyed by the socket client address. A multi-worker or proxy deployment needs a shared edge limiter configured with trusted proxy handling; the application does not trust arbitrary forwarded client-address headers.
