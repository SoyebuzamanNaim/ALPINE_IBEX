# Requirement Traceability Matrix

Status values are updated as phases complete. `CR` = challenge requirement, `DD` = adopted design
decision (guidance, not NASA-required).

| Req | Implemented in | Verified by | Status |
|---|---|---|---|
| CR-1 AI on microgravity combustion research | `src/compute/model.py`, `src/retrieval/` | `tests/test_models.py`, `tests/test_retrieval.py` | see STATE.json |
| CR-2 Spacecraft fire-safety insight | `app/` operator framing, `src/agents/explain.py` | `reports/UI_QA.md` | see STATE.json |
| CR-3 Microgravity-specific behaviour | data restricted to µg tests (`gravity_env`) | `tests/test_ingestion.py` | see STATE.json |
| DD-1 Explorer inputs | `src/api/main.py` `PredictRequest` | `tests/test_api.py` | see STATE.json |
| DD-2 Regime target | `docs/LABELING_PROTOCOL.md`, `src/ingestion/build_table.py` | `tests/test_ingestion.py` | see STATE.json |
| DD-3 Citations | `src/retrieval/nearest.py`, corpus | `tests/test_retrieval.py` | see STATE.json |
| DD-4 Oxygen-sweep demo | `src/features/counterfactual.py` | `tests/test_counterfactual.py`, `docs/DEMO_SCENARIOS.md` | see STATE.json |
| DD-5 Committed, browsable table | `cache/experiments.parquet`, `GET /experiments`, Data page | `tests/test_api.py` | see STATE.json |
| DD-6 Honest CV | `src/compute/model.py` | `tests/test_models.py`, `reports/BASELINE_RESULTS.md` | see STATE.json |
| DD-7 Range guard | `src/envelope/guard.py` | `tests/test_envelope.py`, `tests/test_api.py` | see STATE.json |
| DD-8 Resolvable report IDs | `src/ingestion/ntrs_fetch.py`, `scripts/verify_sources.py` | `tests/test_ingestion.py` | see STATE.json |
| DD-9 GB + baselines | `src/compute/model.py` | `reports/BASELINE_RESULTS.md` | see STATE.json |
| DD-10 Artifact + meta | `models/` | `tests/test_models.py` | see STATE.json |
| DD-11 API endpoints | `src/api/main.py` | `tests/test_api.py` | see STATE.json |
| DD-12 Bounded explanation | `src/agents/explain.py` | `tests/test_agents.py` | see STATE.json |
| DD-13 Frontend | `app/` | `reports/UI_QA.md` | see STATE.json |
| DD-14 Required paths | `cache/`, `src/compute/` | `reports/FINAL_QA.md` | see STATE.json |
| DD-15 Licence / README | `LICENSE`, `README.md` | `reports/FINAL_QA.md` | see STATE.json |
