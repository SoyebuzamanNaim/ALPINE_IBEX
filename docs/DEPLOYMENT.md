# Public demo and recording

The GitHub Pages entry point is <https://soyebuzamannaim.github.io/ALPINE_IBEX/>.
Pages serves static files and cannot run FastAPI. A successful Pages upload alone does not
verify evidence retrieval, scenario parsing, coverage or citation inspection.

## Serve the complete application

Deploy this checkout on a Python 3.12+ host with a public HTTPS URL. Use the repository root
as the working directory, install `requirements.txt`, retain the checked-in `cache/`,
`data/metadata/`, `models/`, `app/` and `project-page/` files, and start:

```bash
python -m pip install -r requirements.txt
python scripts/verify_artifacts.py
python -m uvicorn src.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
```

The host must terminate HTTPS and keep the API reachable for the recording and judging
period. The application serves the workbench at `/` and `/app/`, the overview at
`/project-page/`, and the API on the same origin. This is also a complete submission option
without Pages. The process-local request limiter requires a shared trusted edge limiter if
the deployment runs multiple workers; see the [API contract](API_CONTRACT.md).

## Connect the GitHub Pages demo

1. Deploy and verify the backend first, including `/health`, `/evidence`, report search and provenance.
2. In the repository's **Settings → Secrets and variables → Actions → Variables**, set
   **`FLARE_API_BASE`** to that public HTTPS backend URL. This value is public configuration,
   never an API key. Backend CORS must permit the Pages origin and the local preflight origin.
3. Run **Deploy GitHub Pages**. The workflow refuses an empty or nonpublic API setting,
   writes the URL into `_site/app/config.js`, and checks the assembled page against the real
   deployed API before upload. After publication it checks the exact Pages URL in another
   fresh browser. It uploads screenshots and `report.json` as `public-demo-verification`.
4. Treat a failed post-publication check as a failed demo deployment. Do not record or submit
   it until the check passes; the static upload may already have completed.

## Container option

The supplied image serves the workbench and API on one origin, runs as a non-root user,
uses the checked-in data and model, honors `PORT`, and checks `/health`.

```bash
docker build -t flare-x .
docker run --rm -p 8000:8000 flare-x
```

Open `http://localhost:8000/` locally, or deploy the image on an HTTPS-capable container host.
The container definition still needs a real build/run on a Docker-enabled host; it was not
validated against a running Docker daemon in this workspace. The Python runtime and browser
checks validate the same application separately.

For another static host, copy `index.html`, `project-page/`, and `app/` together and set
`window.FLARE_API_BASE` in `app/config.js` to the deployed API URL. Keep `config.js` before
`app.js`. A same-origin FastAPI deployment uses the checked-in empty setting.

## Verify the exact submission URL before filming

```bash
npm ci
npx playwright install chromium
FLARE_DEMO_URL=https://soyebuzamannaim.github.io/ALPINE_IBEX/ npm run test:demo
```

For a same-origin host, substitute its exact submission URL. `test:demo` opens fresh desktop
and mobile contexts, follows the overview's tool link when present, submits a real scenario,
checks similarity explanations and their citations, opens source provenance, and checks
dataset-scoped coverage and team proposals. Missing APIs, CORS failures and old/incomplete
response shapes fail the check. Evidence is saved under `/tmp/flare-demo/` by default;
`FLARE_DEMO_OUTPUT` changes that path. The broader local regression suite remains
`npm run test:frontend`.

## Recording narrative

Demonstrate **scenario → similar observations → condition differences → original citation →
dataset coverage → team-proposed next experiment**. State that summaries use deterministic
templates. Explain what was observed, which context is missing, and what cannot be concluded.
Keep model selection accuracy out of the pitch; the model card and Model Provenance tab
retain the full evaluation and its limitations. Neither estimates nor similarity ranking
establish operational safety.
