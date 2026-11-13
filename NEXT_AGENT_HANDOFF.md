# FLARE-X handoff for the next agent

**Snapshot:** 2026-11-13, `/home/naiminator/Codebase/ALPINE_IBEX`, branch `master`.
Start with `git status --short` and `git log -1 --oneline` before editing. The
user explicitly asked to keep the earlier NASA datasets.

## User objective and current outcome

The user wants NASA combustion datasets properly fetched into this codebase,
source citations and documentation corrected, application tests run, issues
fixed, and model accuracy improved. The data and artifacts were rebuilt and a
source transcription error was fixed. The current report-held-out gradient
boosting accuracy is **77.5%**, up from **76.0%**, but still below the **81.5%**
majority-class baseline. Public inference must remain withheld. Do not describe
this as a validated high-accuracy model or relax the readiness gate to make the
app show predictions.

## Dataset and provenance

- Canonical model input: [`cache/experiments.parquet`](cache/experiments.parquet),
  200 source-verified microgravity rows: 158 BASS-II, 21 Saffire, 21 other NASA
  report rows. Outcomes: 163 `spread`, 35 `no_spread`, 2 `marginal_spread`.
  The rows come from seven NTRS report groups. The separate NASA 1-g tables and
  other existing datasets remain in `data/processed/`; they must not be silently
  pooled into this microgravity target or removed.
- BASS-II conditions are joined to NASA
  [PSI-25](https://psi.nasa.gov/physci/repo/data/investigations/PSI-25)
  (DOI `10.60555/4qc4-de67`) by `Test #`. Its 158 retained rows match the
  calibrated **initial** oxygen entries. Outcome labels come from the
  [BASS-II NTRS report](https://ntrs.nasa.gov/citations/20210011385) and the
  [labeling protocol](docs/LABELING_PROTOCOL.md), not from a PSI outcome column.
  The PSI-26 BASS table records test identities but lacks outcome labels.
- NASA PSI-98, PSI-99, and PSI-100 experimental CSVs were newly downloaded to
  [`data/external/psi/`](data/external/psi/), recorded in
  [`data/metadata/source_manifest.csv`](data/metadata/source_manifest.csv), and
  byte-compared against NASA's live download endpoints on 2026-11-13. File names,
  DOIs, byte counts, SHA-256 hashes, URLs, and source discrepancies are in the
  [PSI source README](data/external/psi/README.md). These tables verify existing
  Saffire records but add **no independent labeled experiments**.
- In [`experiments_saffire_verified.csv`](data/processed/experiments_saffire_verified.csv),
  Saffire-II sample `SAF_II_8` now uses initial O2 **22.1%** (previously final
  22.0%) and `SAF_II_9` uses initial **22.0%** (previously final 21.9%). Both
  [PSI-99](https://psi.nasa.gov/physci/repo/data/investigations/PSI-99)
  and [NTRS 20170008805 Table I](https://ntrs.nasa.gov/citations/20170008805)
  give the start-to-end ranges. The canonical and provenance exports were
  regenerated. The API provenance records cite the exact NTRS table/sample and
  PSI-99 cross-check.
- NASA sources conflict on Saffire-II sample 2-1 oxygen and sample 2-6 flow.
  The curated rows retain NTRS values (approximately 22.1% and 25 cm/s);
  PSI-99 lists approximately 21.5% and 20 cm/s. Do not overwrite either value
  without a source reconciliation. PSI-98 and PSI-100 also have ambiguous
  headers/units. See the [PSI source README](data/external/psi/README.md).
- The user's broader NASA combustion, ISS, Apollo, Mir, and firefighter
  technology links are cited in
  [`project-page/DATA_SOURCES.md`](project-page/DATA_SOURCES.md) as context.
  They do not supply training labels or validate predictions. Row-level NASA
  evidence is documented in [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).

## Model and application state

The training entry point is [`src/compute/model.py`](src/compute/model.py).
It evaluates majority, logistic regression, random forest, and gradient boosting
with `LeaveOneGroupOut(group=report_id)` as the headline split, a separate
investigation holdout, and an explicitly optimistic 2-fold stratified split.
There are seven uneven report groups with sizes 158, 13, 12, 7, 6, 3, and 1;
the pooled score is dominated by BASS-II. Current report-held-out results from
[`models/metrics.json`](models/metrics.json):

| Model | Accuracy | Balanced accuracy | Macro F1 |
|---|---:|---:|---:|
| Majority baseline | 0.8150 | 0.3333 | 0.2994 |
| Logistic regression | 0.6600 | 0.4120 | 0.3780 |
| Random forest | 0.8000 | 0.3870 | 0.3933 |
| Gradient boosting (saved model) | 0.7750 | 0.3618 | 0.3637 |

The saved gradient booster recalls **6/35** `no_spread` rows and **0/2**
`marginal_spread` rows under report holdout. Its 10-seed holdout means are
0.7755 accuracy and 0.3733 balanced accuracy. The 0.8500 plain stratified
accuracy is optimistic and must not be presented as cross-report performance.
The current dataset SHA-256 is
`26c383559b63ddee3cd5e1260fe15924d8438af89b8a8b74e5cf87d353af28e0`;
the saved model SHA-256 is
`b19a775e2f4af1f76ecf2ed789fa3c95b33d0ab42dae48bd008d201665e06d8a`.
Recheck hashes after any rebuild.

The API checks dataset/model hashes and the majority baseline before inference.
The shared model loader verifies the artifact hash against metadata before
deserializing it; all three model-loading paths use that loader.
At this snapshot, `GET /health` returns `degraded` and `model_ready: false`;
`GET /model` reports the metrics; `POST /predict` for an otherwise eligible
condition returns `model_unvalidated` with null prediction and probabilities.
Other envelope, conflict, and sparse-evidence abstentions remain active.
See [`src/api/main.py`](src/api/main.py),
[`scripts/verify_artifacts.py`](scripts/verify_artifacts.py),
[`docs/API_CONTRACT.md`](docs/API_CONTRACT.md), and the current
[evaluation addendum](reports/REBUILT_MODEL_EVALUATION.md#addendum-11-saffire-psi-retrieval-source-correction-and-current-evaluation).

Exploratory threshold changes, class-weighted models, extra geometry/direction
features, and a BASS-II-only test did not establish a safe or robust accuracy
gain. The [evaluation report](reports/REBUILT_MODEL_EVALUATION.md) separates
historical experiments from Addendum 11's current results. A published PMMA-rod
boundary is a citable reference within its stated scope, not a validated
classifier prediction.

## Last verification and reproduction

The following checks were last run after the source correction on 2026-11-13:

- `.venv/bin/python -m src.ingestion.build_table`: 200/200 valid, zero quarantined.
- `.venv/bin/python src/compute/model.py`: model and generated reports rebuilt.
- `.venv/bin/pytest -q`: **162 passed**. One test expectation was updated to
  reflect the corrected exact-condition conflict (`SAF_II_9`, not `SAF_II_8`),
  and a test verifies that an untrusted model hash is rejected before loading.
- `.venv/bin/python scripts/verify_artifacts.py`: dataset/model metadata and
  metrics matched; dataset hash above.
- `node --check app/app.js` and
  `git -c core.whitespace=cr-at-eol diff --check`: passed.
- NASA PSI-98/99/100 local CSV bytes matched live NASA responses. FastAPI
  TestClient smoke checks confirmed `/health`, `/model`, `/predict`, and
  `/api/provenance/SAF_II_8` and `SAF_II_9` behavior. The route is `/model`,
  not `/model/info`.

To reproduce after making a source change, run in this order:

```bash
.venv/bin/python -m src.ingestion.build_table
.venv/bin/python src/compute/model.py
.venv/bin/python scripts/verify_artifacts.py
.venv/bin/pytest -q
node --check app/app.js
git -c core.whitespace=cr-at-eol diff --check
```

The ingestion command reads curated local source tables; it does not fetch
missing NASA files. Training overwrites the saved model, metadata, metrics,
baseline report, and model card. Use the repository's pinned `.venv` or install
[`requirements.txt`](requirements.txt) before running tests. Local app launcher:
`./scripts/run_local.sh`.

## Next work

1. Inspect the branch and current diff before editing or committing. Preserve
   all existing NASA source files and user work.
2. Pursue **new, independently verifiable `no_spread` and marginal outcomes**,
   with exact test condition, initial oxygen, flow units, geometry, ignition
   history, and NASA citation. The BASS-II
   [`bass2_labelling_worksheet.csv`](data/processed/bass2_labelling_worksheet.csv)
   contains unresolved candidates; most cannot be assigned automatically from
   the narrative. Keep uncertain labels blank and follow the labeling protocol.
3. Evaluate any new model with whole tests/reports held out, compare against
   the majority baseline and minority-class precision/recall, and report the
   number of independent groups. Do not optimize on a held-out report and then
   call its score an unbiased validation result. Keep the API gate until a
   defensible model and safety-relevant error profile are demonstrated.
4. Update all generated artifacts and current-status docs together after a
   dataset or model change. Historical figures in earlier evaluation addenda
   describe prior snapshots; Addendum 11 and `models/metrics.json` describe
   this one.
