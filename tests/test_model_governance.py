"""The public API must abstain when its model fails the baseline gate."""

import math

from fastapi.testclient import TestClient

from src.api import main
from src.api.main import app


client = TestClient(app)
BASELINE = {"oxygen_pct": 21.0, "pressure_kpa": 101.3, "flow_cm_s": 5.0, "material": "PMMA"}


def test_below_baseline_model_is_not_operational():
    meta = client.get("/model").json()
    assert meta["cv_accuracy"] < meta["majority_baseline_accuracy"]

    health = client.get("/health").json()
    assert health["status"] == "degraded"
    assert health["model_ready"] is False

    response = client.post("/predict", json=BASELINE)
    assert response.status_code == 200
    result = response.json()
    assert result["in_training_range"] is True
    assert result["status"] == "model_unvalidated"
    assert result["prediction"] is None
    assert result["probabilities"] is None
    assert len(result["nearest_experiments"]) == 3
    assert "majority" in result["explanation"].lower()


def test_model_dependant_public_routes_refuse_inference():
    counterfactual = client.post(
        "/counterfactual", json={"baseline": BASELINE, "changes": {"oxygen_pct": 18.0}}
    )
    sweep = client.post(
        "/sweep",
        json={"baseline": BASELINE, "param": "oxygen_pct", "start": 17.0, "end": 21.0},
    )
    boundary = client.get("/boundary", params={"material": "PMMA"})
    for response in (counterfactual, sweep, boundary):
        assert response.status_code == 503
        assert "majority" in response.json()["detail"].lower()


def test_invalid_validation_score_cannot_open_gate(monkeypatch):
    for invalid in (math.nan, math.inf, True, 1.5, -0.1):
        meta = dict(main.orchestrator.router.meta)
        meta["cv_accuracy"] = invalid
        monkeypatch.setattr(main.orchestrator.router, "meta", meta)
        ready, _ = main._model_readiness()
        assert ready is False


def test_dataset_hash_mismatch_cannot_open_gate(monkeypatch, tmp_path):
    meta = dict(main.orchestrator.router.meta)
    meta["cv_accuracy"] = 0.95
    monkeypatch.setattr(main.orchestrator.router, "meta", meta)
    changed_dataset = tmp_path / "experiments.parquet"
    changed_dataset.write_bytes(b"changed")
    monkeypatch.setattr(main, "DATA_PATH", changed_dataset)
    ready, reason = main._model_readiness()
    assert ready is False
    assert "hash" in reason.lower()
