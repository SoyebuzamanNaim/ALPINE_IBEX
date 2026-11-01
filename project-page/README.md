# FLARE-X Project Page

A deployable, zero-dependency static page for the FLARE-X research prototype.

The landing page uses inline CSS and SVG and does not run a prediction script. Its
"Open the tool" link points to the separate Mission Control application. The
published PMMA boundary is a cited NASA fit, not the trained classifier.

## Deploy

### GitHub Pages
The repository workflow `.github/workflows/deploy-pages.yml` packages the root
redirect, `project-page/`, and `app/` together. Use that workflow for the
published site.

### Other static hosts
Publish the same three paths together at the site root. Deploying only
`project-page/` breaks its `../app/` tool link.

## Files

- `index.html` — page content, inline styles and cited SVG figure
- `DATA_SOURCES.md` — NASA dataset/source notes
- `LIMITATIONS.md` — scientific boundaries and red lines
- `CREDITS.md` — team and NASA attribution checklist

## Important

The current classifier fails to exceed the majority baseline in report-grouped
validation. Public model inference is withheld until a validated replacement is available.
