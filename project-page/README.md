# FLARE-X Project Page

A deployable, zero-dependency static page for the FLARE-X research prototype.

The landing page uses inline CSS and SVG and does not run a prediction script. Its
"Open the tool" link points to the separate Mission Control application. The
published PMMA boundary is a cited NASA fit, not the trained classifier.

## Deploy

### GitHub Pages
The repository workflow `.github/workflows/deploy-pages.yml` packages the root
redirect, `project-page/`, and `app/` together. It requires a deployed public HTTPS
FastAPI URL in the repository variable `FLARE_API_BASE`, and verifies the evidence
workflow in a fresh browser before and after publication. See the
[deployment and recording guide](../docs/DEPLOYMENT.md).

### Other hosts
Publish the same three paths together at the site root. Set the API URL in
`app/config.js`, or serve the whole repository through FastAPI on one origin.
Deploying only `project-page/` breaks its `../app/` tool link. A static page alone
cannot demonstrate live retrieval, coverage or citation inspection.

## Files

- `index.html` — page content, inline styles and cited SVG figure
- `DATA_SOURCES.md` — NASA dataset/source notes
- `LIMITATIONS.md` — scientific boundaries and red lines
- `CREDITS.md` — team and NASA attribution checklist

## Important

The evidence workflow is the pitch: similarity ranking, explicit condition differences,
original citations, dataset coverage and team proposals. Summaries use deterministic
templates. The optional model has no independent validation; its evaluation and limitations
are in the [model card](../docs/MODEL_CARDS.md). The published PMMA reference has its own
restricted scope. Neither provides operational safety clearance.
