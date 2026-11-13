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

## Evidence presentation

Nearest records use numerical similarity ranking over oxygen, pressure and airflow, with a
material penalty. Each record carries the score components, observed geometry and direction,
and a deterministic summary of the observation, input differences and inference limits.
Unspecified query context and unstructured ignition history are displayed as unknown rather
than assumed to match. Ranking does not measure scientific reliability.

The composer uses deterministic templates by default. The auditor checks numeric values and
citation identifiers; it does not establish scientific entailment. The public API does not
call a generative model, and candidate text is never released. Any future generative summaries need source-preserving semantic
claim checks before publication.

Coverage counts describe only the indexed FLARE-X table. Empty bins make no literature-wide
absence claim. Proposed studies are labeled as team proposals with computed dataset counts.

`POST /evidence` and `/reports/search` are independent of the optional classifier. Invalid
or missing model artifacts degrade only model features rather than stopping evidence startup.
The evidence desk shows source observations first, offers a cited JSON download, and puts
model estimates behind an explicit disclosure. Provenance uses canonical rows directly;
the exported registry cannot override current test conditions or fill missing values by guess.

Study comparisons report recorded dimensions and missing context rather than a weighted
comparability score or causal explanation. The standalone prediction helper, model router,
counterfactual engine and API share the same research-release integrity checks.

GitHub Pages serves static assets; its build requires `FLARE_API_BASE` and writes `app/config.js`.
A fresh-browser acceptance check exercises the real evidence workflow before publishing and
again at the exact published URL. See [public demo deployment](DEPLOYMENT.md).

## Inference gate

The checked-in linear SVM has 200 training rows and an 84.0% exploratory grouped selection score against an 81.5% majority baseline. Guarded research estimates are available; this score was used for selection and is not independent validation. The full search procedure's nested accuracy is 25.5%, which evaluates model selection rather than the fixed SVM alone. Probabilities have not been validated across reports.

The API verifies dataset and model artifact hashes against the loaded metadata. A failed integrity or baseline check returns `model_unvalidated` for an otherwise eligible `/predict` request and HTTP 503 for model-dependent visualization routes. Domain violations, identical-input outcome conflicts, and insufficient material coverage produce explicit abstentions. A final explanation audit failure clears prediction and probability fields before the response is returned.

The request limiter is process-local and keyed by the socket client address. A multi-worker or proxy deployment needs a shared edge limiter configured with trusted proxy handling; the application does not trust arbitrary forwarded client-address headers.
