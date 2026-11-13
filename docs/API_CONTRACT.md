# API contract

The FastAPI service is served locally at `http://localhost:8000`. The interactive OpenAPI specification is available at `/docs`.

## Request guards

- JSON request bodies are limited to 65,536 bytes; larger requests receive HTTP 413.
- Requests are rate limited by socket client address: 60 requests/minute for inference, sweeps, boundaries, scenario parsing, and study comparisons; 600 requests/minute for other routes. A limit response is HTTP 429 with `Retry-After: 60`.
- The limiter is process-local. A multi-worker deployment should enforce a shared limit at a trusted proxy or gateway.
- Prediction material names are limited to 64 characters. Scenario parse text is limited to 2,000 characters. Catalog filters and study/experiment identifiers also have bounded lengths.
- Pydantic validation failures return HTTP 422.

## Routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/health` | Service and model readiness |
| `POST` | `/predict` | Guarded estimate, refusal, or abstention with evidence |
| `POST` | `/evidence` | Model-independent similarity ranking, source context and cited summaries |
| `GET` | `/reports/search` | BM25 lexical search over indexed report metadata and abstracts |
| `GET` | `/experiments` | Paginated curated observations |
| `GET` | `/model` | Model metadata and evaluation metrics |
| `GET` | `/boundary` | Guarded 2-D oxygen/flow slice |
| `POST` | `/counterfactual` | Compare baseline and modified conditions |
| `POST` | `/sweep` | Guarded one-dimensional parameter sweep |
| `POST` | `/scenario/parse` | Parse a free-text scenario and report ambiguities |
| `GET` | `/datasets` | Investigation catalog |
| `GET` | `/sources/{report_id}` | Report metadata and abstract |
| `GET` | `/api/conflict/cases` | Canonical comparison cases |
| `GET` | `/api/conflict/profiles` | Available study profiles |
| `POST` | `/api/conflict/compare-studies` | Compare two study profiles |
| `POST` | `/api/conflict/compare-experiments` | Compare two observations |
| `GET` | `/api/coverage-map` | Current dataset coverage and team proposals |
| `GET` | `/api/provenance` | Filter provenance records |
| `GET` | `/api/provenance/{experiment_id}` | Provenance record for one observation |

## Prediction request

```json
{
  "oxygen_pct": 19.0,
  "pressure_kpa": 101.3,
  "flow_cm_s": 5.0,
  "material": "PMMA"
}
```

The numeric fields must be nonnegative and within broad schema bounds: oxygen 0–100%, pressure 0–200 kPa, and flow 0–100 cm/s. The empirical guard applies stricter material-specific observed-domain checks.

## Prediction outcomes

`POST /predict` returns HTTP 200 for scientifically meaningful abstentions as well as accepted in-domain results. Clients must inspect `status`, `prediction`, and `probabilities`.

- `model_unvalidated`: the loaded model does not pass its dataset/artifact integrity checks or grouped baseline comparison. Prediction and probabilities are null.
- `conflicting_evidence`: opposite outcomes are present at identical model inputs. Prediction and probabilities are null; conflicting observations are returned.
- `insufficient_material_evidence`: fewer than three distinct conditions exist for that material. Prediction and probabilities are null.
- `joint_extrapolation` or an out-of-range refusal: a feature or input combination is outside observed conditions. Prediction and probabilities are null.
- `audit_failed`: the final explanation failed evidence checks. The result and probabilities are withheld.

When status is eligible for a model estimate, the response includes `inputs`, `in_training_range`, `out_of_range_reasons`, `prediction`, `probabilities`, `model`, `nearest_experiments`, and `explanation`. Any abstention keeps the nearest historical observations available when the retrieval service can provide them.

### Similarity ranking and interpretation

`nearest_experiments` are sorted by ascending normalized Euclidean distance over oxygen,
pressure and airflow, plus a material mismatch penalty (default 10). Each feature is divided
by its range in the indexed table; a constant feature uses a divisor of 1. Stable ties retain
dataset order. This is **similarity ranking**, not scientific reliability or evidence strength.

Each result includes `similarity_ranking` (formula, feature ranges, normalized differences,
numeric distance and applied material penalty), the recorded `sample_geometry`,
`sample_thickness_mm`, `flow_direction`, source observation and extraction notes, and an
`interpretation` object with `observed`, `conditions_differ`, `cannot_conclude`, and
`method=deterministic_record_template`. `matched_variables` means within the display
tolerances of 1 oxygen percentage point, 5 kPa and 2 cm/s, with matching material; these
tolerances do not change the distance calculation or imply exact experimental equivalence.

Boolean conditions and extra request fields are rejected. The four-input query does not specify geometry, thickness, direction or ignition protocol,
so agreement for these conditions is unknown. Ignition history is not a structured dataset
field and is not inferred; consult the original notes. The result cards expose this context
even when the model abstains. An interpreted outcome label remains marked as interpreted.

`explanation_source` identifies the deterministic template or refusal path. The public route
does not invoke a generative model. The internal candidate-text hook checks numbers and
citation identifiers for diagnostics, but always returns a deterministic template. Passing
those checks does not establish scientific entailment and does not enable candidate publication.

`POST /evidence` accepts the same four conditions but never runs a classifier. It returns the
scenario, nearest observations, cited report metadata, selected deterministic interpretation,
scope and actual indexed dataset hash. It remains available when optional model artifacts are
missing or invalid. In that situation `/health` reports `evidence_ready=true`,
`model_ready=false`; model-specific routes return HTTP 503.

`GET /reports/search?query=PMMA%20extinction&limit=5` ranks indexed report titles, abstracts and
keywords by BM25 lexical relevance. The query is limited to 500 characters and the result
limit is 1–20. A zero-result search is not a literature-wide absence claim.

### Recorded-condition comparisons

Study profiles summarize the current indexed rows for a study family, rather than guessed
chamber volumes or complete experimental specifications. Each dimension reports `MATCH`,
`DIFFERENT`, or `UNKNOWN`, with unknown used whenever either side lacks complete context.
Range agreement across studies does not establish matched tests or justify pooling.

Comparison responses expose `matching_dimensions`, `unknown_dimensions`, source reports,
and `comparison_method=deterministic_recorded_conditions`. The legacy `comparability_score`
field is always null. The view neither assigns scientific reliability nor infers physical
causes for differing outcomes. Original source review remains necessary.

### Dataset coverage

`/api/coverage-map` reports `scope=current FLARE-X dataset`. Grid occupancy aggregates
materials, pressures and geometries in oxygen–airflow bins; it does not establish coverage
of every scenario in an occupied bin. Empty cells have `density=NO_INDEXED_OBSERVATIONS`.
The legacy keys `coverage_completeness_pct` and `untested_gap_cells_count` mean occupied-bin
percentage and empty-bin count, respectively, not literature completeness or proven gaps.

The legacy `empirical_white_spaces` list now contains `status=team_proposal`, explicit
dataset scope, computed `matching_observations`, per-material counts, and a
`coverage_statement`. Zero matches are described as “No matching observations in the current
FLARE-X dataset.” A proposal with indexed matches reports that count instead. These ideas
are team proposals and make no independently verified literature-wide absence claim.

## Scenario parsing

`POST /scenario/parse` accepts `{"query":"..."}` with at most 2,000 characters. Conflicting mentions of a material or numeric condition are reported as ambiguities rather than silently selecting one mention.

The serving `linear_svm` runs in `release_mode=research`. The 0.84 grouped score is exploratory model-selection evidence. `/model`, `/health`, and prediction metadata expose the full search procedure's nested score separately (0.255), validation status, and calibration limitations. Research availability is not operational certification.
