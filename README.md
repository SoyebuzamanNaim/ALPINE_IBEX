# FLARE-X

FLARE-X is a research prototype for exploring NASA microgravity combustion observations. It provides a FastAPI service and a browser interface for evidence lookup, experimental-domain checks, comparisons, and model exploration. It is not a fire-safety certification or operational decision system.

## Current model status

The checked-in dataset contains 200 observations. The current grouped cross-validation accuracy is 76.0%, below the 81.5% majority-class baseline. Public model inference is therefore withheld for otherwise eligible conditions. The API returns `model_unvalidated` with no prediction or probabilities. Out-of-domain, conflicting, and sparse-material cases also abstain. See [scientific limitations](docs/LIMITATIONS.md) and the [rebuilt model evaluation](reports/REBUILT_MODEL_EVALUATION.md).

## Quick start

Requires Python 3.12 or newer.
`requirements.txt` pins the runtime, test, and transitive Python packages used by CI.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./scripts/run_local.sh
```

Open <http://localhost:8000> for the Mission Control UI and <http://localhost:8000/docs> for the interactive API documentation. The launcher uses the checked-in dataset and model artifacts; if either is missing, it rebuilds or trains it.

Run the existing test suite with:

```bash
.venv/bin/pytest -q
```

GitHub Actions runs the same suite on Python 3.12 and 3.14, checks JavaScript syntax, and verifies the checked-in model artifacts against the dataset hash and evaluation metrics.

## What is included

- Curated observation data and source provenance in `data/`, `cache/`, and `reports/`.
- Input-domain checks and abstention rules in `src/envelope/`.
- Model training and validation in `src/compute/model.py`.
- Evidence retrieval and explanation auditing in `src/retrieval/` and `src/agents/`.
- Counterfactual and coverage analysis in `src/features/` and `src/analysis/`.
- FastAPI routes and request guards in `src/api/`.
- The browser application in `app/`.

## Rebuild data and model artifacts

The ingestion pipeline reads the curated source tables in `data/processed/` and writes the canonical tables and provenance report:

```bash
.venv/bin/python -m src.ingestion.build_table
```

Train and evaluate the model from the canonical Parquet table with:

```bash
.venv/bin/python src/compute/model.py
```

Training overwrites model metadata, model metrics, and generated model reports. The API checks the dataset SHA-256 against model metadata and refuses inference when they differ.

## Repository map

```text
app/          Browser UI and static assets
cache/        Runtime dataset and report corpus
data/         Source, interim, processed, and metadata records
docs/         Maintained project, API, data, and limitation documentation
models/       Serialized model and current metadata
project-page/ Static research overview deployed with GitHub Pages
reports/      Data-quality and model-evaluation evidence
scripts/      Local launcher and catalog builder
src/          API, agents, ingestion, model, analysis, and retrieval code
tests/        Python and browser-runtime regression tests
```

See [architecture](docs/ARCHITECTURE.md), [API contract](docs/API_CONTRACT.md), and [reproduction guide](docs/REPRODUCIBILITY.md) for implementation details.
