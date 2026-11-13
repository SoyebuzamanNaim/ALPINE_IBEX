# FLARE-X

FLARE-X is a research prototype for exploring NASA microgravity combustion observations. It provides a FastAPI service and a browser interface for evidence lookup, experimental-domain checks, comparisons, and model exploration. It is not a fire-safety certification or operational decision system.

Prepared for the [Space Apps 2026 Flame in Freefall challenge](https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/?tab=details).
Start with the [submission narrative and demo script](docs/SUBMISSION.md) for the challenge-to-feature map, NASA data use, and items the team still needs to complete.

## Evidence workflow

Enter a scenario, inspect similar indexed observations and their condition differences, trace
citations to the original reports, and examine coverage of the current FLARE-X dataset.
Similarity ranking describes proximity, not scientific reliability. Explanations use deterministic
templates; follow-up experiments are team proposals, not verified literature gaps.

The evidence desk opens with a source observation and its limits. Search indexed report
abstracts, compare recorded study conditions, and download a cited scenario bundle. The
research model is optional: `/evidence`, report search and provenance remain available if
the classifier cannot load. No generative summaries or inferred physical causes are released.

The optional classifier supplies exploratory research estimates without independent validation.
Probabilities are not validated across reports. Out-of-domain, conflicting, sparse-material and
failed-audit cases abstain. Evaluation figures and limitations belong in the
[model card](docs/MODEL_CARDS.md), not a safety-performance pitch.

## Run locally

Run the commands below from the repository root in Bash or Zsh. Requires Python 3.12 or newer;
the browser checks also require Node.js 22 or newer and npm.
`requirements.txt` pins the runtime, test, and transitive Python packages used by CI.

Create the environment once for a new checkout:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/verify_artifacts.py
```

**Terminal 1 — backend and built-in frontend:**

```bash
./scripts/run_local.sh
```

Keep this terminal running. Open <http://127.0.0.1:8000/> for the workbench or
<http://127.0.0.1:8000/docs> for interactive API documentation. FastAPI serves the frontend
and API together, so this is sufficient to use the complete application.

**Terminal 2 — separate static frontend (optional):**

```bash
.venv/bin/python -m http.server 5501 --bind 127.0.0.1
```

Keep both terminals running and open <http://127.0.0.1:5501/app/>. This frontend sends API
requests to <http://127.0.0.1:8000>. VS Code Live Server at
<http://127.0.0.1:5500/app/> uses the same connection. The checked-in `app/config.js` uses
these local defaults; public hosting needs an explicit backend URL as described below.
Port 5501 avoids conflicting with Live Server on 5500. If a port is occupied, stop your
previous instance before starting another server on that port.

**Terminal 3 — verify the live API:**

```bash
curl --fail http://127.0.0.1:8000/health
curl --fail http://127.0.0.1:8000/evidence \
  -H 'Content-Type: application/json' \
  --data '{"material":"PMMA","oxygen_pct":19,"pressure_kpa":101.3,"flow_cm_s":5}'
```

Health should report `evidence_ready: true` and `dataset_rows: 200` for the checked-in data.
The evidence response includes ranked observations, condition differences, source citations
and the dataset hash. The launcher uses the checked-in dataset and model artifacts; it
rebuilds or trains them only if they are missing. Press `Ctrl+C` in each server terminal to stop it.

Try `PMMA at 19% oxygen, 101.3 kPa, 5 cm/s`, then search reports for `PMMA extinction`.
The container option and public hosting requirements are in the [deployment guide](docs/DEPLOYMENT.md).

## Reproduce the checks

Install the browser dependencies once, then run the Python, artifact and browser checks:

```bash
npm ci
npx playwright install chromium
.venv/bin/pytest -q
.venv/bin/python scripts/verify_artifacts.py
npm run test:frontend
```

`test:frontend` starts and stops its own API on port 8010. To verify the two servers above
instead, leave them running and use:

```bash
FLARE_TEST_URL=http://127.0.0.1:8000 \
FLARE_FRONTEND_URL=http://127.0.0.1:5501/app/ \
FLARE_TEST_OUTPUT=/tmp/flare-connectivity \
npm run test:frontend
```

This checks real frontend-to-backend requests, scenario parsing, evidence retrieval, citations,
coverage, all six views, responsive layouts and connection failure/recovery. Screenshots and
`results.json` are saved in `/tmp/flare-connectivity/`. To test Live Server, change only
`FLARE_FRONTEND_URL` to `http://127.0.0.1:5500/app/`.
Run browser checks sequentially against a shared backend; concurrent runs can exceed its
60 heavy requests per minute limit. If it returns HTTP 429, wait one minute before retrying.

The shorter fresh-browser acceptance check also runs against an exact URL:

```bash
FLARE_DEMO_URL=http://127.0.0.1:5501/app/ \
FLARE_API_BASE=http://127.0.0.1:8000 \
FLARE_DEMO_OUTPUT=/tmp/flare-connectivity-demo \
npm run test:demo
```

It writes `report.json` and desktop/mobile screenshots to `/tmp/flare-connectivity-demo/`.
Substitute the exact public URL for the final submission check after deploying a backend.

GitHub Actions runs the same suite on Python 3.12 and 3.14, checks JavaScript syntax, and verifies the checked-in model artifacts against the dataset hash and evaluation metrics.

For the public demo, follow the [deployment and recording guide](docs/DEPLOYMENT.md). Pages requires a reachable FastAPI backend; the deployment workflow checks the exact submission URL with `npm run test:demo`.

## What is included

- Curated observation data and source provenance in `data/`, `cache/`, and `reports/`.
- Input-domain checks and abstention rules in `src/envelope/`.
- Model training and validation in `src/compute/model.py`.
- Evidence retrieval and explanation auditing in `src/retrieval/` and `src/agents/`.
- Counterfactual and coverage analysis in `src/features/` and `src/analysis/`.
- FastAPI routes and request guards in `src/api/`.
- The browser application in `app/`.

## Rebuild data and model artifacts

The ingestion pipeline reads the curated source tables in `data/processed/`, records validation counts in `data/interim/ingestion_audit.json`, and writes the canonical tables and provenance report. If any row fails schema validation, it saves the row and errors to `data/interim/quarantine.json` and stops before overwriting canonical tables.

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

See [contributing](CONTRIBUTING.md) before changing data or model behavior. Older model-work notes
are preserved as a [historical snapshot](docs/history/2026-11-13-model-handoff.md); they do not describe the current serving model.
