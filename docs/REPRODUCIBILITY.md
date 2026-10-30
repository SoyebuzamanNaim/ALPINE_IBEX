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

This rebuilds `cache/experiments.parquet`, `data/processed/experiments.parquet`, CSV/interim exports, the provenance registry, and `reports/DATA_QUALITY.md`. The checked-in canonical table currently contains 200 rows. Compare its SHA-256 with `models/model_meta.json` before using the model; the API performs this check at request time.

## Train and evaluate

```bash
.venv/bin/python src/compute/model.py
```

This writes `models/flame_spread_gb.joblib`, `models/model_meta.json`, `models/metrics.json`, `reports/BASELINE_RESULTS.md`, and `docs/MODEL_CARDS.md`. Training is a mutating operation: it replaces these artifacts with results from the current dataset and code. Review the generated diffs before committing them.

Current checked-in metadata reports 76.0% grouped accuracy and an 81.5% majority-class baseline. Since the model does not beat that baseline, public model inference remains withheld. The detailed analysis and its caveats are in [REBUILT_MODEL_EVALUATION.md](../reports/REBUILT_MODEL_EVALUATION.md).

## Run the existing checks

```bash
.venv/bin/pytest -q
node --check app/app.js
```

The suite includes a strict expected failure for the current model-governance requirement that the classifier beat its majority baseline.

## Start the local service

```bash
./scripts/run_local.sh
```

The UI is served at <http://localhost:8000>; OpenAPI docs are at <http://localhost:8000/docs>.
