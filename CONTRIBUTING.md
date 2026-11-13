# Contributing

Use Python 3.12 or newer and the locked `requirements.txt`. Keep changes focused and retain
original NASA source files and historical evaluation evidence.

```bash
.venv/bin/python scripts/verify_artifacts.py
.venv/bin/pytest -q
node --check app/app.js
npm run test:frontend
git diff --check
```

Install the browser dependencies with `npm ci` and `npx playwright install chromium` first.
For an exact deployed URL, use `FLARE_DEMO_URL=https://your-submission-url/ npm run test:demo`.

The runtime observation source is `cache/experiments.parquet`. Its source references,
quoted observations and missing values are evidence, not values to fill by guessing. See
the [labeling protocol](docs/LABELING_PROTOCOL.md) before changing outcomes. Accepted data
changes require ingestion, retraining, regenerated evaluation, artifact verification and
regression checks. Keep all model evaluation results, including weak minority performance.

The public workflow does not release generative summaries. Numerical similarity, lexical
relevance, recorded agreement, model probability and scientific reliability are distinct.
Preserve these distinctions in UI copy, responses and documentation.

The Python package retains historical module names for compatibility. `FlameSpreadPredictor`,
the model router, counterfactuals and the API share the research-release checks; do not add
a new inference path that bypasses integrity, joint-domain, conflict or sparse-evidence guards.
