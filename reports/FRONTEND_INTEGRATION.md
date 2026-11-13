# Frontend and backend verification — 2026-11-13

The live VS Code preview at **http://127.0.0.1:5500/app/** connects to the FastAPI model backend at **http://127.0.0.1:8000**. The backend is running locally. Start it again with `./scripts/run_local.sh` when needed. The FastAPI-hosted frontend uses its own origin, including other ports; that mode was independently checked on port 8010.

## Serving model and evidence

The production artifact now contains the selected linear SVM (C=1.0), using the existing four inputs. Training, API metadata, artifact verification, explanation text, and frontend labels agree on `linear_svm` and `release_mode=research`.

The **84.0% grouped score is exploratory model-selection evidence**. The **81.5% majority baseline**, **40.3% balanced accuracy**, three-class confusion matrix, and **25.5% full-search nested accuracy** are exposed separately. The nested score evaluates the search procedure, not the fixed SVM alone. Probabilities have not been validated across reports. A no-spread estimate does not establish safety.

The canonical 200-row dataset and all outcome labels are unchanged. The guards for joint experimental coverage, contradictory observations, insufficient material evidence, artifact integrity and failed explanation audits remain active.

## Fixes verified in the live browser

- Live Server on port 5500 reaches port 8000; API documentation and model metadata links use that same backend.
- FastAPI serves the overview and workbench links at `/project-page/` and `/app/`.
- All eight material choices, all presets, oxygen/pressure/flow controls, scenario search and out-of-range exploration agree with submitted API conditions.
- Source conditions such as 14% oxygen and 0.81 cm/s are preserved by archive probing and controls.
- Chart probing translates between displayed and canvas coordinates correctly; single-condition materials have finite chart axes and no fabricated prediction grid.
- Old probability animations are canceled before a new request or abstention. Connection failures clear probabilities and report an unavailable live estimate; a successful retry restores live status.
- Hidden sweep panels no longer issue background sweep requests. Sweep animations stop when leaving the panel. API rate limits remain enabled.
- Citation inspection includes source observation text, geometry, thickness, flow direction and environment, with Escape, focus trapping, focus restoration and stale-request protection.
- Failed citation lookups clear the previous record's verification and origin badges.
- Delayed scenario-search responses cannot replace a newer search or manually selected conditions. Pending metadata responses cannot hide a failed live prediction connection.
- The boundary endpoint rejects non-finite pressure and values outside the public 0–200 kPa request bounds with HTTP 422. Counterfactual disclaimers and current architecture/availability documentation identify the research model correctly.
- Archive filters, empty states and keyboard probing work. All catalog entries are shown; catalog inclusion is distinguished from training data.
- Conflict presets and custom comparisons use the API. Comparability is labeled as a heuristic; missing coverage is labeled as an untested region.
- Model provenance shows seven report folds and distinguishes the selected score from the full search procedure's nested evaluation.
- Model sweeps retain points when no transition exists, show N/A for transition distance, and make no safety-clearance claim.
- All six views were checked at 1920, 1440, 768, 390 and 320 pixels. The page has no horizontal overflow; wide tables and the sweep plot retain local scrolling. A 320-pixel header overlap was fixed and all 30 viewport/view combinations were checked again.
- Offline views report unavailable data and show the separately scoped published PMMA reference where applicable, without invented model probabilities.

## Verification results

| Check | Result |
|---|---|
| Full Python regression suite | 181 passed |
| Playwright, actual 5500 frontend + 8000 backend | 17 workflow checks passed |
| Playwright, FastAPI same-origin frontend on 8010 | 17 workflow checks passed |
| Final layout checks after the narrow-header fix | 30 view/width combinations passed |
| Browser JavaScript exceptions / server errors during successful workflow runs | None captured |
| Canonical dataset and serving artifact hashes / metadata | Verified |
| Python compilation, JavaScript syntax, Git whitespace checks | Passed |

Browser evidence is saved locally under `/tmp/flare-playwright-5500/` and `/tmp/flare-playwright-same-origin/`, including result JSON and viewport screenshots. Each latest full browser run includes all 30 view/width checks; `responsive-final.json` also records the earlier focused header/overflow check. The repository includes the scripts and pinned Playwright dependency; CI is configured to run the same workflow and upload browser evidence. Remote CI has not been executed in this session.

The scenario-search, metadata-status and boundary-pressure regressions were reproduced with failing tests before applying their fixes. The complete Python and live-browser suites passed after the fixes.

Run the live-page checks with:

```bash
npm ci
npx playwright install chromium
FLARE_TEST_URL=http://127.0.0.1:8000 FLARE_FRONTEND_URL=http://127.0.0.1:5500/app/ npm run test:frontend
```

`npm run test:frontend` without those variables starts a temporary same-origin backend on port 8010. Verification covers Chromium and local services; other browser engines, remote hosting and independent external model validation were not checked.
