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
| `GET` | `/api/coverage-map` | Empirical coverage and knowledge gaps |
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

- `model_unvalidated`: current grouped model score (0.760) does not exceed the 0.815 majority baseline. Prediction and probabilities are null.
- `conflicting_evidence`: opposite outcomes are present at identical model inputs. Prediction and probabilities are null; conflicting observations are returned.
- `insufficient_material_evidence`: fewer than three distinct conditions exist for that material. Prediction and probabilities are null.
- `joint_extrapolation` or an out-of-range refusal: a feature or input combination is outside observed conditions. Prediction and probabilities are null.
- `audit_failed`: the final explanation failed evidence checks. The result and probabilities are withheld.

When status is eligible for a model estimate, the response includes `inputs`, `in_training_range`, `out_of_range_reasons`, `prediction`, `probabilities`, `model`, `nearest_experiments`, and `explanation`. Any abstention keeps the nearest historical observations available when the retrieval service can provide them.

## Scenario parsing

`POST /scenario/parse` accepts `{"query":"..."}` with at most 2,000 characters. Conflicting mentions of a material or numeric condition are reported as ambiguities rather than silently selecting one mention.
