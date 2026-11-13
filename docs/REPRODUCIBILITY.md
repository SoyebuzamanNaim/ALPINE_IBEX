# Reproduction guide

This guide rebuilds the dataset and model artifacts from the source files checked into this repository. The ingestion process does not download missing NASA documents; it reads the curated source tables in `data/processed/`.

## Environment

Use Python 3.12 or newer. `requirements.txt` is a fully pinned environment lock, including transitive and test packages:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Rebuild the canonical dataset

```bash
.venv/bin/python -m src.ingestion.build_table
```

This rebuilds `cache/experiments.parquet`, `data/processed/experiments.parquet`, CSV/interim exports, the provenance registry, and `reports/DATA_QUALITY.md`. Validation counts are recorded in `data/interim/ingestion_audit.json`. If any selected source row fails schema validation, the row and errors are written to `data/interim/quarantine.json` and the command stops before overwriting canonical tables. The checked-in canonical table currently contains 200 rows. The API checks both the dataset and serialized model SHA-256 values against `models/model_meta.json` before allowing inference.

## Train and evaluate

```bash
.venv/bin/python src/compute/model.py
```

This writes `models/flame_spread_gb.joblib`, `models/model_meta.json`, `models/metrics.json`, `reports/BASELINE_RESULTS.md`, and `docs/MODEL_CARDS.md`. Training is a mutating operation: it replaces these artifacts with results from the current dataset and code. Review the generated diffs before committing them.

The serving linear SVM reports an 84.0% exploratory grouped selection score and an 81.5% majority baseline. Guarded research estimates are enabled. The full search procedure scored 25.5% under nested report validation; this is distinct from evaluating the fixed SVM and does not establish a validated improvement. The detailed analysis and its caveats are in [REBUILT_MODEL_EVALUATION.md](../reports/REBUILT_MODEL_EVALUATION.md).

## Run accuracy experiments

```bash
.venv/bin/python -m src.compute.experiments --jobs 6
```

This evaluates the frozen 135-configuration grid with nested leave-one-report-out selection,
plus an exact-condition overlap sensitivity check. It writes scores, outer predictions and
the report under `reports/accuracy_experiments/`, and separate research candidate models and
metadata inside an immutable run bundle. `reports/accuracy_experiments/latest.json` points to the last completed run. Failed runs leave earlier bundles untouched. The initial `models/accuracy_candidate_*` files are historical research artifacts; experiments do not replace production artifacts.
The four-input and seven-input experiments are reported separately; the latter also requires
sample thickness, geometry and flow direction. Read the [experiment protocol](../reports/accuracy_experiments/PROTOCOL.md)
and [results](../reports/accuracy_experiments/SUMMARY.md) before interpreting the selection scores.

## Run the existing checks

```bash
.venv/bin/pytest -q
node --check app/app.js
```

The suite verifies that model metadata matches the evaluated report-grouped metrics and that the API withholds predictions while the readiness gate is unmet. It does not treat model quality failure as an expected test failure.

## Start the local service

```bash
./scripts/run_local.sh
```

The UI is served at <http://localhost:8000>; OpenAPI docs are at <http://localhost:8000/docs>.

## Frontend connection and browser checks

FastAPI serves the workbench at `/` and `/app/`, the overview at `/project-page/`, and the API on the same origin. Any local FastAPI port works. VS Code Live Server at `http://127.0.0.1:5500/app/` automatically connects to the API at `http://127.0.0.1:8000`; start it with `./scripts/run_local.sh`. GitHub Pages hosts static files only; set `window.FLARE_API_BASE` to a reachable API origin before loading `app.js` to enable live results there. Opening the static app without a backend shows explicit unavailable states and the separately scoped NASA PMMA reference where applicable.

The Playwright integration suite is `tests/frontend.playwright.cjs`. Install its pinned dependencies with `npm ci`, install Chromium with `npx playwright install chromium`, then run `npm run test:frontend`. It starts a temporary API on port 8010. To check the Live Server page against an already running API, use:

```bash
FLARE_TEST_URL=http://127.0.0.1:8000 FLARE_FRONTEND_URL=http://127.0.0.1:5500/app/ npm run test:frontend
```

It saves desktop and mobile screenshots and a JSON report under `/tmp/flare-playwright/`. CI runs the same browser checks and uploads the evidence.
